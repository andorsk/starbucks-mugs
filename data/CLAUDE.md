# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Starbucks "Been There" mug collection tracker. Scrapes mug data from starbucks-mugs.com, geocodes locations via Google Maps API, generates interactive Folium map (index.html).

## Source of Truth

`owned_mugs.txt` - one mug name per line, format: `Been There – Location`

## Commands

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Full update (backup → scrape → geocode → generate map)
python starbucks-mugs.py update

# Individual commands
python starbucks-mugs.py backup --input data/final_data.json --output data/old_data.json
python starbucks-mugs.py prepare --previous data/final_data.json --output data/final_data.json
python starbucks-mugs.py visualize --input data/final_data.json --output index.html
```

## Environment

| Variable | Purpose |
|----------|---------|
| `GOOGLE_MAPS_API_KEY` | Required for geocoding new locations |

## Data Files

- `final_data.json` - main mug database (location, latlong, ownership, image URLs)
- `latlong_overrides.json` - manual coordinate overrides for fictional/ambiguous locations (set to `null` to skip)
- `old_data.json` / `final_data.json.bak` - backups

## Architecture

Single script (`starbucks-mugs.py`) handles:
1. **Scraping**: fetches all "Been There" mugs from starbucks-mugs.com (36 pages)
2. **Geocoding**: resolves location names → lat/long via Google Maps API (1s rate limit)
3. **Visualization**: generates Folium map with green (owned) / orange (not owned) markers

CI runs daily via GitHub Actions, deploying to GitHub Pages.

## Adding Mugs

1. Add line to `data/owned_mugs.txt` matching exact mug title
2. Run `python starbucks-mugs.py update` (or push to trigger CI)
3. For locations that fail geocoding, add override to `latlong_overrides.json`
