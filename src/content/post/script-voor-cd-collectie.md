---
title: "Discogs-collectie lokaal opslaan"
description: "Een script dat mijn volledige Discogs CD-verzameling ophaalt via de API en lokaal opslaat als JSON."
publishDate: "20 jul 2025"
tags: ["discogs", "python", "cds"]
---

## CD’s verzamelen (en luisteren)

Sinds 2024 kopen mijn vrouw en ik weer CD’s. 

We registreren onze collectie in de app van [Discogs](https://discogs.com), die handig werkt met barcodes. Maar eerlijk gezegd vind ik mijn eigen [pagina](/cd-collectie/) makkelijker om mee te bladeren dan de app of website van Discogs zelf.

Daarom schreef ik dit script.

Het haalt automatisch onze volledige collectie op via de officiële API en schrijft die naar een lokaal bestand, zodat ik het op mijn eigen manier kan visualiseren of bevragen.

📄 Scriptbestand: `scripts/Workspace_discogs.py`  
📄 Outputbestand: `src/data/cd_collection.json`

```python
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
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
output_dir = os.path.join(project_root, "src", "data")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "cd_collection.json")

# Sla de data op in een JSON-bestand
try:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"releases": releases}, f, indent=2, ensure_ascii=False)
    print(f"Discogs-data succesvol opgeslagen in {output_path}.")
except IOError as e:
    raise Exception(f"Fout bij schrijven naar {output_path}: {e}")
```