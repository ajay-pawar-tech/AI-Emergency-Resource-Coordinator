
import math

from app.ml.demand_model import predict_demand
from app.ml.severity_model import predict_severity


# -------------------------------
# DEMAND MODEL TESTS
# -------------------------------

def test_predict_demand_returns_numeric_value():
    result = predict_demand(
        day_of_week=1,
        day_of_month=18,
        month=8,
        week_of_year=34,
        lag_1=2,
        lag_7=1,
        rolling_7=1.5,
    )

    assert isinstance(result, (int, float))
    assert math.isfinite(float(result))


def test_predict_demand_is_non_negative():
    result = predict_demand(
        day_of_week=1,
        day_of_month=18,
        month=8,
        week_of_year=34,
        lag_1=2,
        lag_7=1,
        rolling_7=1.5,
    )

    assert result >= 0


# -------------------------------
# SEVERITY MODEL TESTS
# -------------------------------

def test_predict_severity_returns_value():
    result = predict_severity(
        incident_type="Flood",
        reported_victims=25,
        weather_condition="Heavy Rain",
        response_time_minutes=20,
        latitude=17.3850,
        longitude=78.4867,
    )

    assert result is not None


def test_predict_severity_is_consistent_for_same_input():
    inputs = {
        "incident_type": "Flood",
        "reported_victims": 25,
        "weather_condition": "Heavy Rain",
        "response_time_minutes": 20,
        "latitude": 17.3850,
        "longitude": 78.4867,
    }

    first_result = predict_severity(**inputs)
    second_result = predict_severity(**inputs)

    assert first_result == second_result
