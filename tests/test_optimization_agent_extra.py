from unittest.mock import patch

from app.agents.optimization_agent import optimize_emergency_resources


@patch("app.agents.optimization_agent.find_nearest_ambulance")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_best_rescue_team")
def test_optimize_returns_all_resources(
    mock_rescue,
    mock_hospital,
    mock_ambulance,
):
    mock_ambulance.return_value = {"vehicle_number": "AMB-101"}
    mock_hospital.return_value = {"name": "City Hospital"}
    mock_rescue.return_value = {"team_name": "Rescue Team A"}

    result = optimize_emergency_resources(
        17.3850,
        78.4867,
        required_beds=2,
        incident_type="Fire",
    )

    assert result["ambulance"]["vehicle_number"] == "AMB-101"
    assert result["hospital"]["name"] == "City Hospital"
    assert result["rescue_team"]["team_name"] == "Rescue Team A"


@patch("app.agents.optimization_agent.find_nearest_ambulance")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_best_rescue_team")
def test_optimize_when_resources_unavailable(
    mock_rescue,
    mock_hospital,
    mock_ambulance,
):
    mock_ambulance.return_value = None
    mock_hospital.return_value = None
    mock_rescue.return_value = None

    result = optimize_emergency_resources(17.3850, 78.4867)

    assert result == {
        "ambulance": None,
        "hospital": None,
        "rescue_team": None,
    }


@patch("app.agents.optimization_agent.find_nearest_ambulance")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_best_rescue_team")
def test_optimize_passes_custom_parameters(
    mock_rescue,
    mock_hospital,
    mock_ambulance,
):
    mock_ambulance.return_value = None
    mock_hospital.return_value = None
    mock_rescue.return_value = None

    optimize_emergency_resources(
        18.5204,
        73.8567,
        required_beds=5,
        incident_type="Medical",
    )

    mock_ambulance.assert_called_once_with(18.5204, 73.8567)
    mock_hospital.assert_called_once_with(18.5204, 73.8567, 5)
    mock_rescue.assert_called_once_with(
        18.5204, 73.8567, "Medical"
    )


@patch("app.agents.optimization_agent.find_nearest_ambulance")
@patch("app.agents.optimization_agent.find_best_hospital")
@patch("app.agents.optimization_agent.find_best_rescue_team")
def test_optimize_handles_partial_resource_availability(
    mock_rescue,
    mock_hospital,
    mock_ambulance,
):
    mock_ambulance.return_value = None
    mock_hospital.return_value = {"name": "Available Hospital"}
    mock_rescue.return_value = None

    result = optimize_emergency_resources(17.3850, 78.4867)

    assert result["ambulance"] is None
    assert result["hospital"]["name"] == "Available Hospital"
    assert result["rescue_team"] is None