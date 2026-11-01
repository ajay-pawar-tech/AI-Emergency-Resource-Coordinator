
from app.database.models import Incident, Hospital, Ambulance, RescueTeam


def test_incident_model_defaults():
    incident = Incident(
        incident_type="Road Accident",
        severity="High",
        city="Pune",
        location="Test Location",
    )

    assert incident.incident_type == "Road Accident"
    assert incident.severity == "High"
    assert incident.city == "Pune"
    assert incident.location == "Test Location"


def test_hospital_model_fields():
    hospital = Hospital(
        name="Test Hospital",
        city="Pune",
        total_beds=100,
        available_beds=25,
    )

    assert hospital.name == "Test Hospital"
    assert hospital.total_beds == 100
    assert hospital.available_beds == 25


def test_ambulance_model_fields():
    ambulance = Ambulance(
        vehicle_number="TEST-AMB-001",
        vehicle_type="Basic Life Support",
        city="Pune",
    )

    assert ambulance.vehicle_number == "TEST-AMB-001"
    assert ambulance.city == "Pune"


def test_rescue_team_model_fields():
    team = RescueTeam(
        team_name="Test Rescue Team",
        team_type="Search and Rescue",
        city="Pune",
    )

    assert team.team_name == "Test Rescue Team"
    assert team.team_type == "Search and Rescue"
