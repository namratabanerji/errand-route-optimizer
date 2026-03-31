import requests
from typing import List
from app.models.location import Location
from app.config import settings


def get_distance_matrix(locations: List[Location]) -> dict:
    if not settings.ORS_API_KEY:
        raise ValueError("Missing ORS_API_KEY in environment.")

    url = f"{settings.ORS_BASE_URL}/v2/matrix/driving-car"
    headers = {
        "Authorization": settings.ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "locations": [[loc.lon, loc.lat] for loc in locations],
        "metrics": ["distance", "duration"]
    }

    response = requests.post(url, json=body, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()
