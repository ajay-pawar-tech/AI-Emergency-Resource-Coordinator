
from unittest.mock import patch

from app.agents import optimization_agent as agent


def test_optimize_emergency_resources_returns_all_resources():
    ambulance = {
        "vehicle_number": "AMB-101",
        "distance_km": 1.2,
    }
    hospital = {
        "name": "City Hospital",
        "available_beds": 10,
        "distance_km": 2.3,
    }
    rescue_team = {
        "team_name": "Team Alpha",
        "team_type": "Medical",
        "distance_km": 3.4,
    }

    with (
        patch.object(
            agent, "find_nearest_ambulance",
            return_value=ambulance,
        ) as mock_ambulance,
        patch.object(
            agent, "find_best_hospital",
            return_value=hospital,
        ) as mock_hospital,
        patch.object(
            agent, "find_best_rescue_team",
            return_value=rescue_team,
        ) as mock_team,
    ):
        result = agent.optimize_emergency_resources(
            17.3850,
            78.4867,
            required_beds=2,
            incident_type="Fire",
        )

    assert result == {
        "ambulance": ambulance,
        "hospital": hospital,
        "rescue_team": rescue_team,
    }

    mock_ambulance.assert_called_once_with(17.3850, 78.4867)
    mock_hospital.assert_called_once_with(17.3850, 78.4867, 2)
    mock_team.assert_called_once_with(
        17.3850, 78.4867, "Fire"
    )


def test_optimize_emergency_resources_when_no_resources_found():
    with (
        patch.object(
            agent, "find_nearest_ambulance",
            return_value=None,
        ),
        patch.object(
            agent, "find_best_hospital",
            return_value=None,
        ),
        patch.object(
            agent, "find_best_rescue_team",
            return_value=None,
        ),
    ):
        result = agent.optimize_emergency_resources(
            17.3850,
            78.4867,
        )

    assert result == {
        "ambulance": None,
        "hospital": None,
        "rescue_team": None,
    }


def test_optimize_emergency_resources_uses_default_beds():
    with (
        patch.object(
            agent, "find_nearest_ambulance",
            return_value=None,
        ),
        patch.object(
            agent, "find_best_hospital",
            return_value=None,
        ) as mock_hospital,
        patch.object(
            agent, "find_best_rescue_team",
            return_value=None,
        ) as mock_team,
    ):
        agent.optimize_emergency_resources(17.3850, 78.4867)

    mock_hospital.assert_called_once_with(
        17.3850, 78.4867, 1
    )
    mock_team.assert_called_once_with(
        17.3850, 78.4867, None
    )


def test_optimize_emergency_resources_passes_custom_bed_count():
    with (
        patch.object(
            agent, "find_nearest_ambulance",
            return_value=None,
        ),
        patch.object(
            agent, "find_best_hospital",
            return_value=None,
        ) as mock_hospital,
        patch.object(
            agent, "find_best_rescue_team",
            return_value=None,
        ),
    ):
        agent.optimize_emergency_resources(
            17.4,
            78.5,
            required_beds=5,
        )

    mock_hospital.assert_called_once_with(17.4, 78.5, 5)
