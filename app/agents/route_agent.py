import sys
from pathlib import Path


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Add the project root to Python's module search path.
# This allows the agent to import modules from the app package.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# Import the route calculation function.
from app.optimization.route_optimizer import calculate_route


# Calculate the best driving route for an emergency response.
def get_emergency_route(
    ambulance_latitude,
    ambulance_longitude,
    emergency_latitude,
    emergency_longitude
):

    # Calculate the driving route using the Geoapify routing service.
    route = calculate_route(
        ambulance_latitude=ambulance_latitude,
        ambulance_longitude=ambulance_longitude,
        emergency_latitude=emergency_latitude,
        emergency_longitude=emergency_longitude
    )

    # Return the calculated route information.
    return route


# Test the route agent when this file is executed directly.
if __name__ == "__main__":

    # Define the example ambulance location.
    ambulance_latitude = 17.441949
    ambulance_longitude = 78.374975

    # Define the example emergency location.
    emergency_latitude = 17.3850
    emergency_longitude = 78.4867

    # Get the emergency route.
    result = get_emergency_route(
        ambulance_latitude,
        ambulance_longitude,
        emergency_latitude,
        emergency_longitude
    )

    # Display the route information.
    if result:

        print("===== Emergency Route =====")

        # Display the route distance.
        print(
            "Distance:",
            round(result["distance_km"], 2),
            "km"
        )

        # Display the estimated travel time.
        print(
            "Estimated Travel Time:",
            round(result["time_minutes"], 2),
            "minutes"
        )

    else:

        # Display an error when no route is available.
        print("Unable to calculate emergency route.")