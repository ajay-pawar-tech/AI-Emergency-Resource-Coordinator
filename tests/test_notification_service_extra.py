
from app.services.notification_service import create_emergency_notification


def sample_data():
    ambulance = {
        "vehicle_number": "AMB-101",
        "distance_km": 1.176,
    }

    hospital = {
        "name": "City Hospital",
        "available_beds": 25,
        "distance_km": 2.735,
    }

    rescue_team = {
        "team_name": "Rescue Team A",
        "team_type": "Fire Rescue",
        "distance_km": 3.204,
    }

    route = {
        "distance_km": 4.567,
        "time_minutes": 12.345,
    }

    return ambulance, hospital, rescue_team, route


def test_notification_contains_incident_details():
    ambulance, hospital, rescue_team, route = sample_data()

    result = create_emergency_notification(
        "Fire",
        "High",
        ambulance,
        hospital,
        rescue_team,
        route,
        "Dispatch resources immediately.",
    )

    assert "Incident Type: Fire" in result
    assert "Severity: High" in result
    assert "EMERGENCY ALERT" in result


def test_notification_contains_resource_details():
    ambulance, hospital, rescue_team, route = sample_data()

    result = create_emergency_notification(
        "Flood",
        "Critical",
        ambulance,
        hospital,
        rescue_team,
        route,
        "Send rescue support.",
    )

    assert "AMB-101" in result
    assert "City Hospital" in result
    assert "Available Beds: 25" in result
    assert "Rescue Team A" in result
    assert "Fire Rescue" in result


def test_notification_formats_distances_and_time():
    ambulance, hospital, rescue_team, route = sample_data()

    result = create_emergency_notification(
        "Accident",
        "Medium",
        ambulance,
        hospital,
        rescue_team,
        route,
        "Use the fastest route.",
    )

    assert "Distance: 1.18 km" in result
    assert "Distance: 2.73 km" in result
    assert "Distance: 3.20 km" in result
    assert "Distance: 4.57 km" in result
    assert "Estimated Travel Time: 12.35 minutes" in result


def test_notification_contains_ai_recommendation_and_footer():
    ambulance, hospital, rescue_team, route = sample_data()
    recommendation = "Dispatch the ambulance immediately."

    result = create_emergency_notification(
        "Road Accident",
        "High",
        ambulance,
        hospital,
        rescue_team,
        route,
        recommendation,
    )

    assert recommendation in result
    assert "END EMERGENCY ALERT" in result
    assert "Time:" in result
