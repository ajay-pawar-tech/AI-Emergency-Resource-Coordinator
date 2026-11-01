
from app.agents import resource_agent


def test_get_available_ambulances_returns_records(monkeypatch):
    expected = ["ambulance_1", "ambulance_2"]

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
    monkeypatch.setattr(resource_agent, "SessionLocal", lambda: fake_db)

    result = resource_agent.get_available_ambulances()

    assert result == expected
    assert fake_db.closed is True


def test_get_active_hospitals_returns_records(monkeypatch):
    expected = ["hospital_1"]

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
    monkeypatch.setattr(resource_agent, "SessionLocal", lambda: fake_db)

    result = resource_agent.get_active_hospitals()

    assert result == expected
    assert fake_db.closed is True


def test_get_available_rescue_teams_returns_records(monkeypatch):
    expected = ["team_1", "team_2"]

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
    monkeypatch.setattr(resource_agent, "SessionLocal", lambda: fake_db)

    result = resource_agent.get_available_rescue_teams()

    assert result == expected
    assert fake_db.closed is True


def test_get_resource_summary_returns_correct_counts(monkeypatch):
    class FakeAmbulance:
        pass

    class FakeHospital:
        def __init__(self, beds):
            self.available_beds = beds

    class FakeRescueTeam:
        pass

    query_results = [
        [FakeAmbulance(), FakeAmbulance()],
        [FakeHospital(10), FakeHospital(5), FakeHospital(None)],
        [FakeRescueTeam()]
    ]

    class FakeQuery:
        def __init__(self, result):
            self.result = result

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return self.result

    class FakeDB:
        closed = False

        def __init__(self):
            self.query_number = 0

        def query(self, *args, **kwargs):
            result = query_results[self.query_number]
            self.query_number += 1
            return FakeQuery(result)

        def close(self):
            self.closed = True

    fake_db = FakeDB()
    monkeypatch.setattr(resource_agent, "SessionLocal", lambda: fake_db)

    result = resource_agent.get_resource_summary()

    assert result == {
        "available_ambulances": 2,
        "active_hospitals": 3,
        "available_beds": 15,
        "available_rescue_teams": 1
    }
    assert fake_db.closed is True


def test_check_resource_availability_when_all_resources_available(monkeypatch):
    monkeypatch.setattr(
        resource_agent,
        "get_resource_summary",
        lambda: {
            "available_ambulances": 2,
            "active_hospitals": 3,
            "available_beds": 10,
            "available_rescue_teams": 4
        }
    )

    result = resource_agent.check_resource_availability(required_beds=5)

    assert result == {
        "ambulance_available": True,
        "hospital_available": True,
        "rescue_team_available": True,
        "all_resources_available": True
    }


def test_check_resource_availability_when_beds_are_insufficient(monkeypatch):
    monkeypatch.setattr(
        resource_agent,
        "get_resource_summary",
        lambda: {
            "available_ambulances": 2,
            "active_hospitals": 1,
            "available_beds": 2,
            "available_rescue_teams": 1
        }
    )

    result = resource_agent.check_resource_availability(required_beds=5)

    assert result["ambulance_available"] is True
    assert result["hospital_available"] is False
    assert result["rescue_team_available"] is True
    assert result["all_resources_available"] is False
