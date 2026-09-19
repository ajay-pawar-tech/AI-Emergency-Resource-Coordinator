import joblib
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml"
    / "models"
    / "severity_model.pkl"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# PREDICT SEVERITY
# --------------------------------------------------

def predict_severity(
    incident_type,
    reported_victims,
    weather_condition,
    response_time_minutes,
    latitude,
    longitude
):

    data = pd.DataFrame({
        "incident_type": [incident_type],
        "reported_victims": [reported_victims],
        "weather_condition": [weather_condition],
        "response_time_minutes": [response_time_minutes],
        "latitude": [latitude],
        "longitude": [longitude]
    })

    prediction = model.predict(data)

    return prediction[0]


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    result = predict_severity(
        incident_type="Flood",
        reported_victims=25,
        weather_condition="Heavy Rain",
        response_time_minutes=20,
        latitude=17.3850,
        longitude=78.4867
    )

    print("Predicted Severity:", result)