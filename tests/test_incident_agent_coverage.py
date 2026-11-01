
from unittest.mock import MagicMock, patch

from app.agents import incident_agent


def make_query(results=None, first=None, count=0, scalar=0):
    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.distinct.return_value = query
    query.all.return_value = results if results is not None else []
    query.first.return_value = first
    query.count.return_value = count
    query.scalar.return_value = scalar
    return query


@patch("app.agents.incident_agent.SessionLocal")
def test_find_incidents_by_type_returns_results_and_closes_db(mock_session):
    incident = MagicMock()
    db = mock_session.return_value
    db.query.return_value = make_query(results=[incident])

    result = incident_agent.find_incidents_by_type("Flood")

    assert result == [incident]
    db.close.assert_called_once()


@patch("app.agents.incident_agent.SessionLocal")
def test_get_incident_count_returns_count_and_closes_db(mock_session):
    db = mock_session.return_value
    db.query.return_value = make_query(count=7)

    result = incident_agent.get_incident_count()

    assert result == 7
    db.close.assert_called_once()


@patch("app.agents.incident_agent.SessionLocal")
def test_get_incidents_by_status_is_case_insensitive(mock_session):
    incident = MagicMock()
    db = mock_session.return_value
    db.query.return_value = make_query(results=[incident])

    result = incident_agent.get_incidents_by_status("ACTIVE")

    assert result == [incident]
    db.close.assert_called_once()


@patch("app.agents.incident_agent.SessionLocal")
def test_get_latest_incident_returns_active_incident(mock_session):
    incident = MagicMock()
    db = mock_session.return_value
    db.query.return_value = make_query(first=incident)

    result = incident_agent.get_latest_incident()

    assert result is incident
    db.close.assert_called_once()


@patch("app.agents.incident_agent.SessionLocal")
def test_get_latest_incident_falls_back_to_latest_record(mock_session):
    historical_incident = MagicMock()
    db = mock_session.return_value

    # First three operational searches return no incident.
    # The fourth query returns the latest database record.
    queries = [
        make_query(first=None),
        make_query(first=None),
        make_query(first=None),
        make_query(first=historical_incident),
    ]

    db.query.side_effect = queries

    result = incident_agent.get_latest_incident()

    assert result is historical_incident
    assert db.query.call_count == 4
    db.close.assert_called_once()
