"""Werkt de bordspellenkast (/bordspellen/) in één keer bij.

1. collectie ophalen bij BGG          (fetch_bgg_collection.py)
2. ontbrekende covers downloaden      (fetch_bgg_covers.py)
3. doosmaten ophalen                  (fetch_bgg_dimensions.py)
4. zijkanten maken                    (make_spines.py)

Nieuwe spellen krijgen op de zijkant eerst de bovenste strook van de cover. Staat het logo
ergens anders, pas dan het logovak aan in src/data/bgg_spines.json en draai make_spines.py opnieuw.

Gebruik: python scripts/update_bordspellen.py   (vereist requests, python-dotenv, Pillow en numpy)
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STEPS = ["fetch_bgg_collection.py", "fetch_bgg_covers.py", "fetch_bgg_dimensions.py", "make_spines.py"]


def main():
    for step in STEPS:
        print(f"\n=== {step} ===", flush=True)
        if subprocess.run([sys.executable, str(SCRIPT_DIR / step)]).returncode != 0:
            sys.exit(f"Gestopt: {step} is mislukt.")
    print("\nBordspellenkast bijgewerkt.")


if __name__ == "__main__":
    main()
