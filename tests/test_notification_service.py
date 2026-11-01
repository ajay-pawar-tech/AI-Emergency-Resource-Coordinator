
from app.services.notification_service import create_emergency_notification


def sample_data():
    return {
        "incident_type": "Road Accident",
        "severity": "High",
        "ambulance": {
            "vehicle_number": "AMB-101",
            "distance_km": 1.234,
        },
        "hospital": {
            "name": "City Hospital",
            "available_beds": 12,
            "distance_km": 2.345,
        },
        "rescue_team": {
            "team_name": "Rescue Team 1",
            "team_type": "Medical",
            "distance_km": 3.456,
        },
        "route": {
            "distance_km": 4.567,
            "time_minutes": 8.789,
        },
        "gemini_recommendation": "Dispatch ambulance immediately.",
    }


def test_notification_contains_incident_details():
    data = sample_data()

    result = create_emergency_notification(**data)

    assert "Road Accident" in result
    assert "Severity: High" in result
    assert "EMERGENCY ALERT" in result
    assert "END EMERGENCY ALERT" in result


def test_notification_contains_ambulance_details():
    data = sample_data()

    result = create_emergency_notification(**data)

    assert "AMB-101" in result
    assert "Distance: 1.23 km" in result


def test_notification_contains_hospital_details():
    data = sample_data()

    result = create_emergency_notification(**data)

    assert "City Hospital" in result
    assert "Available Beds: 12" in result
    assert "Distance: 2.35 km" in result


def test_notification_contains_rescue_and_route_details():
    data = sample_data()

    result = create_emergency_notification(**data)

    assert "Rescue Team 1" in result
    assert "Medical" in result
    assert "Distance: 3.46 km" in result
    assert "Distance: 4.57 km" in result
    assert "Estimated Travel Time: 8.79 minutes" in result


def test_notification_contains_ai_recommendation_and_timestamp():
    data = sample_data()

    result = create_emergency_notification(**data)

    assert "Dispatch ambulance immediately." in result
    assert "Time:" in result
