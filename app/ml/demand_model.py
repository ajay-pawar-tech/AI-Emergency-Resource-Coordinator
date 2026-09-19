import joblib
import pandas as pd
from pathlib import Path


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Define the path of the saved demand forecasting model.
MODEL_PATH = (
    BASE_DIR
    / "app"
    / "ml"
    / "models"
    / "demand_model.pkl"
)


# Check whether the trained model file exists.
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Demand model not found at: {MODEL_PATH}"
    )


# Load the trained Random Forest Regressor model.
model = joblib.load(MODEL_PATH)


# Predict the number of emergency incidents.
def predict_demand(
    day_of_week,
    day_of_month,
    month,
    week_of_year,
    lag_1,
    lag_7,
    rolling_7
):

    # Create a DataFrame using the same feature names used during training.
    input_data = pd.DataFrame([{
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "month": month,
        "week_of_year": week_of_year,
        "lag_1": lag_1,
        "lag_7": lag_7,
        "rolling_7": rolling_7
    }])

    # Generate the emergency demand prediction.
    prediction = model.predict(input_data)

    # Return the predicted demand value.
    return prediction[0]


# Test the demand forecasting model when this file is executed directly.
if __name__ == "__main__":

    # Provide example historical demand features for testing.
    result = predict_demand(
        day_of_week=1,
        day_of_month=18,
        month=8,
        week_of_year=34,
        lag_1=2,
        lag_7=1,
        rolling_7=1.5
    )

    # Display the predicted number of emergency incidents.
    print("Predicted Emergency Demand:", round(result, 2))