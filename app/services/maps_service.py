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

# Check whether the Geoapify API key was loaded from the .env file.

# Print the length of the API key without exposing the actual key.


# Test the Geoapify geocoding API.
def test_geoapify():

    # Stop execution if the API key is missing.
    if not GEOAPIFY_API_KEY:
        print("ERROR: GEOAPIFY_API_KEY is missing from .env")
        return

    # Define the Geoapify geocoding API endpoint.
    url = "https://api.geoapify.com/v1/geocode/search"

    # Define the parameters required by the API.
    params = {
        "text": "Ameerpet, Hyderabad",
        "format": "json",
        "apiKey": GEOAPIFY_API_KEY
    }

    # Send the API request.
    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    # Display the HTTP status code.
    print("Status Code:", response.status_code)

    # Process a successful API response.
    if response.status_code == 200:

        # Convert the API response into JSON.
        data = response.json()

        # Check whether a location was found.
        if data.get("results"):

            # Get the first matching location.
            result = data["results"][0]

            # Display the location information.
            print("Address:", result.get("formatted"))
            print("Latitude:", result.get("lat"))
            print("Longitude:", result.get("lon"))

        else:

            # Display a message when no location is found.
            print("No location found.")

    else:

        # Display the API error response.
        print("API Error:")
        print(response.text)


# Run the API test when this file is executed directly.
if __name__ == "__main__":
    test_geoapify()