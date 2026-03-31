from typing import List, Dict
from pydantic import BaseModel
from app.models.location import Location


class RouteStop(BaseModel):
    order: int
    location: Location


class TripSolution(BaseModel):
    ordered_stops: List[RouteStop]
    total_distance_meters: float
    total_duration_seconds: float
    selected_locations_by_category: Dict[str, str]
