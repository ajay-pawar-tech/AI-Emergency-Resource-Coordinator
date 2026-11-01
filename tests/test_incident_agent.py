from app.agents import incident_agent


def test_find_incidents_by_type_returns_matching_incidents(
    monkeypatch,
):
    expected_incidents = [
        {"id": 3, "incident_type": "Flood"},
        {"id": 2, "incident_type": "Flood"},
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return expected_incidents

    class FakeDB:
        def __init__(self):
            self.closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.find_incidents_by_type("Flood")

    assert result == expected_incidents
    assert fake_db.closed is True


def test_get_incident_count_returns_total_count(monkeypatch):
    class FakeQuery:
        def count(self):
            return 42

    class FakeDB:
        def __init__(self):
            self.closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_incident_count()

    assert result == 42
    assert fake_db.closed is True


def test_get_incidents_by_status_returns_matching_incidents(
    monkeypatch,
):
    expected_incidents = [
        {"id": 10, "status": "active"},
        {"id": 8, "status": "active"},
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return expected_incidents

    class FakeDB:
        def __init__(self):
            self.closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_incidents_by_status("ACTIVE")

    assert result == expected_incidents
    assert fake_db.closed is True


def test_get_latest_incident_prefers_active_operational_incident(
    monkeypatch,
):
    active_incident = {
        "id": 12,
        "status": "active",
        "location": "Hyderabad",
    }

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            return active_incident

    class FakeDB:
        def __init__(self):
            self.closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_latest_incident()

    assert result == active_incident
    assert fake_db.closed is True


def test_get_latest_incident_falls_back_to_in_progress(
    monkeypatch,
):
    in_progress_incident = {
        "id": 15,
        "status": "in_progress",
        "location": "Hyderabad",
    }

    class FakeQuery:
        def __init__(self, db):
            self.db = db

        def filter(self, *args, **kwargs):
            self.db.filter_calls += 1
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            if self.db.filter_calls == 1:
                return None
            return in_progress_incident

    class FakeDB:
        def __init__(self):
            self.closed = False
            self.filter_calls = 0

        def query(self, *args, **kwargs):
            return FakeQuery(self)

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_latest_incident()

    assert result == in_progress_incident
    assert fake_db.closed is True


def test_get_latest_incident_falls_back_to_latest_operational(
    monkeypatch,
):
    operational_incident = {
        "id": 20,
        "status": "resolved",
        "location": "Hyderabad",
    }

    class FakeQuery:
        def __init__(self, db):
            self.db = db

        def filter(self, *args, **kwargs):
            self.db.filter_calls += 1
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            if self.db.filter_calls <= 2:
                return None
            return operational_incident

    class FakeDB:
        def __init__(self):
            self.closed = False
            self.filter_calls = 0

        def query(self, *args, **kwargs):
            return FakeQuery(self)

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_latest_incident()

    assert result == operational_incident
    assert fake_db.closed is True


def test_get_incident_summary_returns_expected_statistics(
    monkeypatch,
):
    class FakeQuery:
        def __init__(self, query_number):
            self.query_number = query_number

        def filter(self, *args, **kwargs):
            return self

        def count(self):
            return {
                1: 10,  # Total incidents
                2: 4,   # Active/in-progress incidents
                5: 3,   # Flood incidents
            }[self.query_number]

        def scalar(self):
            return 25  # Total victims

        def distinct(self):
            return self

        def all(self):
            return [
                ("Flood",),
                ("Fire",),
                (None,),
            ]

    class FakeDB:
        def __init__(self):
            self.closed = False
            self.query_number = 0

        def query(self, *args, **kwargs):
            self.query_number += 1
            return FakeQuery(self.query_number)

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        incident_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = incident_agent.get_incident_summary()

    assert result == {
        "total_incidents": 10,
        "active_incidents": 4,
        "total_victims": 25,
        "incident_types": ["Flood", "Fire"],
        "flood_incidents": 3,
    }

    assert fake_db.closed is True