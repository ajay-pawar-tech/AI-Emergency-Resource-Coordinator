
from unittest.mock import MagicMock, patch

from app.optimization import route_optimizer


def test_calculate_route_missing_api_key():
    with patch.object(route_optimizer, "GEOAPIFY_API_KEY", None):
        result = route_optimizer.calculate_route(17.44, 78.37, 17.38, 78.48)

    assert result is None


@patch("app.optimization.route_optimizer.requests.get")
def test_calculate_route_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "features": [
            {
                "properties": {
                    "distance": 5000,
                    "time": 600,
                }
            }
        ]
    }
    mock_get.return_value = mock_response

    with patch.object(route_optimizer, "GEOAPIFY_API_KEY", "fake-test-key"):
        result = route_optimizer.calculate_route(17.44, 78.37, 17.38, 78.48)

    assert result == {
        "distance_km": 5.0,
        "time_minutes": 10.0,
    }
    mock_get.assert_called_once()

    args, kwargs = mock_get.call_args
    assert args[0] == "https://api.geoapify.com/v1/routing"
    assert kwargs["timeout"] == 10
    assert kwargs["params"]["mode"] == "drive"
    assert kwargs["params"]["apiKey"] == "fake-test-key"


@patch("app.optimization.route_optimizer.requests.get")
def test_calculate_route_api_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_get.return_value = mock_response

    with patch.object(route_optimizer, "GEOAPIFY_API_KEY", "fake-test-key"):
        result = route_optimizer.calculate_route(17.44, 78.37, 17.38, 78.48)

    assert result is None


@patch("app.optimization.route_optimizer.requests.get")
def test_calculate_route_no_features(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"features": []}
    mock_get.return_value = mock_response

    with patch.object(route_optimizer, "GEOAPIFY_API_KEY", "fake-test-key"):
        result = route_optimizer.calculate_route(17.44, 78.37, 17.38, 78.48)

    assert result is None


@patch("app.optimization.route_optimizer.requests.get")
def test_calculate_route_missing_properties(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "features": [{}]
    }
    mock_get.return_value = mock_response

    with patch.object(route_optimizer, "GEOAPIFY_API_KEY", "fake-test-key"):
        result = route_optimizer.calculate_route(17.44, 78.37, 17.38, 78.48)

    assert result == {
        "distance_km": 0.0,
        "time_minutes": 0.0,
    }
