from typing import List, Optional
from pydantic import BaseModel


class TripRequest(BaseModel):
    origin: str
    destination: str
    stops: List[str]
    max_candidates_per_stop: int = 3
    require_opening_hours: bool = False
    search_radius_meters: int = 15000
    departure_time: Optional[str] = None
