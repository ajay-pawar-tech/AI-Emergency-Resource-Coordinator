from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.optimization.ambulance_optimizer import (
    find_nearest_ambulance
)

from app.optimization.resource_allocator import (
    find_best_hospital,
    find_best_rescue_team
)


def optimize_emergency_resources(
    emergency_latitude,
    emergency_longitude,
    required_beds=1,
    incident_type=None
):
    ambulance = find_nearest_ambulance(
        emergency_latitude,
        emergency_longitude
    )

    hospital = find_best_hospital(
        emergency_latitude,
        emergency_longitude,
        required_beds
    )

    rescue_team = find_best_rescue_team(
        emergency_latitude,
        emergency_longitude,
        incident_type
    )

    return {
        "ambulance": ambulance,
        "hospital": hospital,
        "rescue_team": rescue_team
    }


if __name__ == "__main__":
    emergency_latitude = 17.3850
    emergency_longitude = 78.4867
    required_beds = 2

    result = optimize_emergency_resources(
        emergency_latitude,
        emergency_longitude,
        required_beds
    )

    print("===== Selected Ambulance =====")
    if result["ambulance"]:
        print("Vehicle:", result["ambulance"]["vehicle_number"])
        print("Distance:", round(result["ambulance"]["distance_km"], 2), "km")
    else:
        print("No available ambulance found.")

    print("\n===== Selected Hospital =====")
    if result["hospital"]:
        print("Hospital:", result["hospital"]["name"])
        print("Available Beds:", result["hospital"]["available_beds"])
        print("Distance:", round(result["hospital"]["distance_km"], 2), "km")
    else:
        print("No suitable hospital found.")

    print("\n===== Selected Rescue Team =====")
    if result["rescue_team"]:
        print("Team:", result["rescue_team"]["team_name"])
        print("Team Type:", result["rescue_team"]["team_type"])
        print("Distance:", round(result["rescue_team"]["distance_km"], 2), "km")
    else:
        print("No available rescue team found.")