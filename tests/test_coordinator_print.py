
from app.agents import coordinator_agent


def sample_result(ambulance=True, hospital=True, rescue_team=True, route=True):
    return {
        "current_incident": {
            "id": 101,
            "incident_type": "Road Accident",
            "severity": "High",
            "city": "Hyderabad",
            "location": "Ameerpet",
            "victims": 3,
            "critical_victims": 1,
        },
        "incident_summary": {
            "total_incidents": 10,
            "active_incidents": 2,
        },
        "victim_summary": {
            "total_victims": 20,
            "critical_victims": 3,
            "non_critical_victims": 17,
        },
        "hospital_summary": {
            "total_hospitals": 5,
            "active_hospitals": 4,
            "available_beds": 25,
        },
        "resource_summary": {
            "available_ambulances": 3,
            "available_rescue_teams": 2,
        },
        "demand_forecast": 4.5,
        "optimized_resources": {
            "ambulance": (
                {"vehicle_number": "AMB-01", "distance_km": 2.35}
                if ambulance else None
            ),
            "hospital": (
                {"name": "City Hospital", "available_beds": 10,
                 "distance_km": 3.25}
                if hospital else None
            ),
            "rescue_team": (
                {"team_name": "Team Alpha", "team_type": "Medical",
                 "distance_km": 1.75}
                if rescue_team else None
            ),
        },
        "route": (
            {"distance_km": 4.5, "time_minutes": 12}
            if route else None
        ),
        "gemini_recommendation": "Send medical assistance immediately.",
        "notification": "Emergency notification created.",
    }


def test_print_emergency_result_with_all_resources(capsys):
    coordinator_agent.print_emergency_result(sample_result())

    output = capsys.readouterr().out

    assert "AI EMERGENCY COORDINATION SYSTEM" in output
    assert "Road Accident" in output
    assert "AMB-01" in output
    assert "City Hospital" in output
    assert "Team Alpha" in output
    assert "Emergency notification created." in output
    assert "COORDINATION COMPLETED" in output


def test_print_emergency_result_without_resources(capsys):
    result = sample_result(
        ambulance=False,
        hospital=False,
        rescue_team=False,
        route=False,
    )

    coordinator_agent.print_emergency_result(result)

    output = capsys.readouterr().out

    assert "No ambulance available." in output
    assert "No suitable hospital available." in output
    assert "No rescue team available." in output
    assert "Route unavailable." in output


def test_print_emergency_result_includes_recommendation(capsys):
    result = sample_result()
    result["gemini_recommendation"] = "Prioritize critical victims."

    coordinator_agent.print_emergency_result(result)

    output = capsys.readouterr().out

    assert "AI EMERGENCY RECOMMENDATION" in output
    assert "Prioritize critical victims." in output
