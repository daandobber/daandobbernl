"""Haalt de echte doosmaten van de bordspellen op bij BoardGameGeek voor /bordspellen/.

BGG bewaart maten per editie (in inches). Per spel kiest dit script:
1. de editie die in de BGG-collectie als 'eigen versie' staat;
2. anders de doosmaat die bij de meeste edities voorkomt (bij gelijke stand de Nederlandse,
   dan de Engelse editie). Zo vallen zeldzame luxe- of afwijkende edities weg.
Het resultaat (in cm) komt in src/data/bgg_dimensions.json.

Maten die bij BGG fout staan of ontbreken kun je in cm vastleggen in
src/data/bgg_dimensions_handmatig.json: {"<bgg-id>": {"width": .., "length": .., "depth": .., "note": ".."}}.

Vereist BGG_API_TOKEN (en voor stap 1 BGG_USERNAME) in scripts/.env.
Gebruik: python scripts/fetch_bgg_dimensions.py
"""

import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
COLLECTION_FILE = PROJECT_ROOT / "src" / "data" / "bgg_collection.json"
OUTPUT_FILE = PROJECT_ROOT / "src" / "data" / "bgg_dimensions.json"
# Handmatige maten in cm (zelf gemeten of een BGG-fout gecorrigeerd); deze gaan altijd voor.
MANUAL_FILE = PROJECT_ROOT / "src" / "data" / "bgg_dimensions_handmatig.json"

load_dotenv()
BGG_API_TOKEN = os.environ.get("BGG_API_TOKEN")
BGG_USERNAME = os.environ.get("BGG_USERNAME")

API_BASE_URL = "https://boardgamegeek.com/xmlapi2"
BATCH_SIZE = 20  # BGG staat maximaal 20 ids per thing-verzoek toe
SLEEP_BETWEEN_REQUESTS = 5
INCH = 2.54


def get(session, endpoint, params):
    """GET met nette pauzes; BGG antwoordt 202 zolang een collectie nog wordt klaargezet."""
    for attempt in range(8):
        response = session.get(f"{API_BASE_URL}/{endpoint}", params=params, timeout=60)
        if response.status_code == 200:
            return ET.fromstring(response.content)
        if response.status_code not in (202, 429, 500, 502, 503):
            response.raise_for_status()
        time.sleep(SLEEP_BETWEEN_REQUESTS * (attempt + 1))
    raise RuntimeError(f"BGG gaf geen antwoord op {endpoint} na meerdere pogingen")


def dimensions(version):
    """(breedte, lengte, diepte) in inches, of None als niet alle drie bekend zijn."""
    values = []
    for key in ("width", "length", "depth"):
        node = version.find(key)
        try:
            value = float(node.get("value")) if node is not None else 0
        except (TypeError, ValueError):
            value = 0
        values.append(value)
    return tuple(values) if all(0 < v < 40 for v in values) else None


def version_info(version):
    name = version.find("name")
    return {
        "id": version.get("id"),
        "name": name.get("value", "") if name is not None else "",
        "languages": [link.get("value", "") for link in version.findall("link[@type='language']")],
        "dims": dimensions(version),
    }


def owned_versions(session):
    if not BGG_USERNAME:
        print("BGG_USERNAME ontbreekt; eigen edities worden overgeslagen.")
        return {}
    root = get(session, "collection", {"username": BGG_USERNAME, "own": 1, "version": 1, "excludesubtype": "boardgameexpansion"})
    owned = {}
    for item in root.findall("item"):
        version = item.find("version/item")
        if version is not None:
            owned[item.get("objectid")] = version_info(version)
    return owned


def size_key(version):
    # Afgerond op hele cm, zodat kleine meetverschillen tussen edities als dezelfde doos tellen.
    return tuple(sorted(round(v * INCH) for v in version["dims"][:2])) + (round(version["dims"][2] * INCH),)


def choose(versions, owned):
    if owned and owned["dims"]:
        return owned, "eigen editie"
    complete = [version for version in versions if version["dims"]]
    if not complete:
        return None, ""
    counts = Counter(size_key(version) for version in complete)
    top = max(counts.values())
    candidates = [version for version in complete if counts[size_key(version)] == top]
    for language, label in (("Dutch", "meest voorkomende maat (Nederlandse editie)"), ("English", "meest voorkomende maat (Engelse editie)")):
        matching = [version for version in candidates if language in version["languages"]]
        if matching:
            return matching[0], label
    return candidates[0], "meest voorkomende maat"


def main():
    if not BGG_API_TOKEN:
        sys.exit("Fout: BGG_API_TOKEN ontbreekt in .env")

    games = [g for g in json.loads(COLLECTION_FILE.read_text(encoding="utf-8"))["games"] if not g.get("is_expansion")]
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {BGG_API_TOKEN}", "User-Agent": "daandobber.nl bordspellenkast"})

    owned = owned_versions(session)
    ids = [game["id"] for game in games]
    versions = {}
    for start in range(0, len(ids), BATCH_SIZE):
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        root = get(session, "thing", {"id": ",".join(ids[start:start + BATCH_SIZE]), "versions": 1})
        for item in root.findall("item"):
            versions[item.get("id")] = [version_info(version) for version in item.findall("versions/item")]
        print(f"  {min(start + BATCH_SIZE, len(ids))}/{len(ids)} spellen opgehaald")

    manual = json.loads(MANUAL_FILE.read_text(encoding="utf-8")) if MANUAL_FILE.exists() else {}
    result, missing = {}, []
    for game in sorted(games, key=lambda g: g["name"].lower()):
        if game["id"] in manual:
            fixed = manual[game["id"]]
            result[game["id"]] = {"name": game["name"], "width": fixed["width"], "length": fixed["length"], "depth": fixed["depth"], "edition": fixed.get("note", ""), "source": "handmatig"}
            continue
        version, source = choose(versions.get(game["id"], []), owned.get(game["id"]))
        if not version:
            missing.append(game["name"])
            continue
        width, length, depth = (round(value * INCH, 1) for value in version["dims"])
        result[game["id"]] = {"name": game["name"], "width": width, "length": length, "depth": depth, "edition": version["name"], "source": source}

    lines = [f"\t{json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}" for key, value in result.items()]
    OUTPUT_FILE.write_text("{\n" + ",\n".join(lines) + "\n}\n", encoding="utf-8")
    print(f"{len(result)} spellen met maten opgeslagen in {OUTPUT_FILE.name}.")
    if missing:
        print(f"Geen maten bekend bij BGG voor: {', '.join(missing)}")


if __name__ == "__main__":
    main()
