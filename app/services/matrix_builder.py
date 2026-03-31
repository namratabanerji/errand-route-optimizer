from typing import List
from app.models.location import Location
from app.api.routing import get_distance_matrix


def build_matrix(locations: List[Location]) -> dict:
    return get_distance_matrix(locations)
