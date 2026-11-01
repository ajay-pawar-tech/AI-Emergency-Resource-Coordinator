
from unittest.mock import patch

from app.agents.optimization_agent import optimize_emergency_resources


@patch("app.agents.optimization_agent.find_best_rescue_team")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_nearest_ambulance")
def test_returns_all_selected_resources(
    mock_ambulance,
    mock_hospital,
    mock_rescue_team,
):
    ambulance = {"vehicle_number": "AMB-01"}
    hospital = {"name": "City Hospital"}
    rescue_team = {"team_name": "Team Alpha"}

    mock_ambulance.return_value = ambulance
    mock_hospital.return_value = hospital
    mock_rescue_team.return_value = rescue_team

    result = optimize_emergency_resources(17.385, 78.4867, 2, "Flood")

    assert result == {
        "ambulance": ambulance,
        "hospital": hospital,
        "rescue_team": rescue_team,
    }


@patch("app.agents.optimization_agent.find_best_rescue_team")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_nearest_ambulance")
def test_passes_correct_arguments(
    mock_ambulance,
    mock_hospital,
    mock_rescue_team,
):
    optimize_emergency_resources(17.385, 78.4867, 3, "Fire")

    mock_ambulance.assert_called_once_with(17.385, 78.4867)
    mock_hospital.assert_called_once_with(17.385, 78.4867, 3)
    mock_rescue_team.assert_called_once_with(17.385, 78.4867, "Fire")


@patch("app.agents.optimization_agent.find_best_rescue_team")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_nearest_ambulance")
def test_handles_no_available_resources(
    mock_ambulance,
    mock_hospital,
    mock_rescue_team,
):
    mock_ambulance.return_value = None
    mock_hospital.return_value = None
    mock_rescue_team.return_value = None

    result = optimize_emergency_resources(17.385, 78.4867)

    assert result == {
        "ambulance": None,
        "hospital": None,
        "rescue_team": None,
    }


@patch("app.agents.optimization_agent.find_best_rescue_team")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_nearest_ambulance")
def test_default_arguments(
    mock_ambulance,
    mock_hospital,
    mock_rescue_team,
):
    optimize_emergency_resources(17.385, 78.4867)

    mock_hospital.assert_called_once_with(17.385, 78.4867, 1)
    mock_rescue_team.assert_called_once_with(17.385, 78.4867, None)
