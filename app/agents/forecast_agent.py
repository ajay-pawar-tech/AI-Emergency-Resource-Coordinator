from datetime import datetime, timedelta, timezone

from app.database.db import SessionLocal
from app.database.models import Incident

from app.ml.demand_model import predict_demand


# ============================================================
# GET DAILY INCIDENT COUNT
# ============================================================

def get_daily_incident_count(target_date):
    """
    Count incidents created on a specific date.
    """

    db = SessionLocal()

    try:

        start_datetime = datetime(
            target_date.year,
            target_date.month,
            target_date.day,
        )

        end_datetime = (
            start_datetime
            + timedelta(days=1)
        )

        count = (
            db.query(Incident)
            .filter(
                Incident.created_at >= start_datetime,
                Incident.created_at < end_datetime,
            )
            .count()
        )

        return count

    finally:

        db.close()


# ============================================================
# GET INCIDENT HISTORY
# ============================================================

def get_incident_history():
    """
    Return daily incident counts from SQLite.

    Example:
        {
            date(2026, 8, 30): 1,
            date(2026, 8, 29): 2,
            ...
        }
    """

    db = SessionLocal()

    try:

        incidents = (
            db.query(Incident)
            .order_by(
                Incident.created_at.asc()
            )
            .all()
        )

        history = {}

        for incident in incidents:

            if not incident.created_at:
                continue

            date_key = (
                incident.created_at.date()
            )

            history[date_key] = (
                history.get(
                    date_key,
                    0
                )
                + 1
            )

        return history

    finally:

        db.close()


# ============================================================
# GET LAST OBSERVED DATE
# ============================================================

def get_latest_incident_date():
    """
    Return the latest date available in the incident database.

    Returns None when no incident exists.
    """

    db = SessionLocal()

    try:

        latest_incident = (
            db.query(Incident)
            .filter(
                Incident.created_at.isnot(None)
            )
            .order_by(
                Incident.created_at.desc()
            )
            .first()
        )

        if latest_incident is None:
            return None

        return latest_incident.created_at.date()

    finally:

        db.close()


# ============================================================
# GET DEFAULT FORECAST DATE
# ============================================================

def get_default_forecast_date():
    """
    Forecast the next day after the latest
    available historical incident date.

    This is more meaningful than forecasting a date
    for which no recent historical observations exist.
    """

    latest_date = get_latest_incident_date()

    if latest_date is not None:

        return (
            latest_date
            + timedelta(days=1)
        )

    # Fallback when database contains no history.
    return datetime.now(
        timezone.utc
    ).date()


# ============================================================
# CALCULATE FORECAST FEATURES
# ============================================================

def calculate_forecast_features(
    target_date=None
):
    """
    Calculate the seven features required by
    the trained demand model.

    Features:

        day_of_week
        day_of_month
        month
        week_of_year
        lag_1
        lag_7
        rolling_7

    The target date defaults to the day immediately
    after the latest available historical date.
    """

    # ========================================================
    # TARGET DATE
    # ========================================================

    if target_date is None:

        target_date = (
            get_default_forecast_date()
        )


    # ========================================================
    # DATE FEATURES
    # ========================================================

    day_of_week = (
        target_date.weekday()
    )

    day_of_month = (
        target_date.day
    )

    month = (
        target_date.month
    )

    week_of_year = (
        target_date.isocalendar().week
    )


    # ========================================================
    # LOAD HISTORY
    # ========================================================

    history = (
        get_incident_history()
    )


    # ========================================================
    # LAG 1
    # ========================================================

    yesterday = (
        target_date
        - timedelta(days=1)
    )

    lag_1 = history.get(
        yesterday,
        0
    )


    # ========================================================
    # LAG 7
    # ========================================================

    seven_days_ago = (
        target_date
        - timedelta(days=7)
    )

    lag_7 = history.get(
        seven_days_ago,
        0
    )


    # ========================================================
    # ROLLING 7
    # ========================================================

    rolling_start = (
        target_date
        - timedelta(days=7)
    )

    recent_counts = []

    current_date = rolling_start


    while current_date < target_date:

        recent_counts.append(
            history.get(
                current_date,
                0
            )
        )

        current_date += timedelta(
            days=1
        )


    if recent_counts:

        rolling_7 = (
            sum(recent_counts)
            / len(recent_counts)
        )

    else:

        rolling_7 = 0.0


    # ========================================================
    # RETURN FEATURES
    # ========================================================

    return {

        "day_of_week":
            day_of_week,

        "day_of_month":
            day_of_month,

        "month":
            month,

        "week_of_year":
            week_of_year,

        "lag_1":
            lag_1,

        "lag_7":
            lag_7,

        "rolling_7":
            rolling_7,
    }


# ============================================================
# FORECAST EMERGENCY DEMAND
# ============================================================

def forecast_emergency_demand(
    day_of_week=None,
    day_of_month=None,
    month=None,
    week_of_year=None,
    lag_1=None,
    lag_7=None,
    rolling_7=None,
    target_date=None,
):
    """
    Generate emergency demand forecast.

    When feature values are not supplied,
    they are automatically calculated from SQLite history.
    """

    # ========================================================
    # AUTO-CALCULATE FEATURES
    # ========================================================

    if (
        day_of_week is None
        or day_of_month is None
        or month is None
        or week_of_year is None
        or lag_1 is None
        or lag_7 is None
        or rolling_7 is None
    ):

        features = (
            calculate_forecast_features(
                target_date=target_date
            )
        )

        day_of_week = (
            features["day_of_week"]
        )

        day_of_month = (
            features["day_of_month"]
        )

        month = (
            features["month"]
        )

        week_of_year = (
            features["week_of_year"]
        )

        lag_1 = (
            features["lag_1"]
        )

        lag_7 = (
            features["lag_7"]
        )

        rolling_7 = (
            features["rolling_7"]
        )


    # ========================================================
    # ML MODEL
    # ========================================================

    predicted_demand = predict_demand(

        day_of_week=day_of_week,

        day_of_month=day_of_month,

        month=month,

        week_of_year=week_of_year,

        lag_1=lag_1,

        lag_7=lag_7,

        rolling_7=rolling_7,
    )


    return float(
        predicted_demand
    )


# ============================================================
# GET FORECAST DETAILS
# ============================================================

def get_forecast_details(
    target_date=None
):
    """
    Return forecast date,
    calculated features,
    and predicted demand.
    """

    if target_date is None:

        target_date = (
            get_default_forecast_date()
        )


    features = (
        calculate_forecast_features(
            target_date=target_date
        )
    )


    prediction = predict_demand(

        day_of_week=features[
            "day_of_week"
        ],

        day_of_month=features[
            "day_of_month"
        ],

        month=features[
            "month"
        ],

        week_of_year=features[
            "week_of_year"
        ],

        lag_1=features[
            "lag_1"
        ],

        lag_7=features[
            "lag_7"
        ],

        rolling_7=features[
            "rolling_7"
        ],
    )


    return {

        "target_date":
            target_date,

        "features":
            features,

        "predicted_demand":
            float(prediction),
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "      EMERGENCY DEMAND FORECAST"
    )

    print(
        "======================================"
    )


    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    result = (
        get_forecast_details()
    )


    # --------------------------------------------------------
    # FORECAST DATE
    # --------------------------------------------------------

    print(
        "\n===== FORECAST DATE ====="
    )

    print(
        result["target_date"]
    )


    # --------------------------------------------------------
    # FEATURES
    # --------------------------------------------------------

    print(
        "\n===== FORECAST FEATURES ====="
    )

    features = (
        result["features"]
    )


    print(
        "Day of Week:",
        features["day_of_week"]
    )

    print(
        "Day of Month:",
        features["day_of_month"]
    )

    print(
        "Month:",
        features["month"]
    )

    print(
        "Week of Year:",
        features["week_of_year"]
    )

    print(
        "Lag 1:",
        features["lag_1"]
    )

    print(
        "Lag 7:",
        features["lag_7"]
    )

    print(
        "Rolling 7:",
        round(
            features["rolling_7"],
            3
        )
    )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    print(
        "\n===== PREDICTED DEMAND ====="
    )

    print(
        round(
            result["predicted_demand"],
            3
        )
    )


    print(
        "\n======================================"
    )