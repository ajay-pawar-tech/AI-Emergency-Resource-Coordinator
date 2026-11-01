
from app.agents import route_agent


def test_get_emergency_route_returns_route(monkeypatch):
    expected_route = {
        "distance_km": 12.5,
        "time_minutes": 24.0
    }

    def fake_calculate_route(**kwargs):
        return expected_route

    monkeypatch.setattr(
        route_agent,
        "calculate_route",
        fake_calculate_route
    )

    result = route_agent.get_emergency_route(
        17.441949,
        78.374975,
        17.3850,
        78.4867
    )

    assert result == expected_route


def test_get_emergency_route_returns_none_when_route_unavailable(monkeypatch):
    def fake_calculate_route(**kwargs):
        return None

    monkeypatch.setattr(
        route_agent,
        "calculate_route",
        fake_calculate_route
    )

    result = route_agent.get_emergency_route(
        17.441949,
        78.374975,
        17.3850,
        78.4867
    )

    assert result is None


def test_get_emergency_route_passes_correct_coordinates(monkeypatch):
    expected_route = {"distance_km": 5.0, "time_minutes": 10.0}
    captured_arguments = {}

    def fake_calculate_route(**kwargs):
        captured_arguments.update(kwargs)
        return expected_route

    monkeypatch.setattr(
        route_agent,
        "calculate_route",
        fake_calculate_route
    )

    route_agent.get_emergency_route(
        17.44,
        78.37,
        17.38,
        78.48
    )

    assert captured_arguments == {
        "ambulance_latitude": 17.44,
        "ambulance_longitude": 78.37,
        "emergency_latitude": 17.38,
        "emergency_longitude": 78.48
    }


from unittest.mock import patch

from app.agents import route_agent as agent


def test_get_emergency_route_returns_route():
    expected_route = {
        "distance_km": 5.2,
        "time_minutes": 12.5,
    }

    with patch.object(
        agent,
        "calculate_route",
        return_value=expected_route,
    ) as mock_route:
        result = agent.get_emergency_route(
            17.44, 78.37, 17.38, 78.48
        )

    assert result == expected_route
    mock_route.assert_called_once_with(
        ambulance_latitude=17.44,
        ambulance_longitude=78.37,
        emergency_latitude=17.38,
        emergency_longitude=78.48,
    )


def test_get_emergency_route_returns_none_when_unavailable():
    with patch.object(
        agent, "calculate_route", return_value=None
    ) as mock_route:
        result = agent.get_emergency_route(
            17.44, 78.37, 17.38, 78.48
        )

    assert result is None
    mock_route.assert_called_once()


def test_get_emergency_route_passes_zero_coordinates():
    with patch.object(
        agent, "calculate_route", return_value=None
    ) as mock_route:
        agent.get_emergency_route(0, 0, 0, 0)

    mock_route.assert_called_once_with(
        ambulance_latitude=0,
        ambulance_longitude=0,
        emergency_latitude=0,
        emergency_longitude=0,
    )


def test_get_emergency_route_propagates_calculation_error():
    with patch.object(
        agent,
        "calculate_route",
        side_effect=ValueError("Invalid coordinates"),
    ):
        try:
            agent.get_emergency_route(
                17.44, 78.37, 17.38, 78.48
            )
        except ValueError as error:
            assert str(error) == "Invalid coordinates"
        else:
            raise AssertionError("Expected ValueError")
