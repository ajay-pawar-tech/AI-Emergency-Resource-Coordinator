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


# Display basic API configuration information.
print("ENV file exists:", ENV_FILE.exists())
print(
    "WEATHER_API_KEY found:",
    "WEATHER_API_KEY" in config
)
print(
    "Weather key length:",
    len(WEATHER_API_KEY) if WEATHER_API_KEY else 0
)


# Get current weather information for a city.
def get_weather(city):

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

            # Convert the API response into JSON data.
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


        # Return the API error when the request fails.
        return {
            "success": False,
            "error": response.text
        }


    except requests.RequestException as e:

        # Return the network error when the API request fails.
        return {
            "success": False,
            "error": str(e)
        }


# Test the weather service directly.
if __name__ == "__main__":

    # Get the current weather for Hyderabad.
    weather = get_weather("Hyderabad")


    # Display the weather information.
    print("\n===== WEATHER INFORMATION =====")


    # Display successful weather data.
    if weather["success"]:

        print("City:", weather["city"])
        print("Temperature:", weather["temperature"], "°C")
        print("Humidity:", weather["humidity"], "%")
        print("Weather:", weather["weather"])
        print("Wind Speed:", weather["wind_speed"], "m/s")


    # Display the API error.
    else:

        print("Weather API Error:")
        print(weather["error"])