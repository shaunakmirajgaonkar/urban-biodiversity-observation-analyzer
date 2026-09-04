# 🌿 Urban Biodiversity Observation Analyzer — UrbanBioTrack

A privacy-conscious, local-first Streamlit application for analyzing citizen biodiversity observations, species patterns, habitat conditions, images, and seasonal change.

## Highlights
- Explainable 0–100 biodiversity observation attention score
- Low / Moderate / High / Critical screening bands
- Species, habitat, seasonality and observation analytics
- Local coordinates visualized without external map tiles
- Scenario Lab for transparent what-if exploration
- Data-quality checks and local report export
- Local-only processing with no external APIs required

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 validate_project.py
python3 -m pytest -q
python3 run.py
```

## Optional uploaded data
See `doc/DATA_DICTIONARY.md` for required CSV columns. The app works out of the box with the included sample CSVs.

## Responsible use
Observation counts are influenced by observer effort, accessibility, reporting behavior, detection probability and seasonality. Screening scores are indicators for review and must not be treated as population estimates, ecological-health certification, or biodiversity conservation outcomes without suitable field and scientific validation.
