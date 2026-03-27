import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

# Haal token en gebruikersnaam uit omgevingsvariabelen
# Deze worden ingesteld door GitHub Actions via Secrets
DISC_TOKEN = os.environ.get("DISCOGS_TOKEN")
DISC_USERNAME = os.environ.get("DISCOGS_USERNAME")

# Controleer of de variabelen zijn ingesteld
if not DISC_TOKEN or not DISC_USERNAME:
    raise Exception("DISCOGS_TOKEN en/of DISCOGS_USERNAME omgevingsvariabelen zijn niet ingesteld!")

# Basis API-URL
BASE_URL = f"https://api.discogs.com/users/{DISC_USERNAME}/collection/folders/0/releases"
PER_PAGE = 100

# Alle pagina's ophalen
releases = []
page = 1
while True:
    params = {"token": DISC_TOKEN, "page": page, "per_page": PER_PAGE}
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fout bij ophalen Discogs-data: {e}")

    data = response.json()
    releases.extend(data.get("releases", []))

    pagination = data.get("pagination", {})
    if not pagination or pagination.get("page") >= pagination.get("pages", 1):
        break
    page += 1

# Zorg dat de output map bestaat (src/data)
output_dir = "/var/www/vhosts/daandobber.nl/httpdocs/src/data"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "cd_collection.json")

# Sla de data op in een JSON-bestand
try:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"releases": releases}, f, indent=2, ensure_ascii=False)
    print(f"Discogs-data succesvol opgeslagen in {output_path}.")
except IOError as e:
    raise Exception(f"Fout bij schrijven naar {output_path}: {e}")