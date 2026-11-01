
import pytest

from app.optimization.resource_allocator import (
    calculate_distance,
    find_best_hospital,
    find_best_rescue_team,
)


# ==========================================
# DISTANCE CALCULATION TESTS
# ==========================================

def test_distance_between_same_coordinates_is_zero():
    distance = calculate_distance(
        18.5204, 73.8567,
        18.5204, 73.8567,
    )

    assert distance == pytest.approx(0.0)


def test_distance_between_different_coordinates_is_positive():
    distance = calculate_distance(
        18.5204, 73.8567,
        19.0760, 72.8777,
    )

    assert distance > 0


def test_distance_is_symmetric():
    distance_forward = calculate_distance(
        18.5204, 73.8567,
        19.0760, 72.8777,
    )

    distance_backward = calculate_distance(
        19.0760, 72.8777,
        18.5204, 73.8567,
    )

    assert distance_forward == pytest.approx(
        distance_backward
    )


# ==========================================
# HOSPITAL ALLOCATION TESTS
# ==========================================

def test_find_best_hospital_returns_none_when_no_hospitals(
    monkeypatch,
):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "app.optimization.resource_allocator.SessionLocal",
        lambda: FakeDB(),
    )

    result = find_best_hospital(
        emergency_latitude=18.5204,
        emergency_longitude=73.8567,
        required_beds=1,
    )

    assert result is None
def test_find_best_hospital_selects_nearest_hospital(
    monkeypatch,
):
    from types import SimpleNamespace

    nearby_hospital = SimpleNamespace(
        id=1,
        name="Nearby Hospital",
        city="Pune",
        status="active",
        total_beds=100,
        available_beds=20,
        latitude=18.5300,
        longitude=73.8600,
    )

    far_hospital = SimpleNamespace(
        id=2,
        name="Far Hospital",
        city="Mumbai",
        status="active",
        total_beds=200,
        available_beds=50,
        latitude=19.0760,
        longitude=72.8777,
    )

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [far_hospital, nearby_hospital]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "app.optimization.resource_allocator.SessionLocal",
        lambda: FakeDB(),
    )

    result = find_best_hospital(
        emergency_latitude=18.5204,
        emergency_longitude=73.8567,
        required_beds=1,
    )

    assert result is not None
    assert result["id"] == 1
    assert result["name"] == "Nearby Hospital"
    assert result["distance_km"] > 0


# ==========================================
# RESCUE TEAM ALLOCATION TESTS
# ==========================================

def test_find_best_rescue_team_returns_none_when_no_teams(
    monkeypatch,
):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return []

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "app.optimization.resource_allocator.SessionLocal",
        lambda: FakeDB(),
    )

    result = find_best_rescue_team(
        emergency_latitude=18.5204,
        emergency_longitude=73.8567,
        incident_type="Fire",
    )

    assert result is None
def test_find_best_rescue_team_selects_nearest_matching_team(
    monkeypatch,
):
    from types import SimpleNamespace

    nearby_team = SimpleNamespace(
        id=1,
        team_name="Nearby Fire Team",
        team_type="Fire Rescue",
        members=5,
        city="Pune",
        status="available",
        latitude=18.5300,
        longitude=73.8600,
    )

    far_team = SimpleNamespace(
        id=2,
        team_name="Far Fire Team",
        team_type="Fire Rescue",
        members=8,
        city="Mumbai",
        status="available",
        latitude=19.0760,
        longitude=72.8777,
    )

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return [far_team, nearby_team]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        "app.optimization.resource_allocator.SessionLocal",
        lambda: FakeDB(),
    )

    result = find_best_rescue_team(
        emergency_latitude=18.5204,
        emergency_longitude=73.8567,
        incident_type="Fire",
    )

    assert result is not None
    assert result["id"] == 1
    assert result["team_name"] == "Nearby Fire Team"
    assert result["team_type"] == "Fire Rescue"
    assert result["distance_km"] > 0
