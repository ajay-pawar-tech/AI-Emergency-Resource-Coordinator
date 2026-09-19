from pathlib import Path
import sys


# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Add the project root to Python's module search path.
# This allows the agent to import modules from the app package.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# Import the ambulance optimization function.
from app.optimization.ambulance_optimizer import (
    find_nearest_ambulance
)


# Import the hospital and rescue team allocation functions.
from app.optimization.resource_allocator import (
    find_best_hospital,
    find_best_rescue_team
)


# Find the best emergency resources for a given location.
def optimize_emergency_resources(
    emergency_latitude,
    emergency_longitude,
    required_beds=1
):

    # Find the nearest available ambulance.
    ambulance = find_nearest_ambulance(
        emergency_latitude,
        emergency_longitude
    )

    # Find the nearest suitable hospital.
    hospital = find_best_hospital(
        emergency_latitude,
        emergency_longitude,
        required_beds
    )

    # Find the nearest available rescue team.
    rescue_team = find_best_rescue_team(
        emergency_latitude,
        emergency_longitude
    )

    # Return all selected emergency resources.
    return {
        "ambulance": ambulance,
        "hospital": hospital,
        "rescue_team": rescue_team
    }


# Test the optimization agent when this file is executed directly.
if __name__ == "__main__":

    # Define an example emergency location in Hyderabad.
    emergency_latitude = 17.3850
    emergency_longitude = 78.4867

    # Define the number of hospital beds required.
    required_beds = 2

    # Optimize all emergency resources.
    result = optimize_emergency_resources(
        emergency_latitude,
        emergency_longitude,
        required_beds
    )

    # Display the selected ambulance.
    print("===== Selected Ambulance =====")

    if result["ambulance"]:

        print(
            "Vehicle:",
            result["ambulance"]["vehicle_number"]
        )

        print(
            "Distance:",
            round(
                result["ambulance"]["distance_km"],
                2
            ),
            "km"
        )

    else:

        print("No available ambulance found.")

    # Display the selected hospital.
    print("\n===== Selected Hospital =====")

    if result["hospital"]:

        print(
            "Hospital:",
            result["hospital"]["name"]
        )

        print(
            "Available Beds:",
            result["hospital"]["available_beds"]
        )

        print(
            "Distance:",
            round(
                result["hospital"]["distance_km"],
                2
            ),
            "km"
        )

    else:

        print("No suitable hospital found.")

    # Display the selected rescue team.
    print("\n===== Selected Rescue Team =====")

    if result["rescue_team"]:

        print(
            "Team:",
            result["rescue_team"]["team_name"]
        )

        print(
            "Team Type:",
            result["rescue_team"]["team_type"]
        )

        print(
            "Distance:",
            round(
                result["rescue_team"]["distance_km"],
                2
            ),
            "km"
        )

    else:

        print("No available rescue team found.")