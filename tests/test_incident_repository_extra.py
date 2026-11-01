
from unittest.mock import MagicMock

from app.database.repositories.incident_repository import IncidentRepository


def create_mock_db(incident=None):
    db = MagicMock()
    query = db.query.return_value
    query.filter.return_value.first.return_value = incident
    query.offset.return_value.limit.return_value.all.return_value = []
    return db


def test_create_incident():
    db = create_mock_db()
    incident_data = {
        "incident_type": "Fire",
        "severity": "High",
        "city": "Hyderabad",
    }

    result = IncidentRepository.create(db, incident_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)
    assert result is not None


def test_get_by_id_returns_incident():
    incident = MagicMock()
    db = create_mock_db(incident)

    result = IncidentRepository.get_by_id(db, 10)

    assert result is incident


def test_get_by_id_returns_none_when_missing():
    db = create_mock_db()

    result = IncidentRepository.get_by_id(db, 999)

    assert result is None


def test_get_all_returns_incidents():
    incidents = [MagicMock(), MagicMock()]
    db = create_mock_db()
    db.query.return_value.offset.return_value.limit.return_value.all.return_value = incidents

    result = IncidentRepository.get_all(db, skip=5, limit=10)

    assert result == incidents
    db.query.return_value.offset.assert_called_once_with(5)
    db.query.return_value.offset.return_value.limit.assert_called_once_with(10)


def test_update_incident_fields():
    incident = MagicMock()
    db = create_mock_db(incident)
    update_data = {
        "severity": "Critical",
        "city": "Pune",
        "unknown_field": "ignored",
    }

    result = IncidentRepository.update(db, 10, update_data)

    assert result is incident
    assert incident.severity == "Critical"
    assert incident.city == "Pune"
    assert "unknown_field" not in incident.__dict__
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(incident)


def test_update_returns_none_when_missing():
    db = create_mock_db()

    result = IncidentRepository.update(db, 999, {"severity": "High"})

    assert result is None
    db.commit.assert_not_called()


def test_delete_existing_incident():
    incident = MagicMock()
    db = create_mock_db(incident)

    result = IncidentRepository.delete(db, 10)

    assert result is True
    db.delete.assert_called_once_with(incident)
    db.commit.assert_called_once()


def test_delete_missing_incident():
    db = create_mock_db()

    result = IncidentRepository.delete(db, 999)

    assert result is False
    db.delete.assert_not_called()
    db.commit.assert_not_called()
