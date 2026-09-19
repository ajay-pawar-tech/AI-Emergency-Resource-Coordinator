import math


# ============================================================
# DATABASE IMPORTS
# ============================================================

from app.database.db import SessionLocal
from app.database.models import Ambulance


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate the geographic distance between two coordinates
    using the Haversine formula.
    """

    # Convert degrees to radians.
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [
            lat1,
            lon1,
            lat2,
            lon2
        ]
    )

    # Calculate coordinate differences.
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine calculation.
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    # Angular distance.
    c = 2 * math.asin(
        math.sqrt(a)
    )

    # Earth radius in kilometers.
    earth_radius_km = 6371

    return earth_radius_km * c


# ============================================================
# FIND NEAREST AVAILABLE AMBULANCE
# ============================================================

def find_nearest_ambulance(
    emergency_latitude,
    emergency_longitude
):
    """
    Find the nearest available ambulance from SQLite.
    """

    db = SessionLocal()

    try:

        # Get all available ambulances.
        ambulances = (
            db.query(Ambulance)
            .filter(
                Ambulance.status.ilike("available")
            )
            .all()
        )

        # No ambulance available.
        if not ambulances:

            return None


        nearest_ambulance = None

        nearest_distance = float(
            "inf"
        )


        # Calculate distance for every ambulance.
        for ambulance in ambulances:

            # Skip ambulances without coordinates.
            if (
                ambulance.latitude is None
                or ambulance.longitude is None
            ):
                continue


            distance = calculate_distance(
                emergency_latitude,
                emergency_longitude,
                ambulance.latitude,
                ambulance.longitude
            )


            # Select the closest ambulance.
            if distance < nearest_distance:

                nearest_distance = distance

                nearest_ambulance = ambulance


        # Return None when no valid coordinates exist.
        if nearest_ambulance is None:

            return None


        # Return dictionary in the same structure
        # expected by the existing coordinator.
        return {
            "id": nearest_ambulance.id,

            "ambulance_id":
                nearest_ambulance.id,

            "vehicle_number":
                nearest_ambulance.vehicle_number,

            "vehicle_type":
                nearest_ambulance.vehicle_type,

            "status":
                nearest_ambulance.status,

            "capacity":
                nearest_ambulance.capacity,

            "city":
                nearest_ambulance.city,

            "latitude":
                nearest_ambulance.latitude,

            "longitude":
                nearest_ambulance.longitude,

            "distance_km":
                nearest_distance
        }

    finally:

        # Always close database connection.
        db.close()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    emergency_latitude = 17.3850

    emergency_longitude = 78.4867


    result = find_nearest_ambulance(
        emergency_latitude,
        emergency_longitude
    )


    if result:

        print(
            "===== Nearest Ambulance ====="
        )

        print(
            "Ambulance ID:",
            result["ambulance_id"]
        )

        print(
            "Vehicle Number:",
            result["vehicle_number"]
        )

        print(
            "Status:",
            result["status"]
        )

        print(
            "Capacity:",
            result["capacity"]
        )

        print(
            "Distance:",
            round(
                result["distance_km"],
                2
            ),
            "km"
        )

    else:

        print(
            "No available ambulance found."
        )