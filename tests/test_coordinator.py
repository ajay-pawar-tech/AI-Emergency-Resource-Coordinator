
import pytest
from unittest.mock import patch

from app.agents import coordinator_agent
from app.database.repositories.incident_repository import IncidentRepository


def test_coordinate_emergency_raises_error_when_no_incident(monkeypatch):
    monkeypatch.setattr(
        coordinator_agent,
        "get_latest_incident",
        lambda: None,
    )

    with pytest.raises(
        RuntimeError,
        match="No active emergency incident found",
    ):
        coordinator_agent.coordinate_emergency()


def test_coordinate_emergency_raises_error_for_invalid_incident_id():
    with patch.object(
        IncidentRepository,
        "get_by_id",
        return_value=None,
    ) as mock_get_by_id:
        with pytest.raises(
            RuntimeError,
            match="was not found in the database",
        ):
            coordinator_agent.coordinate_emergency(
                incident_id=-999999
            )

    mock_get_by_id.assert_called_once()
