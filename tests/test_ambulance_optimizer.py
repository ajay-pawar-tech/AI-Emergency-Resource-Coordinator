
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.optimization import ambulance_optimizer as optimizer


def make_ambulance(
    ambulance_id,
    latitude,
    longitude,
    vehicle_number="AMB-101",
):
    return SimpleNamespace(
        id=ambulance_id,
        vehicle_number=vehicle_number,
        vehicle_type="Basic",
        status="available",
        capacity=2,
        city="Hyderabad",
        latitude=latitude,
        longitude=longitude,
    )


def test_calculate_distance_same_coordinates():
    distance = optimizer.calculate_distance(
        17.3850, 78.4867,
        17.3850, 78.4867,
    )

    assert distance == pytest.approx(0.0)


def test_calculate_distance_is_positive():
    distance = optimizer.calculate_distance(
        17.3850, 78.4867,
        17.4419, 78.3750,
    )

    assert distance > 0
    assert distance == pytest.approx(13.5, abs=1.0)


def test_find_nearest_ambulance_none_available():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []

    with patch.object(optimizer, "SessionLocal", return_value=mock_db):
        result = optimizer.find_nearest_ambulance(17.3850, 78.4867)

    assert result is None
    mock_db.close.assert_called_once()


def test_find_nearest_ambulance_skips_missing_coordinates():
    ambulance = make_ambulance(1, None, None)

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [
        ambulance
    ]

    with patch.object(optimizer, "SessionLocal", return_value=mock_db):
        result = optimizer.find_nearest_ambulance(17.3850, 78.4867)

    assert result is None
    mock_db.close.assert_called_once()


def test_find_nearest_ambulance_selects_closest():
    far_ambulance = make_ambulance(
        1, 17.5000, 78.6000, "AMB-FAR"
    )
    near_ambulance = make_ambulance(
        2, 17.3860, 78.4870, "AMB-NEAR"
    )

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [
        far_ambulance,
        near_ambulance,
    ]

    with patch.object(optimizer, "SessionLocal", return_value=mock_db):
        result = optimizer.find_nearest_ambulance(17.3850, 78.4867)

    assert result is not None
    assert result["ambulance_id"] == 2
    assert result["vehicle_number"] == "AMB-NEAR"
    assert result["status"] == "available"
    assert result["distance_km"] >= 0
    assert result["distance_km"] < 1
    mock_db.close.assert_called_once()


def test_find_nearest_ambulance_all_coordinates_missing():
    ambulances = [
        make_ambulance(1, None, 78.4),
        make_ambulance(2, 17.4, None),
    ]

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = ambulances

    with patch.object(optimizer, "SessionLocal", return_value=mock_db):
        result = optimizer.find_nearest_ambulance(17.3850, 78.4867)

    assert result is None
    mock_db.close.assert_called_once()


def test_find_nearest_ambulance_returns_expected_fields():
    ambulance = make_ambulance(7, 17.3860, 78.4870, "AMB-007")

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [
        ambulance
    ]

    with patch.object(optimizer, "SessionLocal", return_value=mock_db):
        result = optimizer.find_nearest_ambulance(17.3850, 78.4867)

    assert result["id"] == 7
    assert result["ambulance_id"] == 7
    assert result["vehicle_number"] == "AMB-007"
    assert result["vehicle_type"] == "Basic"
    assert result["capacity"] == 2
    assert result["city"] == "Hyderabad"
    assert "latitude" in result
    assert "longitude" in result
    assert "distance_km" in result


def test_database_closes_when_query_raises_error():
    mock_db = MagicMock()
    mock_db.query.side_effect = RuntimeError("Database error")

    with (
        patch.object(optimizer, "SessionLocal", return_value=mock_db),
        pytest.raises(RuntimeError, match="Database error"),
    ):
        optimizer.find_nearest_ambulance(17.3850, 78.4867)

    mock_db.close.assert_called_once()
