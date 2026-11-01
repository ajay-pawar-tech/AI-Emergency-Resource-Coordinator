
from unittest.mock import patch

from app.agents.route_agent import get_emergency_route


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_route(mock_calculate_route):
    expected_route = {
        "distance_km": 12.5,
        "time_minutes": 24.0,
    }
    mock_calculate_route.return_value = expected_route

    result = get_emergency_route(17.44, 78.37, 17.38, 78.48)

    assert result == expected_route


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_none_when_unavailable(
    mock_calculate_route,
):
    mock_calculate_route.return_value = None

    result = get_emergency_route(17.44, 78.37, 17.38, 78.48)

    assert result is None


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_passes_correct_coordinates(
    mock_calculate_route,
):
    mock_calculate_route.return_value = {"distance_km": 5.0}

    get_emergency_route(10.1, 20.2, 30.3, 40.4)

    mock_calculate_route.assert_called_once_with(
        ambulance_latitude=10.1,
        ambulance_longitude=20.2,
        emergency_latitude=30.3,
        emergency_longitude=40.4,
    )


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_route_without_modification(
    mock_calculate_route,
):
    expected_route = {
        "distance_km": 8.75,
        "time_minutes": 16.5,
        "geometry": {"type": "LineString", "coordinates": []},
    }
    mock_calculate_route.return_value = expected_route

    result = get_emergency_route(1.0, 2.0, 3.0, 4.0)

    assert result is expected_route
