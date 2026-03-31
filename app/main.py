from app.models.request import TripRequest
from app.services.planner import plan_trip


def main():
    trip_request = TripRequest(
        origin="1460 Worthington St, Columbus, OH 43201",
        destination="2115 Neil Ave, Columbus, OH 43210",
        stops=["Lowe's", "Walmart"],
        max_candidates_per_stop=3,
        require_opening_hours=False,
        search_radius_meters=10000,
    )

    solution, runtime_seconds = plan_trip(trip_request)

    print("\nOptimal Route:")
    for stop in solution.ordered_stops:
        loc = stop.location
        print(f"{stop.order}: {loc.name} ({loc.category})")
        print(f"    {loc.address}")

    print(f"\nTotal distance: {solution.total_distance_meters:.2f} meters")
    print(f"Total duration: {solution.total_duration_seconds / 60:.2f} minutes")
    print(f"Runtime: {runtime_seconds:.4f} seconds")

    print("\nSelected locations by category:")
    for category, name in solution.selected_locations_by_category.items():
        print(f"{category}: {name}")


if __name__ == "__main__":
    main()
