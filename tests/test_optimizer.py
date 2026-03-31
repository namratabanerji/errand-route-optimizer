from app.models.location import Location
from app.services.optimizer import compute_route_cost


def test_compute_route_cost():
    matrix_distance = [
        [0, 10, 20],
        [10, 0, 5],
        [20, 5, 0]
    ]
    matrix_duration = [
        [0, 100, 200],
        [100, 0, 50],
        [200, 50, 0]
    ]

    route = [0, 1, 2]
    dist, dur = compute_route_cost(route, matrix_distance, matrix_duration)

    assert dist == 15
    assert dur == 150
