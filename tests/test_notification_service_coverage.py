
from app.services.notification_service import create_emergency_notification


def sample_notification_data():
    return {
        "incident_type": "Road Accident",
        "severity": "High",
        "ambulance": {
            "vehicle_number": "AMB-101",
            "distance_km": 2.345,
        },
        "hospital": {
            "name": "City Hospital",
            "available_beds": 12,
            "distance_km": 3.456,
        },
        "rescue_team": {
            "team_name": "Team Alpha",
            "team_type": "Medical",
            "distance_km": 1.234,
        },
        "route": {
            "distance_km": 4.567,
            "time_minutes": 10.789,
        },
        "gemini_recommendation": "Send medical assistance immediately.",
    }


def test_notification_contains_incident_details():
    data = sample_notification_data()

    result = create_emergency_notification(**data)

    assert "Incident Type: Road Accident" in result
    assert "Severity: High" in result


def test_notification_contains_all_resource_details():
    data = sample_notification_data()

    result = create_emergency_notification(**data)

    assert "AMB-101" in result
    assert "City Hospital" in result
    assert "Available Beds: 12" in result
    assert "Team Alpha" in result
    assert "Team Type: Medical" in result


def test_notification_formats_distances_and_travel_time():
    data = sample_notification_data()

    result = create_emergency_notification(**data)

    assert "Distance: 2.35 km" in result
    assert "Distance: 3.46 km" in result
    assert "Distance: 1.23 km" in result
    assert "Distance: 4.57 km" in result
    assert "Estimated Travel Time: 10.79 minutes" in result


def test_notification_contains_ai_recommendation_and_footer():
    data = sample_notification_data()

    result = create_emergency_notification(**data)

    assert "Send medical assistance immediately." in result
    assert "END EMERGENCY ALERT" in result
