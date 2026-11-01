import math


# ============================================================
# DATABASE IMPORTS
# ============================================================

from app.database.db import SessionLocal

from app.database.models import (
    Hospital,
    RescueTeam
)


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
    Calculate geographic distance using the Haversine formula.
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

    # Haversine formula.
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

    # Earth's radius in kilometers.
    earth_radius_km = 6371

    return earth_radius_km * c


# ============================================================
# FIND BEST HOSPITAL
# ============================================================

def find_best_hospital(
    emergency_latitude,
    emergency_longitude,
    required_beds=1
):
    """
    Find the nearest active hospital having enough available beds.
    """

    db = SessionLocal()

    try:

        # Get active hospitals with enough beds.
        hospitals = (
            db.query(Hospital)
            .filter(
                Hospital.status.ilike("active"),
                Hospital.available_beds >= required_beds
            )
            .all()
        )


        # No suitable hospital.
        if not hospitals:

            return None


        best_hospital = None

        best_distance = float(
            "inf"
        )


        # Calculate distance for each hospital.
        for hospital in hospitals:

            # Skip invalid coordinates.
            if (
                hospital.latitude is None
                or hospital.longitude is None
            ):
                continue


            distance = calculate_distance(
                emergency_latitude,
                emergency_longitude,
                hospital.latitude,
                hospital.longitude
            )


            # Select nearest suitable hospital.
            if distance < best_distance:

                best_distance = distance

                best_hospital = hospital


        # No hospital had valid coordinates.
        if best_hospital is None:

            return None


        # Return structure expected by coordinator.
        return {
            "id":
                best_hospital.id,

            "hospital_id":
                best_hospital.id,

            "name":
                best_hospital.name,

            "city":
                best_hospital.city,

            "status":
                best_hospital.status,

            "total_beds":
                best_hospital.total_beds,

            "available_beds":
                best_hospital.available_beds,

            "latitude":
                best_hospital.latitude,

            "longitude":
                best_hospital.longitude,

            "distance_km":
                best_distance
        }

    finally:

        db.close()


# ============================================================
# FIND BEST RESCUE TEAM
# ============================================================

def find_best_rescue_team(
    emergency_latitude,
    emergency_longitude,
    incident_type=None
):
    """
    Find the nearest available rescue team.
    """

    # ========================================================
    # INCIDENT TYPE → RESCUE TEAM TYPE MAPPING
    # ========================================================

    rescue_type_mapping = {
        "Road Accident": [
            "Search and Rescue",
            "Medical Rescue"
        ],
        "Fire": [
            "Fire Rescue",
            "Search and Rescue"
        ],
        "Flood": [
            "Flood Rescue",
            "Water Rescue"
        ],
        "Building Collapse": [
            "Search and Rescue",
            "Urban Rescue"
        ],
        "Medical Emergency": [
            "Medical Rescue"
        ]
    }

    required_team_types = rescue_type_mapping.get(
        incident_type,
        []
    )

    db = SessionLocal()

    try:

        # Get available rescue teams.
                # Get available rescue teams.
        query = (
            db.query(RescueTeam)
            .filter(
                RescueTeam.status.ilike("available")
            )
        )

        # Filter rescue teams according to incident type.
        if required_team_types:
            query = query.filter(
                RescueTeam.team_type.in_(
                    required_team_types
                )
            )

        teams = query.all()


        # No team available.
        if not teams:

            return None


        best_team = None

        best_distance = float(
            "inf"
        )


        # Calculate distance for each rescue team.
        for team in teams:

            # Skip invalid coordinates.
            if (
                team.latitude is None
                or team.longitude is None
            ):
                continue


            distance = calculate_distance(
                emergency_latitude,
                emergency_longitude,
                team.latitude,
                team.longitude
            )


            # Select nearest available team.
            if distance < best_distance:

                best_distance = distance

                best_team = team


        # No valid team found.
        if best_team is None:

            return None


        # Return structure expected by coordinator.
        return {
            "id":
                best_team.id,

            "team_id":
                best_team.id,

            "team_name":
                best_team.team_name,

            "team_type":
                best_team.team_type,

            "members":
                best_team.members,

            "city":
                best_team.city,

            "status":
                best_team.status,

            "latitude":
                best_team.latitude,

            "longitude":
                best_team.longitude,

            "distance_km":
                best_distance
        }

    finally:

        db.close()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    emergency_latitude = 17.3850

    emergency_longitude = 78.4867

    required_beds = 2


    # --------------------------------------------------------
    # TEST HOSPITAL
    # --------------------------------------------------------

    hospital = find_best_hospital(
        emergency_latitude,
        emergency_longitude,
        required_beds
    )


    print(
        "===== Best Hospital ====="
    )


    if hospital:

        print(
            "Hospital ID:",
            hospital["hospital_id"]
        )

        print(
            "Hospital Name:",
            hospital["name"]
        )

        print(
            "Status:",
            hospital["status"]
        )

        print(
            "Available Beds:",
            hospital["available_beds"]
        )

        print(
            "Distance:",
            round(
                hospital["distance_km"],
                2
            ),
            "km"
        )

    else:

        print(
            "No suitable hospital found."
        )


    # --------------------------------------------------------
    # TEST RESCUE TEAM
    # --------------------------------------------------------

    rescue_team = find_best_rescue_team(
        emergency_latitude,
        emergency_longitude
    )


    print(
        "\n===== Best Rescue Team ====="
    )


    if rescue_team:

        print(
            "Team ID:",
            rescue_team["team_id"]
        )

        print(
            "Team Name:",
            rescue_team["team_name"]
        )

        print(
            "Team Type:",
            rescue_team["team_type"]
        )

        print(
            "Members:",
            rescue_team["members"]
        )

        print(
            "Status:",
            rescue_team["status"]
        )

        print(
            "Distance:",
            round(
                rescue_team["distance_km"],
                2
            ),
            "km"
        )

    else:

        print(
            "No available rescue team found."
        )