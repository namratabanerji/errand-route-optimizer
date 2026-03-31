from typing import Optional
from pydantic import BaseModel


class Location(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    category: Optional[str] = None
    opening_hours: Optional[str] = None
