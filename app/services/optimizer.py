import itertools
from math import prod
from typing import Dict, List, Tuple
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from app.models.location import Location
from app.models.solution import RouteStop, TripSolution


def compute_route_cost(
    route_indices: List[int],
    distance_matrix: List[List[float]],
    duration_matrix: List[List[float]],
) -> Tuple[float, float]:
    total_distance = 0.0
    total_duration = 0.0

    for i in range(len(route_indices) - 1):
        a = route_indices[i]
        b = route_indices[i + 1]
        total_distance += distance_matrix[a][b]
        total_duration += duration_matrix[a][b]

    return total_distance, total_duration


def solve_tsp_order_for_selected_locations(
    selected_global_indices: List[int],
    distance_matrix: List[List[float]],
    duration_matrix: List[List[float]],
) -> List[int]:
    n = len(selected_global_indices)

    local_duration_matrix = [
        [int(duration_matrix[i][j]) for j in selected_global_indices]
        for i in selected_global_indices
    ]

    manager = pywrapcp.RoutingIndexManager(n, 1, [0], [n - 1])
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return local_duration_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = 3

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        raise RuntimeError("OR-Tools could not find a valid route ordering.")

    ordered_local_nodes = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        ordered_local_nodes.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    ordered_local_nodes.append(manager.IndexToNode(index))

    ordered_global_indices = [selected_global_indices[local_idx] for local_idx in ordered_local_nodes]
    return ordered_global_indices


def solve_with_ortools_exhaustive(
    origin: Location,
    destination: Location,
    candidates_by_stop: Dict[str, List[Location]],
    distance_matrix: List[List[float]],
    duration_matrix: List[List[float]],
    flattened_locations: List[Location],
) -> TripSolution:
    categories = list(candidates_by_stop.keys())
    candidate_lists = [candidates_by_stop[cat] for cat in categories]

    total_combinations = prod(len(lst) for lst in candidate_lists)
    combinations_evaluated = 0

    print(f"\n[Exhaustive] Total candidate combinations: {total_combinations}")

    best = None
    origin_index = 0
    destination_index = len(flattened_locations) - 1

    for chosen_locations in itertools.product(*candidate_lists):
        combinations_evaluated += 1

        chosen_indices = [flattened_locations.index(loc) for loc in chosen_locations]
        selected_global_indices = [origin_index] + chosen_indices + [destination_index]

        ordered_global_indices = solve_tsp_order_for_selected_locations(
            selected_global_indices=selected_global_indices,
            distance_matrix=distance_matrix,
            duration_matrix=duration_matrix,
        )

        total_distance, total_duration = compute_route_cost(
            ordered_global_indices,
            distance_matrix,
            duration_matrix,
        )

        if best is None or total_duration < best["total_duration"]:
            best = {
                "ordered_global_indices": ordered_global_indices,
                "total_distance": total_distance,
                "total_duration": total_duration,
                "selected": {
                    categories[i]: chosen_locations[i].name
                    for i in range(len(categories))
                },
            }

    if best is None:
        raise RuntimeError("No feasible solution found.")

    ordered_stops = [
        RouteStop(order=i, location=flattened_locations[global_idx])
        for i, global_idx in enumerate(best["ordered_global_indices"])
    ]

    return TripSolution(
        ordered_stops=ordered_stops,
        total_distance_meters=best["total_distance"],
        total_duration_seconds=best["total_duration"],
        selected_locations_by_category=best["selected"],
        solver_name="exhaustive",
        combinations_evaluated=combinations_evaluated,
        beam_states_explored=None,
        beam_width_used=None,
    )


def solve_with_beam_search(
    origin: Location,
    destination: Location,
    candidates_by_stop: Dict[str, List[Location]],
    distance_matrix: List[List[float]],
    duration_matrix: List[List[float]],
    flattened_locations: List[Location],
    beam_width: int = 5,
) -> TripSolution:
    categories = list(candidates_by_stop.keys())
    origin_index = 0
    destination_index = len(flattened_locations) - 1

    total_combinations = prod(len(candidates_by_stop[cat]) for cat in categories)
    beam_states_explored = 0

    print(f"\n[Beam] Theoretical full combinations: {total_combinations}")
    print(f"[Beam] Beam width: {beam_width}")

    beam = [
        {
            "chosen_locations": [],
            "selected_by_category": {},
            "ordered_global_indices": [origin_index, destination_index],
            "total_distance": 0.0,
            "total_duration": 0.0,
        }
    ]

    for step_idx, category in enumerate(categories, start=1):
        next_beam = []

        for partial in beam:
            for candidate in candidates_by_stop[category]:
                if candidate in partial["chosen_locations"]:
                    continue

                beam_states_explored += 1

                new_chosen_locations = partial["chosen_locations"] + [candidate]
                chosen_indices = [flattened_locations.index(loc) for loc in new_chosen_locations]
                selected_global_indices = [origin_index] + chosen_indices + [destination_index]

                ordered_global_indices = solve_tsp_order_for_selected_locations(
                    selected_global_indices=selected_global_indices,
                    distance_matrix=distance_matrix,
                    duration_matrix=duration_matrix,
                )

                total_distance, total_duration = compute_route_cost(
                    ordered_global_indices,
                    distance_matrix,
                    duration_matrix,
                )

                new_selected = dict(partial["selected_by_category"])
                new_selected[category] = candidate.name

                next_beam.append(
                    {
                        "chosen_locations": new_chosen_locations,
                        "selected_by_category": new_selected,
                        "ordered_global_indices": ordered_global_indices,
                        "total_distance": total_distance,
                        "total_duration": total_duration,
                    }
                )

        next_beam.sort(key=lambda x: x["total_duration"])
        beam = next_beam[:beam_width]

        print(
            f"[Beam] After category {step_idx}/{len(categories)} "
            f"('{category}'): kept {len(beam)} states, explored {beam_states_explored} total states"
        )

        if not beam:
            raise RuntimeError(f"Beam search failed while expanding category '{category}'.")

    best = min(beam, key=lambda x: x["total_duration"])

    ordered_stops = [
        RouteStop(order=i, location=flattened_locations[global_idx])
        for i, global_idx in enumerate(best["ordered_global_indices"])
    ]

    return TripSolution(
        ordered_stops=ordered_stops,
        total_distance_meters=best["total_distance"],
        total_duration_seconds=best["total_duration"],
        selected_locations_by_category=best["selected_by_category"],
        solver_name="beam_search",
        combinations_evaluated=total_combinations,
        beam_states_explored=beam_states_explored,
        beam_width_used=beam_width,
    )


def solve_with_ortools(
    origin: Location,
    destination: Location,
    candidates_by_stop: Dict[str, List[Location]],
    distance_matrix: List[List[float]],
    duration_matrix: List[List[float]],
    flattened_locations: List[Location],
    beam_width: int = 5,
    use_beam_search: bool = True,
) -> TripSolution:
    if use_beam_search:
        return solve_with_beam_search(
            origin=origin,
            destination=destination,
            candidates_by_stop=candidates_by_stop,
            distance_matrix=distance_matrix,
            duration_matrix=duration_matrix,
            flattened_locations=flattened_locations,
            beam_width=beam_width,
        )

    return solve_with_ortools_exhaustive(
        origin=origin,
        destination=destination,
        candidates_by_stop=candidates_by_stop,
        distance_matrix=distance_matrix,
        duration_matrix=duration_matrix,
        flattened_locations=flattened_locations,
    )
