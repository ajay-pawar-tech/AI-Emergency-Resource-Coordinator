
from app.agents import victim_agent


def test_get_incidents_with_victims_returns_records(monkeypatch):
    expected = ["incident_1", "incident_2"]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return expected

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_incidents_with_victims()

    assert result == expected
    assert fake_db.closed is True


def test_get_victim_summary_calculates_statistics(monkeypatch):
    class FakeIncident:
        def __init__(self, victims, critical_victims):
            self.victims = victims
            self.critical_victims = critical_victims

    incidents = [
        FakeIncident(10, 3),
        FakeIncident(5, 2),
        FakeIncident(0, 0),
    ]

    class FakeQuery:
        def all(self):
            return incidents

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_victim_summary()

    assert result == {
        "total_victims": 15,
        "critical_victims": 5,
        "non_critical_victims": 10,
        "incidents_with_victims": 2,
    }
    assert fake_db.closed is True


def test_get_victim_summary_handles_invalid_values(monkeypatch):
    class FakeIncident:
        def __init__(self, victims, critical_victims):
            self.victims = victims
            self.critical_victims = critical_victims

    incidents = [
        FakeIncident("invalid", "invalid"),
        FakeIncident(None, None),
        FakeIncident(4, 1),
    ]

    class FakeQuery:
        def all(self):
            return incidents

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_victim_summary()

    assert result == {
        "total_victims": 4,
        "critical_victims": 1,
        "non_critical_victims": 3,
        "incidents_with_victims": 1,
    }
    assert fake_db.closed is True


def test_get_victim_count_by_incident_returns_details(monkeypatch):
    class FakeIncident:
        id = 12
        incident_type = "Flood"
        severity = "High"
        victims = 8
        critical_victims = 3

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return FakeIncident()

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_victim_count_by_incident(12)

    assert result == {
        "incident_id": 12,
        "incident_type": "Flood",
        "severity": "High",
        "victims": 8,
        "critical_victims": 3,
        "non_critical_victims": 5,
    }
    assert fake_db.closed is True


def test_get_victim_count_by_incident_returns_none_if_missing(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_victim_count_by_incident(999)

    assert result is None
    assert fake_db.closed is True


def test_get_latest_incident_victims_returns_none_if_no_active_incident(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(victim_agent, "SessionLocal", lambda: fake_db)

    result = victim_agent.get_latest_incident_victims()

    assert result is None
    assert fake_db.closed is True
