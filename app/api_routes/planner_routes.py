from fastapi import APIRouter, HTTPException
from app.models.request import TripRequest
from app.services.planner import plan_trip

router = APIRouter()


@router.post("/plan")
def plan_route(trip_request: TripRequest):
    try:
        solution, runtime_seconds, route_geojson = plan_trip(trip_request)

        return {
            "ordered_stops": [
                {
                    "order": stop.order,
                    "name": stop.location.name,
                    "address": stop.location.address,
                    "category": stop.location.category,
                    "lat": stop.location.lat,
                    "lon": stop.location.lon,
                }
                for stop in solution.ordered_stops
            ],
            "total_distance_meters": solution.total_distance_meters,
            "total_duration_seconds": solution.total_duration_seconds,
            "selected_locations_by_category": solution.selected_locations_by_category,
            "runtime_seconds": runtime_seconds,
            "route_geojson": route_geojson,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
