
from app.agents import hospital_agent


def test_get_active_hospitals_returns_active_hospitals(
    monkeypatch,
):
    expected_hospitals = [
        {"id": 3, "name": "Hospital C"},
        {"id": 2, "name": "Hospital B"},
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return expected_hospitals

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.get_active_hospitals()

    assert result == expected_hospitals
    assert fake_db.closed is True
def test_find_hospitals_with_beds_returns_matching_hospitals(
    monkeypatch,
):
    expected_hospitals = [
        {"id": 5, "available_beds": 20},
        {"id": 2, "available_beds": 10},
    ]

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return expected_hospitals

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.find_hospitals_with_beds(
        required_beds=5
    )

    assert result == expected_hospitals
    assert fake_db.closed is True
def test_get_hospital_summary_returns_correct_statistics(
    monkeypatch,
):
    from types import SimpleNamespace

    hospitals = [
        SimpleNamespace(
            status="active",
            total_beds=100,
            available_beds=20,
        ),
        SimpleNamespace(
            status="active",
            total_beds=50,
            available_beds=1,
        ),
        SimpleNamespace(
            status="inactive",
            total_beds=30,
            available_beds=0,
        ),
        SimpleNamespace(
            status="active",
            total_beds=None,
            available_beds=None,
        ),
    ]

    class FakeQuery:
        def all(self):
            return hospitals

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.get_hospital_summary()

    assert result == {
        "total_hospitals": 4,
        "active_hospitals": 3,
        "total_beds": 180,
        "available_beds": 21,
        "hospitals_with_2_beds": 1,
        "hospitals_with_beds": 2,
    }

    assert fake_db.closed is True
def test_get_hospital_by_id_returns_hospital(
    monkeypatch,
):
    expected_hospital = {
        "id": 7,
        "name": "Test Hospital",
    }

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return expected_hospital

    class FakeDB:
        closed = False

        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            self.closed = True

    fake_db = FakeDB()

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.get_hospital_by_id(
        hospital_id=7
    )

    assert result == expected_hospital
    assert fake_db.closed is True
def test_get_hospital_by_id_returns_none_when_not_found(
    monkeypatch,
):
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

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.get_hospital_by_id(
        hospital_id=99999
    )

    assert result is None
    assert fake_db.closed is True
def test_get_hospital_by_id_returns_none_when_not_found(
    monkeypatch,
):
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

    monkeypatch.setattr(
        hospital_agent,
        "SessionLocal",
        lambda: fake_db,
    )

    result = hospital_agent.get_hospital_by_id(
        hospital_id=99999
    )

    assert result is None
    assert fake_db.closed is True
