"""Maakt de zijkanten (ruggen) van de bordspeldozen voor /bordspellen/.

Per spel staat in src/data/bgg_spines.json waar het logo op de cover staat, als fracties
[links, boven, rechts, onder]. Staat een logo op meerdere regels, gebruik dan een lijst van
vakken in leesvolgorde; die worden naast elkaar op één regel gezet, zoals op een echte doosrug.
Op een effen achtergrond herkent het script regels ook zelf; zet "regels_splitsen": false om dat
voor een spel uit te zetten.

Het script knipt het logo uit de cover. Is de achtergrond rond het logo effen, dan wordt die
transparant en wordt strak op de letters bijgesneden; anders loopt de rand zacht over in de
achtergrondkleur. Met de doosmaten uit bgg_dimensions.json kiest het script de opmaak met de
grootste letters op de rug: op één regel of gestapeld, gedraaid of rechtop. Het resultaat komt in
src/assets/bordspellen/logos/, de achtergrondkleur (de kleur van de rug) in bgg_spines.json.

Nieuwe spellen zonder logovak krijgen de bovenste strook van de cover en de vlag
"controleren"; pas het vak aan, haal de vlag weg en draai het script opnieuw.

Gebruik: python scripts/make_spines.py   (vereist Pillow en numpy)
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
COLLECTION_FILE = PROJECT_ROOT / "src" / "data" / "bgg_collection.json"
SPINES_FILE = PROJECT_ROOT / "src" / "data" / "bgg_spines.json"
DIMENSIONS_FILE = PROJECT_ROOT / "src" / "data" / "bgg_dimensions.json"
COVER_DIR = PROJECT_ROOT / "src" / "assets" / "bordspellen"
LOGO_DIR = COVER_DIR / "logos"

DEFAULT_LOGO = [0.05, 0.03, 0.95, 0.3]
LONG_SIDE = 480  # pixels langs de lengte van de rug
FEATHER = 0.08  # deel van de korte zijde dat zacht overloopt in de achtergrond
CLEAN_SHARE = 0.6  # zoveel van de rand moet op de achtergrondkleur lijken om die weg te halen
BG_DISTANCE = (22, 62)  # kleurafstand tot de achtergrond: daaronder transparant, daarboven dekkend


def find_cover(game_id):
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = COVER_DIR / f"{game_id}.{ext}"
        if path.exists():
            return path
    return None


def border_pixels(pixels):
    h, w, _ = pixels.shape
    ring = max(2, round(min(w, h) * 0.06))
    return np.concatenate([pixels[:ring].reshape(-1, 3), pixels[-ring:].reshape(-1, 3), pixels[:, :ring].reshape(-1, 3), pixels[:, -ring:].reshape(-1, 3)])


def feather_mask(size):
    w, h = size
    edge = max(2, round(min(w, h) * FEATHER))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle([edge, edge, w - edge - 1, h - edge - 1], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(edge / 2))


def trim(logo, alpha):
    """Snijdt bij tot op de letters, met een kleine marge."""
    ys, xs = np.nonzero(alpha > 0.35)
    if not len(xs):
        return logo
    margin = max(2, round(min(logo.size) * 0.04))
    return logo.crop((max(0, xs.min() - margin), max(0, ys.min() - margin), min(logo.width, xs.max() + margin + 1), min(logo.height, ys.max() + margin + 1)))


def split_lines(logo):
    """Knipt een logo op meerdere regels op in losse regels, op de lege rijen ertussen."""
    alpha = np.asarray(logo, dtype=float)[:, :, 3] / 255
    h, w = alpha.shape
    filled = (alpha > 0.35).sum(axis=1) > max(1, w * 0.004)
    runs, start = [], None
    for y, row in enumerate(list(filled) + [False]):
        if row and start is None:
            start = y
        elif not row and start is not None:
            runs.append([start, y])
            start = None
    # Kleine onderbrekingen (binnen één letterregel) tellen niet als nieuwe regel.
    merged = []
    for run in runs:
        if merged and run[0] - merged[-1][1] < h * 0.03:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    ink = (alpha > 0.35).sum()
    # Losse vlekjes (stof, versiering) zijn geen regel.
    lines = [run for run in merged if run[1] - run[0] >= h * 0.05 and (alpha[run[0]:run[1]] > 0.35).sum() >= ink * 0.04]
    if len(lines) < 2:
        return [logo]
    return [trim(band, alpha[top:bottom]) for top, bottom in lines for band in [logo.crop((0, top, w, bottom))]]


def extract(crop, split=True):
    """Geeft de logodelen als RGBA-afbeeldingen en de achtergrondkleur (RGB) erachter."""
    pixels = np.asarray(crop, dtype=float)
    border = border_pixels(pixels)
    background = np.median(border, axis=0)
    clean = (np.linalg.norm(border - background, axis=1) < BG_DISTANCE[0] * 1.8).mean() >= CLEAN_SHARE
    if not clean:
        logo = crop.convert("RGBA")
        logo.putalpha(feather_mask(crop.size))
        return [logo], background
    low, high = BG_DISTANCE
    alpha = np.clip((np.linalg.norm(pixels - background, axis=2) - low) / (high - low), 0, 1)
    logo = trim(Image.fromarray(np.dstack([pixels, alpha * 255]).astype(np.uint8), "RGBA"), alpha)
    return (split_lines(logo) if split else [logo]), background


def join_side_by_side(parts):
    """Zet logodelen (van verschillende regels) naast elkaar, verticaal gecentreerd, op hun eigen schaal."""
    if len(parts) == 1:
        return parts[0]
    height = max(part.height for part in parts)
    gap = round(height * 0.18)
    canvas = Image.new("RGBA", (sum(part.width for part in parts) + gap * (len(parts) - 1), height), (0, 0, 0, 0))
    x = 0
    for part in parts:
        canvas.alpha_composite(part, (x, (height - part.height) // 2))
        x += part.width + gap
    return canvas


def stack(parts):
    """Zet logodelen onder elkaar, horizontaal gecentreerd: de opmaak zoals op de cover."""
    if len(parts) == 1:
        return parts[0]
    width = max(part.width for part in parts)
    gap = round(max(part.height for part in parts) * 0.08)
    canvas = Image.new("RGBA", (width, sum(part.height for part in parts) + gap * (len(parts) - 1)), (0, 0, 0, 0))
    y = 0
    for part in parts:
        canvas.alpha_composite(part, ((width - part.width) // 2, y))
        y += part.height + gap
    return canvas


def best_layout(parts, spine):
    """Kiest de opmaak (op één regel of gestapeld, gedraaid of rechtop) met de grootste letters op deze rug."""
    height_cm, depth_cm = spine
    # Ruimte binnen de rug zoals bordspellen.astro die laat: 9% opzij, een smalle rand boven en onder.
    inner_w, inner_h = depth_cm * 0.82, height_cm * 0.9
    options = []
    for layout in {id(p): p for p in (join_side_by_side(parts), stack(parts))}.values():
        for rotated in (True, False):
            w, h = (layout.height, layout.width) if rotated else layout.size
            # Een opmaak op één regel, gedraaid, leest als een echte rug; die krijgt een kleine voorsprong.
            bonus = 1.12 if rotated and layout.width >= layout.height else 1
            options.append((min(inner_w / w, inner_h / h) * bonus, rotated, layout))
    _, rotated, layout = max(options, key=lambda option: option[0])
    return layout.transpose(Image.Transpose.ROTATE_270) if rotated else layout  # gedraaid leest van boven naar beneden


def make_spine(cover_path, boxes, out_path, spine, split=True):
    cover = Image.open(cover_path).convert("RGB")
    w, h = cover.size
    if boxes and not isinstance(boxes[0], list):
        boxes = [boxes]
    parts, backgrounds = [], []
    for left, top, right, bottom in boxes:
        logos, background = extract(cover.crop((round(left * w), round(top * h), round(right * w), round(bottom * h))), split)
        parts.extend(logos)
        backgrounds.append(background)
    logo = best_layout(parts, spine)
    scale = LONG_SIDE / max(logo.size)
    if scale < 1:
        logo = logo.resize((round(logo.width * scale), round(logo.height * scale)), Image.Resampling.LANCZOS)
    logo.save(out_path, "WEBP", quality=90)
    color = np.mean(backgrounds, axis=0)
    return "#{:02x}{:02x}{:02x}".format(*(round(c) for c in color))


def spine_size(game, cover_path, dimensions):
    """(hoogte, dikte) van de rug in cm; dezelfde berekening als boxShape in src/pages/bordspellen.astro."""
    with Image.open(cover_path) as cover:
        ratio = cover.height / cover.width
    known = dimensions.get(game["id"])
    if known:
        long, short = max(known["width"], known["length"]), min(known["width"], known["length"])
        return (short if ratio < 0.95 else long), min(known["depth"], short)
    weight = game.get("weight") or 0
    if "Card Game" in (game.get("categories") or []) and weight < 2.2:
        face, depth = 18, 5
    elif weight >= 3:
        face, depth = 30, 9
    elif weight >= 2.2:
        face, depth = 28, 8
    else:
        face, depth = 25, 6.5
    return round(face * max(1, ratio)), depth


def main():
    games = [g for g in json.loads(COLLECTION_FILE.read_text(encoding="utf-8"))["games"] if not g.get("is_expansion")]
    spines = json.loads(SPINES_FILE.read_text(encoding="utf-8")) if SPINES_FILE.exists() else {}
    dimensions = json.loads(DIMENSIONS_FILE.read_text(encoding="utf-8")) if DIMENSIONS_FILE.exists() else {}
    LOGO_DIR.mkdir(parents=True, exist_ok=True)

    made = missing = 0
    for game in sorted(games, key=lambda g: g["name"].lower()):
        cover = find_cover(game["id"])
        if not cover:
            missing += 1
            continue
        # "controleren" blijft staan tot iemand het logovak heeft nagekeken en de vlag weghaalt.
        entry = spines.setdefault(game["id"], {"name": game["name"], "logo": DEFAULT_LOGO, "controleren": True})
        entry["color"] = make_spine(cover, entry["logo"], LOGO_DIR / f"{game['id']}.webp", spine_size(game, cover, dimensions), entry.get("regels_splitsen", True))
        made += 1

    # Compact wegschrijven: één regel per spel.
    lines = [f"\t{json.dumps(key)}: {json.dumps(value, ensure_ascii=False)}" for key, value in sorted(spines.items(), key=lambda item: item[1]["name"].lower())]
    SPINES_FILE.write_text("{\n" + ",\n".join(lines) + "\n}\n", encoding="utf-8")
    print(f"{made} zijkanten gemaakt, {missing} spellen zonder cover overgeslagen.")
    unchecked = [entry["name"] for entry in spines.values() if entry.get("controleren")]
    if unchecked:
        print(f"Logovak nog nakijken in bgg_spines.json: {', '.join(unchecked)}")


if __name__ == "__main__":
    main()
