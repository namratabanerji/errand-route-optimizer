import requests
from app.config import settings
from app.models.location import Location


def geocode_address(address: str) -> Location:
    url = f"{settings.NOMINATIM_BASE_URL}/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": settings.USER_AGENT
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    results = response.json()

    if not results:
        raise ValueError(f"No geocoding result found for address: {address}")

    result = results[0]
    return Location(
        name=address,
        lat=float(result["lat"]),
        lon=float(result["lon"]),
        address=result.get("display_name")
    )
