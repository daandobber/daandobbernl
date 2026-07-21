# daandobber.nl

Website van Daan Dobber

## Automatische Deployment

Deze repository is gekoppeld aan de live site via GitHub Actions. Elke push naar de `master` branch wordt gecontroleerd, gebouwd en naar GitHub Pages gedeployed.

### Workflow
1. Maak wijzigingen lokaal of via GitHub
2. Commit en push naar `master`
3. GitHub Actions controleert en bouwt de site en publiceert `dist/` via GitHub Pages

### Handmatig deployen
Je kunt ook handmatig een deployment triggeren via de [Actions tab](https://github.com/daandobber/daandobbernl/actions) door "Deploy to VPS" te selecteren en "Run workflow" te klikken.

## Structuur
- `dist/` - Lokaal gegenereerde Astro-site (wordt niet in Git opgeslagen)
- `.github/workflows/` - GitHub Actions deployment workflow
- `astro.config.ts` - Astro configuratie
- `biome.json` - Code formatter configuratie
