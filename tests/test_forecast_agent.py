
import pytest
from datetime import date

from app.agents import forecast_agent


def test_calculate_forecast_features_uses_incident_history(monkeypatch):
    target_date = date(2026, 10, 20)

    history = {
        date(2026, 10, 13): 7,
        date(2026, 10, 14): 1,
        date(2026, 10, 15): 2,
        date(2026, 10, 16): 3,
        date(2026, 10, 17): 4,
        date(2026, 10, 18): 5,
        date(2026, 10, 19): 4,
    }

    monkeypatch.setattr(
        forecast_agent,
        "get_incident_history",
        lambda: history,
    )

    features = forecast_agent.calculate_forecast_features(
        target_date=target_date
    )

    assert features["day_of_week"] == target_date.weekday()
    assert features["day_of_month"] == 20
    assert features["month"] == 10
    assert features["week_of_year"] == target_date.isocalendar().week

    assert features["lag_1"] == 4
    assert features["lag_7"] == 7
    assert features["rolling_7"] == pytest.approx(26 / 7)

def test_calculate_forecast_features_with_empty_history(monkeypatch):
    target_date = date(2026, 10, 20)

    monkeypatch.setattr(
        forecast_agent,
        "get_incident_history",
        lambda: {},
    )

    features = forecast_agent.calculate_forecast_features(
        target_date=target_date
    )

    assert features["day_of_month"] == 20
    assert features["month"] == 10
    assert features["lag_1"] == 0
    assert features["lag_7"] == 0
    assert features["rolling_7"] == 0.0

def test_default_forecast_date_is_day_after_latest_incident(monkeypatch):
    latest_date = date(2026, 10, 25)

    monkeypatch.setattr(
        forecast_agent,
        "get_latest_incident_date",
        lambda: latest_date,
    )

    result = forecast_agent.get_default_forecast_date()

    assert result == date(2026, 10, 26)

def test_get_latest_incident_date_returns_none_when_no_incidents(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        forecast_agent,
        "SessionLocal",
        lambda: FakeDB(),
    )

    result = forecast_agent.get_latest_incident_date()

    assert result is None

def test_get_incident_history_counts_incidents_per_day(monkeypatch):
    from datetime import datetime
    from types import SimpleNamespace

    class FakeQuery:
        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return [
                SimpleNamespace(
                    created_at=datetime(2026, 10, 20, 9, 0)
                ),
                SimpleNamespace(
                    created_at=datetime(2026, 10, 20, 15, 0)
                ),
                SimpleNamespace(
                    created_at=datetime(2026, 10, 21, 10, 0)
                ),
                SimpleNamespace(created_at=None),
            ]

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        forecast_agent,
        "SessionLocal",
        lambda: FakeDB(),
    )

    history = forecast_agent.get_incident_history()

    assert history == {
        date(2026, 10, 20): 2,
        date(2026, 10, 21): 1,
    }

def test_get_daily_incident_count_returns_count(monkeypatch):
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def count(self):
            return 3

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        forecast_agent,
        "SessionLocal",
        lambda: FakeDB(),
    )

    result = forecast_agent.get_daily_incident_count(
        date(2026, 10, 20)
    )

    assert result == 3

def test_forecast_emergency_demand_returns_float(monkeypatch):
    monkeypatch.setattr(
        forecast_agent,
        "predict_demand",
        lambda **kwargs: 12.5,
    )

    result = forecast_agent.forecast_emergency_demand(
        day_of_week=1,
        day_of_month=20,
        month=10,
        week_of_year=43,
        lag_1=4,
        lag_7=7,
        rolling_7=3.5,
    )

    assert result == 12.5
    assert isinstance(result, float)
def test_get_forecast_details_returns_expected_data(monkeypatch):
    target_date = date(2026, 10, 20)

    expected_features = {
        "day_of_week": 1,
        "day_of_month": 20,
        "month": 10,
        "week_of_year": 43,
        "lag_1": 4,
        "lag_7": 7,
        "rolling_7": 3.5,
    }

    monkeypatch.setattr(
        forecast_agent,
        "calculate_forecast_features",
        lambda target_date=None: expected_features,
    )

    monkeypatch.setattr(
        forecast_agent,
        "predict_demand",
        lambda **kwargs: 12.5,
    )

    result = forecast_agent.get_forecast_details(target_date)

    assert result["target_date"] == target_date
    assert result["predicted_demand"] == 12.5
def test_default_forecast_date_uses_utc_today_when_no_history(
    monkeypatch,
):
    from datetime import datetime, timezone

    expected_date = date(2026, 10, 26)

    class FakeDateTime:
        @staticmethod
        def now(tz=None):
            assert tz == timezone.utc
            return datetime(
                2026, 10, 26, 12, 0, 0,
                tzinfo=timezone.utc,
            )

    monkeypatch.setattr(
        forecast_agent,
        "get_latest_incident_date",
        lambda: None,
    )

    monkeypatch.setattr(
        forecast_agent,
        "datetime",
        FakeDateTime,
    )

    result = forecast_agent.get_default_forecast_date()

    assert result == expected_date
def test_forecast_emergency_demand_calculates_missing_features(
    monkeypatch,
):
    expected_features = {
        "day_of_week": 1,
        "day_of_month": 20,
        "month": 10,
        "week_of_year": 43,
        "lag_1": 4,
        "lag_7": 7,
        "rolling_7": 3.5,
    }

    monkeypatch.setattr(
        forecast_agent,
        "calculate_forecast_features",
        lambda target_date=None: expected_features,
    )

    captured = {}

    def fake_predict_demand(**kwargs):
        captured.update(kwargs)
        return 15

    monkeypatch.setattr(
        forecast_agent,
        "predict_demand",
        fake_predict_demand,
    )

    result = forecast_agent.forecast_emergency_demand()

    assert result == 15.0
    assert captured == expected_features
def test_get_latest_incident_date_returns_date(monkeypatch):
    from datetime import datetime
    from types import SimpleNamespace

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def first(self):
            return SimpleNamespace(
                created_at=datetime(2026, 10, 25, 14, 30)
            )

    class FakeDB:
        def query(self, *args, **kwargs):
            return FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(
        forecast_agent,
        "SessionLocal",
        lambda: FakeDB(),
    )

    result = forecast_agent.get_latest_incident_date()

    assert result == date(2026, 10, 25)
def test_calculate_forecast_features_uses_default_date(
    monkeypatch,
):
    target_date = date(2026, 10, 26)

    monkeypatch.setattr(
        forecast_agent,
        "get_default_forecast_date",
        lambda: target_date,
    )

    monkeypatch.setattr(
        forecast_agent,
        "get_incident_history",
        lambda: {},
    )

    result = forecast_agent.calculate_forecast_features()

    assert result["day_of_week"] == target_date.weekday()
    assert result["day_of_month"] == target_date.day
    assert result["month"] == target_date.month
    assert result["week_of_year"] == target_date.isocalendar().week
    assert result["lag_1"] == 0
    assert result["lag_7"] == 0
    assert result["rolling_7"] == 0.0
def test_forecast_emergency_demand_passes_target_date(
    monkeypatch,
):
    target_date = date(2026, 10, 26)
    captured = {}

    expected_features = {
        "day_of_week": 0,
        "day_of_month": 26,
        "month": 10,
        "week_of_year": 44,
        "lag_1": 2,
        "lag_7": 5,
        "rolling_7": 3.0,
    }

    def fake_calculate_forecast_features(target_date=None):
        captured["target_date"] = target_date
        return expected_features

    monkeypatch.setattr(
        forecast_agent,
        "calculate_forecast_features",
        fake_calculate_forecast_features,
    )

    monkeypatch.setattr(
        forecast_agent,
        "predict_demand",
        lambda **kwargs: 9,
    )

    result = forecast_agent.forecast_emergency_demand(
        target_date=target_date
    )

    assert result == 9.0
    assert captured["target_date"] == target_date
def test_get_forecast_details_uses_default_date(monkeypatch):
    target_date = date(2026, 10, 26)

    features = {
        "day_of_week": 0,
        "day_of_month": 26,
        "month": 10,
        "week_of_year": 44,
        "lag_1": 2,
        "lag_7": 5,
        "rolling_7": 3.0,
    }

    monkeypatch.setattr(
        forecast_agent,
        "get_default_forecast_date",
        lambda: target_date,
    )
    monkeypatch.setattr(
        forecast_agent,
        "calculate_forecast_features",
        lambda target_date=None: features,
    )
    monkeypatch.setattr(
        forecast_agent,
        "predict_demand",
        lambda **kwargs: 8,
    )

    result = forecast_agent.get_forecast_details()

    assert result["target_date"] == target_date
    assert result["features"] == features
    assert result["predicted_demand"] == 8.0
