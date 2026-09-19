import os
import requests
from pathlib import Path
from dotenv import load_dotenv


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Define the path of the .env file.
ENV_FILE = BASE_DIR / ".env"


# Load environment variables from the project .env file.
load_dotenv(dotenv_path=ENV_FILE, override=True)


# Read the Geoapify API key from the environment.
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


# Calculate the driving route between two locations.
def calculate_route(
    ambulance_latitude,
    ambulance_longitude,
    emergency_latitude,
    emergency_longitude
):

    # Stop execution if the API key is missing.
    if not GEOAPIFY_API_KEY:
        print("ERROR: GEOAPIFY_API_KEY is missing from .env")
        return None

    # Define the Geoapify routing API endpoint.
    url = "https://api.geoapify.com/v1/routing"

    # Create the routing parameters.
    params = {
        "waypoints": (
            f"{ambulance_latitude},{ambulance_longitude}|"
            f"{emergency_latitude},{emergency_longitude}"
        ),
        "mode": "drive",
        "apiKey": GEOAPIFY_API_KEY
    }

    # Send the route request to Geoapify.
    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    # Display the API status code.
    print("Status Code:", response.status_code)

    # Stop if the API request failed.
    if response.status_code != 200:
        print("API Error:")
        print(response.text)
        return None

    # Convert the API response into JSON.
    data = response.json()

    # Check whether route information is available.
    if not data.get("features"):
        print("No route found.")
        return None

    # Get the first route from the API response.
    route = data["features"][0]

    # Extract route properties.
    properties = route.get("properties", {})

    # Get route distance in meters.
    distance_meters = properties.get("distance", 0)

    # Get route travel time in seconds.
    time_seconds = properties.get("time", 0)

    # Convert distance from meters to kilometers.
    distance_km = distance_meters / 1000

    # Convert travel time from seconds to minutes.
    time_minutes = time_seconds / 60

    # Return the route information.
    return {
        "distance_km": distance_km,
        "time_minutes": time_minutes
    }


# Test the route optimizer when this file is executed directly.
if __name__ == "__main__":

    # Example ambulance location.
    ambulance_latitude = 17.441949
    ambulance_longitude = 78.374975

    # Example emergency location in Hyderabad.
    emergency_latitude = 17.3850
    emergency_longitude = 78.4867

    # Calculate the driving route.
    result = calculate_route(
        ambulance_latitude,
        ambulance_longitude,
        emergency_latitude,
        emergency_longitude
    )

    # Display the route result.
    if result:

        print("===== Route Information =====")
        print(
            "Distance:",
            round(result["distance_km"], 2),
            "km"
        )
        print(
            "Estimated Travel Time:",
            round(result["time_minutes"], 2),
            "minutes"
        )