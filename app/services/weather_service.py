
import requests
from pathlib import Path
from dotenv import dotenv_values


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]

# Define the path of the .env file.
ENV_FILE = BASE_DIR / ".env"

# Read environment variables from the .env file.
config = dotenv_values(ENV_FILE)

# Get the OpenWeather API key.
WEATHER_API_KEY = config.get("WEATHER_API_KEY")


def get_weather(city):
    """Get current weather information for a city."""

    # Stop execution if the API key is missing.
    if not WEATHER_API_KEY:
        return {
            "success": False,
            "error": "WEATHER_API_KEY is empty or missing from .env"
        }

    # Define the OpenWeather current weather API endpoint.
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Define the parameters required by the weather API.
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        # Send the request to the OpenWeather API.
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        # Check whether the API request was successful.
        if response.status_code == 200:
            data = response.json()

            # Return the important weather information.
            return {
                "success": True,
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "weather": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"]
            }

        # Return the API error expected by the existing tests.
        return {
            "success": False,
            "error": response.text
        }

    except requests.RequestException as e:
        # Return the network error expected by the existing tests.
        return {
            "success": False,
            "error": str(e)
        }


# Test the weather service directly.
if __name__ == "__main__":
    weather = get_weather("Hyderabad")

    print("\n===== WEATHER INFORMATION =====")

    if weather["success"]:
        print("City:", weather["city"])
        print("Temperature:", weather["temperature"], "°C")
        print("Humidity:", weather["humidity"], "%")
        print("Weather:", weather["weather"])
        print("Wind Speed:", weather["wind_speed"], "m/s")
    else:
        print("Weather API Error:")
        print(weather["error"])
