# daandobber.nl

Website van Daan Dobber

## Automatische Deployment

Deze repository is gekoppeld aan de live site via GitHub Actions. Elke keer dat je pusht naar de `master` branch worden de wijzigingen automatisch naar de VPS gedeployed.

### Workflow
1. Maak wijzigingen lokaal of via GitHub
2. Commit en push naar `master`
3. GitHub Actions deployt automatisch naar de VPS via FTP

### Handmatig deployen
Je kunt ook handmatig een deployment triggeren via de [Actions tab](https://github.com/daandobber/daandobbernl/actions) door "Deploy to VPS" te selecteren en "Run workflow" te klikken.

## Structuur
- `dist/` - Gebouwde Astro site
- `.github/workflows/` - GitHub Actions deployment workflow
- `astro.config.ts` - Astro configuratie
- `biome.json` - Code formatter configuratie
