
from unittest.mock import patch

from app.agents import route_agent


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_route_data(mock_calculate_route):
    expected_route = {
        "distance_km": 5.2,
        "time_minutes": 14.0,
    }
    mock_calculate_route.return_value = expected_route

    result = route_agent.get_emergency_route(
        17.44, 78.37, 17.38, 78.48
    )

    assert result == expected_route


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_none_when_route_unavailable(
    mock_calculate_route,
):
    mock_calculate_route.return_value = None

    result = route_agent.get_emergency_route(
        17.44, 78.37, 17.38, 78.48
    )

    assert result is None


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_passes_coordinates_to_optimizer(
    mock_calculate_route,
):
    route_agent.get_emergency_route(
        17.44, 78.37, 17.38, 78.48
    )

    mock_calculate_route.assert_called_once_with(
        ambulance_latitude=17.44,
        ambulance_longitude=78.37,
        emergency_latitude=17.38,
        emergency_longitude=78.48,
    )


@patch("app.agents.route_agent.calculate_route")
def test_get_emergency_route_returns_empty_dictionary(
    mock_calculate_route,
):
    mock_calculate_route.return_value = {}

    result = route_agent.get_emergency_route(
        17.44, 78.37, 17.38, 78.48
    )

    assert result == {}
