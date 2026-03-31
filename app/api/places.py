import math
import requests
from typing import List
from app.models.location import Location
from app.config import settings


def _bounding_box(lat: float, lon: float, radius_meters: int) -> tuple[float, float, float, float]:
    lat_delta = radius_meters / 111_320.0
    lon_delta = radius_meters / (111_320.0 * max(math.cos(math.radians(lat)), 1e-6))
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta
    return min_lat, min_lon, max_lat, max_lon


def search_places_nearby(
    lat: float,
    lon: float,
    query_name: str,
    radius_meters: int = 8000,
    limit: int = 10,
) -> List[Location]:
    min_lat, min_lon, max_lat, max_lon = _bounding_box(lat, lon, radius_meters)

    url = f"{settings.NOMINATIM_BASE_URL}/search"
    params = {
        "q": query_name,
        "format": "jsonv2",
        "limit": limit,
        "bounded": 1,
        "viewbox": f"{min_lon},{max_lat},{max_lon},{min_lat}",
        "addressdetails": 1,
    }

    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": settings.USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    locations = []
    seen = set()

    for item in data:
        item_lat = float(item["lat"])
        item_lon = float(item["lon"])
        name = item.get("name") or item.get("display_name", query_name).split(",")[0].strip()

        key = (round(item_lat, 6), round(item_lon, 6), name)
        if key in seen:
            continue
        seen.add(key)

        address = item.get("display_name")
        category = query_name

        locations.append(
            Location(
                name=name,
                lat=item_lat,
                lon=item_lon,
                address=address,
                category=category,
                opening_hours=None,
            )
        )

    return locations
