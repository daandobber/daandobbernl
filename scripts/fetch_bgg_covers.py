"""Downloadt de covers van de bordspellen voor /bordspellen/.

Voor elk basisspel in src/data/bgg_collection.json zonder cover in src/assets/bordspellen/
wordt de BGG-afbeelding gedownload, verkleind tot maximaal 400 px en als <bgg-id>.jpg opgeslagen.
Bestaande covers blijven staan.

Gebruik: python scripts/fetch_bgg_covers.py   (vereist requests en Pillow)
"""

import io
import json
import time
from pathlib import Path

import requests
from PIL import Image

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
COLLECTION_FILE = PROJECT_ROOT / "src" / "data" / "bgg_collection.json"
COVER_DIR = PROJECT_ROOT / "src" / "assets" / "bordspellen"

MAX_SIZE = 400
SLEEP_BETWEEN_DOWNLOADS = 1


def has_cover(game_id):
    return any((COVER_DIR / f"{game_id}.{ext}").exists() for ext in ("jpg", "jpeg", "png", "webp"))


def main():
    games = [g for g in json.loads(COLLECTION_FILE.read_text(encoding="utf-8"))["games"] if not g.get("is_expansion")]
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": "daandobber.nl bordspellenkast"})

    added, failed = [], []
    for game in sorted(games, key=lambda g: g["name"].lower()):
        if has_cover(game["id"]):
            continue
        url = game.get("image") or game.get("thumbnail")
        if not url:
            failed.append(game["name"])
            continue
        try:
            response = session.get(url, timeout=60)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            image.thumbnail((MAX_SIZE, MAX_SIZE), Image.Resampling.LANCZOS)
            image.save(COVER_DIR / f"{game['id']}.jpg", "JPEG", quality=86, optimize=True)
            added.append(game["name"])
        except (requests.RequestException, OSError) as error:
            print(f"  Mislukt voor {game['name']}: {error}")
            failed.append(game["name"])
        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    print(f"{len(added)} covers toegevoegd.")
    if added:
        print("  " + ", ".join(added))
    if failed:
        print(f"Geen cover voor: {', '.join(failed)}")


if __name__ == "__main__":
    main()
