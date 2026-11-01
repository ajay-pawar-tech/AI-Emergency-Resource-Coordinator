
import requests
from app.services import weather_service


def test_get_weather_returns_error_when_api_key_missing(monkeypatch):
    monkeypatch.setattr(weather_service, "WEATHER_API_KEY", None)

    result = weather_service.get_weather("Hyderabad")

    assert result["success"] is False
    assert "WEATHER_API_KEY" in result["error"]


def test_get_weather_returns_weather_data_on_success(monkeypatch):
    monkeypatch.setattr(weather_service, "WEATHER_API_KEY", "test-key")

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "name": "Hyderabad",
                "main": {"temp": 30.5, "humidity": 60},
                "weather": [{"description": "clear sky"}],
                "wind": {"speed": 3.2}
            }

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(weather_service.requests, "get", fake_get)

    result = weather_service.get_weather("Hyderabad")

    assert result == {
        "success": True,
        "city": "Hyderabad",
        "temperature": 30.5,
        "humidity": 60,
        "weather": "clear sky",
        "wind_speed": 3.2
    }


def test_get_weather_returns_api_error(monkeypatch):
    monkeypatch.setattr(weather_service, "WEATHER_API_KEY", "test-key")

    class FakeResponse:
        status_code = 401
        text = "Invalid API key"

    monkeypatch.setattr(
        weather_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse()
    )

    result = weather_service.get_weather("Hyderabad")

    assert result["success"] is False
    assert result["error"] == "Invalid API key"


def test_get_weather_handles_network_error(monkeypatch):
    monkeypatch.setattr(weather_service, "WEATHER_API_KEY", "test-key")

    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("Network unavailable")

    monkeypatch.setattr(weather_service.requests, "get", fake_get)

    result = weather_service.get_weather("Hyderabad")

    assert result["success"] is False
    assert "Network unavailable" in result["error"]

from app.services import maps_service


def test_test_geoapify_handles_missing_api_key(monkeypatch, capsys):
    monkeypatch.setattr(maps_service, "GEOAPIFY_API_KEY", None)

    maps_service.test_geoapify()

    output = capsys.readouterr().out
    assert "GEOAPIFY_API_KEY is missing" in output


def test_test_geoapify_prints_location_on_success(monkeypatch, capsys):
    monkeypatch.setattr(maps_service, "GEOAPIFY_API_KEY", "test-key")

    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "results": [{
                    "formatted": "Ameerpet, Hyderabad",
                    "lat": 17.4375,
                    "lon": 78.4483
                }]
            }

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(maps_service.requests, "get", fake_get)

    maps_service.test_geoapify()

    output = capsys.readouterr().out
    assert "Status Code: 200" in output
    assert "Ameerpet, Hyderabad" in output
    assert "17.4375" in output
    assert "78.4483" in output


def test_test_geoapify_handles_no_location(monkeypatch, capsys):
    monkeypatch.setattr(maps_service, "GEOAPIFY_API_KEY", "test-key")

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"results": []}

    monkeypatch.setattr(
        maps_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse()
    )

    maps_service.test_geoapify()

    output = capsys.readouterr().out
    assert "No location found." in output


def test_test_geoapify_handles_api_error(monkeypatch, capsys):
    monkeypatch.setattr(maps_service, "GEOAPIFY_API_KEY", "test-key")

    class FakeResponse:
        status_code = 401
        text = "Invalid API key"

    monkeypatch.setattr(
        maps_service.requests,
        "get",
        lambda *args, **kwargs: FakeResponse()
    )

    maps_service.test_geoapify()

    output = capsys.readouterr().out
    assert "API Error:" in output
    assert "Invalid API key" in output
