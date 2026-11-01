
from unittest.mock import MagicMock, patch

from app.agents import resource_agent as agent


def test_get_available_ambulances_closes_database():
    fake_ambulances = [
        MagicMock(id=1, status="available"),
        MagicMock(id=2, status="available"),
    ]
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        fake_ambulances
    )

    with patch.object(agent, "SessionLocal", return_value=db):
        result = agent.get_available_ambulances()

    assert result == fake_ambulances
    db.query.assert_called_once_with(agent.Ambulance)
    db.close.assert_called_once()


def test_get_active_hospitals_closes_database():
    fake_hospitals = [
        MagicMock(id=1, status="active"),
        MagicMock(id=2, status="active"),
    ]
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        fake_hospitals
    )

    with patch.object(agent, "SessionLocal", return_value=db):
        result = agent.get_active_hospitals()

    assert result == fake_hospitals
    db.query.assert_called_once_with(agent.Hospital)
    db.close.assert_called_once()


def test_get_available_rescue_teams_closes_database():
    fake_teams = [
        MagicMock(id=1, status="available"),
        MagicMock(id=2, status="available"),
    ]
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
        fake_teams
    )

    with patch.object(agent, "SessionLocal", return_value=db):
        result = agent.get_available_rescue_teams()

    assert result == fake_teams
    db.query.assert_called_once_with(agent.RescueTeam)
    db.close.assert_called_once()


def test_get_available_ambulances_closes_database_on_error():
    db = MagicMock()
    db.query.side_effect = RuntimeError("Database query failed")

    with patch.object(agent, "SessionLocal", return_value=db):
        try:
            agent.get_available_ambulances()
        except RuntimeError as error:
            assert str(error) == "Database query failed"
        else:
            raise AssertionError("Expected RuntimeError")

    db.close.assert_called_once()

def test_get_resource_summary_calculates_counts_and_beds():
    ambulances = [object(), object()]
    hospitals = [
        type("HospitalStub", (), {"available_beds": 5})(),
        type("HospitalStub", (), {"available_beds": 3})(),
        type("HospitalStub", (), {"available_beds": None})(),
    ]
    teams = [object(), object(), object()]

    db = MagicMock()
    db.query.return_value.filter.return_value.all.side_effect = [
        ambulances,
        hospitals,
        teams,
    ]

    with patch.object(agent, "SessionLocal", return_value=db):
        result = agent.get_resource_summary()

    assert result["available_ambulances"] == 2
    assert result["active_hospitals"] == 3
    assert result["available_beds"] == 8
    assert result["available_rescue_teams"] == 3
    db.close.assert_called_once()

def test_check_resource_availability_all_available():
    summary = {
        "available_ambulances": 2,
        "active_hospitals": 3,
        "available_beds": 10,
        "available_rescue_teams": 4,
    }

    with patch.object(
        agent, "get_resource_summary", return_value=summary
    ):
        result = agent.check_resource_availability(required_beds=5)

    assert result == {
        "ambulance_available": True,
        "hospital_available": True,
        "rescue_team_available": True,
        "all_resources_available": True,
    }


def test_check_resource_availability_insufficient_resources():
    summary = {
        "available_ambulances": 0,
        "active_hospitals": 1,
        "available_beds": 2,
        "available_rescue_teams": 0,
    }

    with patch.object(
        agent, "get_resource_summary", return_value=summary
    ):
        result = agent.check_resource_availability(required_beds=5)

    assert result == {
        "ambulance_available": False,
        "hospital_available": False,
        "rescue_team_available": False,
        "all_resources_available": False,
    }


from unittest.mock import patch

from app.agents import resource_agent


@patch("app.agents.resource_agent.get_resource_summary")
def test_check_availability_all_resources_available(mock_summary):
    mock_summary.return_value = {
        "available_ambulances": 2,
        "active_hospitals": 3,
        "available_beds": 10,
        "available_rescue_teams": 4,
    }

    result = resource_agent.check_resource_availability(required_beds=5)

    assert result == {
        "ambulance_available": True,
        "hospital_available": True,
        "rescue_team_available": True,
        "all_resources_available": True,
    }


@patch("app.agents.resource_agent.get_resource_summary")
def test_check_availability_no_ambulance(mock_summary):
    mock_summary.return_value = {
        "available_ambulances": 0,
        "active_hospitals": 2,
        "available_beds": 10,
        "available_rescue_teams": 3,
    }

    result = resource_agent.check_resource_availability(required_beds=2)

    assert result["ambulance_available"] is False
    assert result["hospital_available"] is True
    assert result["rescue_team_available"] is True
    assert result["all_resources_available"] is False


@patch("app.agents.resource_agent.get_resource_summary")
def test_check_availability_insufficient_beds(mock_summary):
    mock_summary.return_value = {
        "available_ambulances": 1,
        "active_hospitals": 2,
        "available_beds": 3,
        "available_rescue_teams": 1,
    }

    result = resource_agent.check_resource_availability(required_beds=5)

    assert result["ambulance_available"] is True
    assert result["hospital_available"] is False
    assert result["rescue_team_available"] is True
    assert result["all_resources_available"] is False


@patch("app.agents.resource_agent.get_resource_summary")
def test_check_availability_no_rescue_team(mock_summary):
    mock_summary.return_value = {
        "available_ambulances": 1,
        "active_hospitals": 1,
        "available_beds": 5,
        "available_rescue_teams": 0,
    }

    result = resource_agent.check_resource_availability(required_beds=1)

    assert result["ambulance_available"] is True
    assert result["hospital_available"] is True
    assert result["rescue_team_available"] is False
    assert result["all_resources_available"] is False


@patch("app.agents.resource_agent.get_resource_summary")
def test_check_availability_exact_bed_requirement(mock_summary):
    mock_summary.return_value = {
        "available_ambulances": 1,
        "active_hospitals": 1,
        "available_beds": 2,
        "available_rescue_teams": 1,
    }

    result = resource_agent.check_resource_availability(required_beds=2)

    assert result["hospital_available"] is True
    assert result["all_resources_available"] is True
