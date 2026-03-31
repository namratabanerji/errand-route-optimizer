# Errand Route Optimizer

A Python application that selects the best store locations and visit order for multi-stop errands.

## Features
- Geocode origin and destination
- Search candidate business locations
- Build travel time and distance matrix
- Choose the best store branch from each category
- Optimize visit order

## Tech Stack
- Python
- OpenStreetMap / Nominatim
- Overpass API
- OpenRouteService
- OR-Tools (planned)

## Run
```bash
pip install -r requirements.txt
python run.py
