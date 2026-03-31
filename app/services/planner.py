import time

from app.models.request import TripRequest
from app.services.candidate_generator import generate_candidates
from app.services.matrix_builder import build_matrix
from app.services.optimizer import solve_with_ortools


def plan_trip(trip_request: TripRequest):
    start_time = time.perf_counter()

    origin, destination, candidates_by_stop = generate_candidates(trip_request)

    flattened_locations = [origin]
    for _, candidates in candidates_by_stop.items():
        flattened_locations.extend(candidates)
    flattened_locations.append(destination)

    print("\n--- All Locations ---")
    for i, loc in enumerate(flattened_locations):
        print(i, loc.name, loc.category)

    matrix = build_matrix(flattened_locations)
    distance_matrix = matrix["distances"]
    duration_matrix = matrix["durations"]

    solution = solve_with_ortools(
        origin=origin,
        destination=destination,
        candidates_by_stop=candidates_by_stop,
        distance_matrix=distance_matrix,
        duration_matrix=duration_matrix,
        flattened_locations=flattened_locations,
    )

    end_time = time.perf_counter()
    runtime_seconds = end_time - start_time

    return solution, runtime_seconds
