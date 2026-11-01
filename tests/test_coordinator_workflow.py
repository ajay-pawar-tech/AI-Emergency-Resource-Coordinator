
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.agents import coordinator_agent as coordinator


@pytest.fixture
def incident():
    return SimpleNamespace(
        id=101,
        incident_type="Road Accident",
        severity="High",
        city="Hyderabad",
        location="Ameerpet",
        latitude=17.4375,
        longitude=78.4483,
        victims=2,
        critical_victims=1,
        status="active",
    )


@pytest.fixture
def mock_workflow():
    with (
        patch.object(coordinator, "get_latest_incident") as latest,
        patch.object(coordinator, "get_incident_summary") as incident_summary,
        patch.object(coordinator, "get_victim_summary") as victim_summary,
        patch.object(coordinator, "get_hospital_summary") as hospital_summary,
        patch.object(coordinator, "get_resource_summary") as resource_summary,
        patch.object(coordinator, "forecast_emergency_demand") as forecast,
        patch.object(coordinator, "get_weather") as weather,
        patch.object(coordinator, "optimize_emergency_resources") as optimize,
        patch.object(coordinator, "get_emergency_route") as route,
        patch.object(coordinator, "generate_emergency_response") as ai,
        patch.object(coordinator, "create_emergency_notification") as notification,
    ):
        latest.return_value = None
        incident_summary.return_value = {"total_incidents": 5}
        victim_summary.return_value = {"total_victims": 8}
        hospital_summary.return_value = {"total_hospitals": 3}
        resource_summary.return_value = {"available_ambulances": 2}
        forecast.return_value = 4.0
        weather.return_value = {"condition": "Clear"}

        optimize.return_value = {
            "ambulance": {
                "vehicle_number": "AMB-101",
                "distance_km": 1.2,
                "latitude": 17.43,
                "longitude": 78.44,
            },
            "hospital": {
                "name": "City Hospital",
                "available_beds": 10,
                "distance_km": 2.3,
            },
            "rescue_team": {
                "team_name": "Team Alpha",
                "team_type": "Medical",
                "distance_km": 3.4,
            },
        }

        route.return_value = {
            "distance_km": 4.5,
            "time_minutes": 8.0,
        }
        ai.return_value = "Dispatch emergency resources."
        notification.return_value = "Emergency alert created."

        yield {
            "latest": latest,
            "optimize": optimize,
            "route": route,
            "ai": ai,
            "notification": notification,
        }


def test_coordinate_emergency_no_incident_raises_error(mock_workflow):
    with pytest.raises(RuntimeError, match="No active emergency incident"):
        coordinator.coordinate_emergency()


def test_coordinate_emergency_missing_coordinates_raises_error(
    incident, mock_workflow
):
    incident.latitude = None
    mock_workflow["latest"].return_value = incident

    with pytest.raises(RuntimeError, match="valid coordinates"):
        coordinator.coordinate_emergency()


def test_coordinate_emergency_success(incident, mock_workflow):
    mock_workflow["latest"].return_value = incident

    result = coordinator.coordinate_emergency()

    assert result["current_incident"]["id"] == 101
    assert result["current_incident"]["incident_type"] == "Road Accident"
    assert result["current_incident"]["severity"] == "High"
    assert result["demand_forecast"] == 4.0
    assert result["weather"] == {"condition": "Clear"}
    assert result["route"]["distance_km"] == 4.5
    assert result["gemini_recommendation"] == "Dispatch emergency resources."
    assert result["notification"] == "Emergency alert created."

    mock_workflow["optimize"].assert_called_once_with(
        17.4375,
        78.4483,
        required_beds=2,
        incident_type="Road Accident",
    )
    mock_workflow["route"].assert_called_once()
    mock_workflow["ai"].assert_called_once()
    mock_workflow["notification"].assert_called_once()


def test_coordinate_emergency_uses_image_incident_data(
    incident, mock_workflow
):
    mock_workflow["latest"].return_value = incident

    result = coordinator.coordinate_emergency(
        incident_data={
            "incident_type": "Fire",
            "severity": "Critical",
            "victims": 4,
        }
    )

    assert result["current_incident"]["incident_type"] == "Fire"
    assert result["current_incident"]["severity"] == "Critical"
    assert result["current_incident"]["victims"] == 4

    mock_workflow["optimize"].assert_called_once_with(
        17.4375,
        78.4483,
        required_beds=4,
        incident_type="Fire",
    )


def test_coordinate_emergency_without_ambulance_skips_route(
    incident, mock_workflow
):
    mock_workflow["latest"].return_value = incident
    mock_workflow["optimize"].return_value = {
        "ambulance": None,
        "hospital": None,
        "rescue_team": None,
    }

    mock_workflow["route"].return_value = None

    result = coordinator.coordinate_emergency()

    assert result["optimized_resources"]["ambulance"] is None
    assert result["optimized_resources"]["hospital"] is None
    assert result["route"] is None
    mock_workflow["route"].assert_not_called()
