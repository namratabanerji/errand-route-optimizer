from typing import Dict, List, Tuple
from app.models.location import Location
from app.models.request import TripRequest
from app.api.geocoding import geocode_address
from app.api.places import search_places_nearby
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_candidates(trip_request: TripRequest) -> Tuple[Location, Location, Dict[str, List[Location]]]:
    origin = geocode_address(trip_request.origin)
    destination = geocode_address(trip_request.destination)

    candidates_by_stop = {}
    for stop_name in trip_request.stops:
        candidates = search_places_nearby(
            lat=origin.lat,
            lon=origin.lon,
            query_name=stop_name,
            radius_meters=trip_request.search_radius_meters,
            limit=trip_request.max_candidates_per_stop * 3,
        )

        print(f"\nStop: {stop_name}")
        print(f"Found {len(candidates)} candidates")
        for c in candidates[:5]:
            print(f"  - {c.name} | {c.address}")


        if trip_request.require_opening_hours:
            candidates = [c for c in candidates if c.opening_hours]
            
        candidates.sort(key=lambda loc: haversine(origin.lat, origin.lon, loc.lat, loc.lon))

        candidates = candidates[:trip_request.max_candidates_per_stop]

        if not candidates:
            raise ValueError(
                f"No candidate locations found for stop '{stop_name}'. "
                f"Try increasing the radius or changing the query."
            )

        candidates_by_stop[stop_name] = candidates

    return origin, destination, candidates_by_stop
