from app.models.request import TripRequest
from app.services.planner import plan_trip


def main():
    trip_request = TripRequest(
        origin="2115 Neil Ave, Columbus, OH 43210",
        destination="2115 Neil Ave, Columbus, OH 43210",
        stops=["Walmart", "Lowe's", "Kroger", "Michaels"],
        max_candidates_per_stop=3,
        require_opening_hours=False,
        search_radius_meters=10000,
        beam_width=4,
    )

    solution, runtime_seconds, route_geojson = plan_trip(trip_request)

    print("\nOptimal Route:")
    for stop in solution.ordered_stops:
        loc = stop.location
        print(f"{stop.order}: {loc.name} ({loc.category})")
        print(f"    {loc.address}")

    print(f"\nSolver: {solution.solver_name}")
    print(f"Total distance: {solution.total_distance_meters:.2f} meters")
    print(f"Total duration: {solution.total_duration_seconds / 60:.2f} minutes")
    print(f"Runtime: {runtime_seconds:.4f} seconds")

    if solution.combinations_evaluated is not None:
        print(f"Candidate combinations (full space): {solution.combinations_evaluated}")

    if solution.beam_states_explored is not None:
        print(f"Beam states explored: {solution.beam_states_explored}")

    if solution.beam_width_used is not None:
        print(f"Beam width used: {solution.beam_width_used}")

    print("\nSelected locations by category:")
    for category, name in solution.selected_locations_by_category.items():
        print(f"{category}: {name}")


if __name__ == "__main__":
    main()
