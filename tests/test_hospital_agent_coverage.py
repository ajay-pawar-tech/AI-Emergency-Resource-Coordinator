
from unittest.mock import MagicMock, patch

from app.agents import hospital_agent


def mock_query_chain(results):
    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = results
    query.first.return_value = results[0] if results else None
    return query


@patch("app.agents.hospital_agent.SessionLocal")
def test_get_active_hospitals_returns_results_and_closes_db(mock_session):
    hospital1 = MagicMock()
    hospital2 = MagicMock()

    db = mock_session.return_value
    db.query.return_value = mock_query_chain([hospital1, hospital2])

    result = hospital_agent.get_active_hospitals()

    assert result == [hospital1, hospital2]
    db.close.assert_called_once()


@patch("app.agents.hospital_agent.SessionLocal")
def test_find_hospitals_with_beds_returns_results_and_closes_db(mock_session):
    hospital = MagicMock()
    db = mock_session.return_value
    db.query.return_value = mock_query_chain([hospital])

    result = hospital_agent.find_hospitals_with_beds(required_beds=4)

    assert result == [hospital]
    db.close.assert_called_once()


@patch("app.agents.hospital_agent.SessionLocal")
def test_get_hospital_summary_calculates_statistics_and_closes_db(mock_session):
    hospitals = [
        MagicMock(
            status="active",
            total_beds=10,
            available_beds=3,
        ),
        MagicMock(
            status="inactive",
            total_beds=20,
            available_beds=0,
        ),
        MagicMock(
            status="ACTIVE",
            total_beds=15,
            available_beds=1,
        ),
        MagicMock(
            status="active",
            total_beds=None,
            available_beds=None,
        ),
    ]

    db = mock_session.return_value
    db.query.return_value.all.return_value = hospitals

    result = hospital_agent.get_hospital_summary()

    assert result == {
        "total_hospitals": 4,
        "active_hospitals": 3,
        "total_beds": 45,
        "available_beds": 4,
        "hospitals_with_2_beds": 1,
        "hospitals_with_beds": 2,
    }
    db.close.assert_called_once()


@patch("app.agents.hospital_agent.SessionLocal")
def test_get_hospital_by_id_returns_hospital_and_closes_db(mock_session):
    hospital = MagicMock()
    db = mock_session.return_value
    db.query.return_value = mock_query_chain([hospital])

    result = hospital_agent.get_hospital_by_id(7)

    assert result is hospital
    db.close.assert_called_once()


@patch("app.agents.hospital_agent.SessionLocal")
def test_get_hospital_by_id_returns_none_when_not_found(mock_session):
    db = mock_session.return_value
    db.query.return_value = mock_query_chain([])

    result = hospital_agent.get_hospital_by_id(99999)

    assert result is None
    db.close.assert_called_once()
