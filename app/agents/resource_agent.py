from app.database.db import SessionLocal

from app.database.models import (
    Ambulance,
    Hospital,
    RescueTeam
)


# ============================================================
# GET AVAILABLE AMBULANCES
# ============================================================

def get_available_ambulances():
    """
    Return all currently available ambulances
    from the SQLite database.
    """

    db = SessionLocal()

    try:

        ambulances = (
            db.query(Ambulance)
            .filter(
                Ambulance.status.ilike("available")
            )
            .order_by(
                Ambulance.id
            )
            .all()
        )

        return ambulances

    finally:

        db.close()


# ============================================================
# GET ACTIVE HOSPITALS
# ============================================================

def get_active_hospitals():
    """
    Return all active hospitals
    from the SQLite database.
    """

    db = SessionLocal()

    try:

        hospitals = (
            db.query(Hospital)
            .filter(
                Hospital.status.ilike("active")
            )
            .order_by(
                Hospital.id
            )
            .all()
        )

        return hospitals

    finally:

        db.close()


# ============================================================
# GET AVAILABLE RESCUE TEAMS
# ============================================================

def get_available_rescue_teams():
    """
    Return all available rescue teams
    from the SQLite database.
    """

    db = SessionLocal()

    try:

        rescue_teams = (
            db.query(RescueTeam)
            .filter(
                RescueTeam.status.ilike("available")
            )
            .order_by(
                RescueTeam.id
            )
            .all()
        )

        return rescue_teams

    finally:

        db.close()


# ============================================================
# GET RESOURCE SUMMARY
# ============================================================

def get_resource_summary():
    """
    Create a complete emergency resource summary
    using SQLite database records.
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # AVAILABLE AMBULANCES
        # ----------------------------------------------------

        available_ambulances = (
            db.query(Ambulance)
            .filter(
                Ambulance.status.ilike("available")
            )
            .all()
        )


        # ----------------------------------------------------
        # ACTIVE HOSPITALS
        # ----------------------------------------------------

        active_hospitals = (
            db.query(Hospital)
            .filter(
                Hospital.status.ilike("active")
            )
            .all()
        )


        # ----------------------------------------------------
        # AVAILABLE RESCUE TEAMS
        # ----------------------------------------------------

        available_rescue_teams = (
            db.query(RescueTeam)
            .filter(
                RescueTeam.status.ilike("available")
            )
            .all()
        )


        # ----------------------------------------------------
        # AVAILABLE HOSPITAL BEDS
        # ----------------------------------------------------

        available_beds = sum(
            hospital.available_beds or 0
            for hospital in active_hospitals
        )


        # ----------------------------------------------------
        # RETURN SUMMARY
        # ----------------------------------------------------

        return {

            "available_ambulances":
                len(
                    available_ambulances
                ),

            "active_hospitals":
                len(
                    active_hospitals
                ),

            "available_beds":
                int(
                    available_beds
                ),

            "available_rescue_teams":
                len(
                    available_rescue_teams
                )
        }

    finally:

        db.close()


# ============================================================
# CHECK RESOURCE AVAILABILITY
# ============================================================

def check_resource_availability(
    required_beds=1
):
    """
    Check whether sufficient emergency resources
    are currently available.
    """

    summary = get_resource_summary()


    # --------------------------------------------------------
    # AMBULANCE
    # --------------------------------------------------------

    ambulance_available = (
        summary["available_ambulances"] > 0
    )


    # --------------------------------------------------------
    # HOSPITAL
    # --------------------------------------------------------

    hospital_available = (
        summary["available_beds"]
        >= required_beds
    )


    # --------------------------------------------------------
    # RESCUE TEAM
    # --------------------------------------------------------

    rescue_team_available = (
        summary["available_rescue_teams"] > 0
    )


    # --------------------------------------------------------
    # ALL RESOURCES
    # --------------------------------------------------------

    all_resources_available = (
        ambulance_available
        and hospital_available
        and rescue_team_available
    )


    return {

        "ambulance_available":
            ambulance_available,

        "hospital_available":
            hospital_available,

        "rescue_team_available":
            rescue_team_available,

        "all_resources_available":
            all_resources_available
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # RESOURCE SUMMARY
    # --------------------------------------------------------

    summary = get_resource_summary()


    print(
        "===== Emergency Resource Summary ====="
    )


    print(
        "Available Ambulances:",
        summary["available_ambulances"]
    )


    print(
        "Active Hospitals:",
        summary["active_hospitals"]
    )


    print(
        "Available Hospital Beds:",
        summary["available_beds"]
    )


    print(
        "Available Rescue Teams:",
        summary["available_rescue_teams"]
    )


    # --------------------------------------------------------
    # RESOURCE AVAILABILITY
    # --------------------------------------------------------

    availability = check_resource_availability(
        required_beds=2
    )


    print(
        "\n===== Resource Availability ====="
    )


    print(
        "Ambulance Available:",
        availability["ambulance_available"]
    )


    print(
        "Hospital Available:",
        availability["hospital_available"]
    )


    print(
        "Rescue Team Available:",
        availability["rescue_team_available"]
    )


    print(
        "All Resources Available:",
        availability["all_resources_available"]
    )


    # --------------------------------------------------------
    # SAMPLE AVAILABLE AMBULANCE
    # --------------------------------------------------------

    ambulances = get_available_ambulances()


    if ambulances:

        ambulance = ambulances[0]

        print(
            "\n===== Sample Available Ambulance ====="
        )

        print(
            "ID:",
            ambulance.id
        )

        print(
            "Vehicle:",
            ambulance.vehicle_number
        )

        print(
            "Status:",
            ambulance.status
        )

        print(
            "Capacity:",
            ambulance.capacity
        )

    else:

        print(
            "\nNo available ambulances found."
        )


    # --------------------------------------------------------
    # SAMPLE ACTIVE HOSPITAL
    # --------------------------------------------------------

    hospitals = get_active_hospitals()


    if hospitals:

        hospital = hospitals[0]

        print(
            "\n===== Sample Active Hospital ====="
        )

        print(
            "ID:",
            hospital.id
        )

        print(
            "Name:",
            hospital.name
        )

        print(
            "Available Beds:",
            hospital.available_beds
        )

        print(
            "Status:",
            hospital.status
        )

    else:

        print(
            "\nNo active hospitals found."
        )


    # --------------------------------------------------------
    # SAMPLE RESCUE TEAM
    # --------------------------------------------------------

    rescue_teams = get_available_rescue_teams()


    if rescue_teams:

        team = rescue_teams[0]

        print(
            "\n===== Sample Available Rescue Team ====="
        )

        print(
            "ID:",
            team.id
        )

        print(
            "Team:",
            team.team_name
        )

        print(
            "Type:",
            team.team_type
        )

        print(
            "Members:",
            team.members
        )

        print(
            "Status:",
            team.status
        )

    else:

        print(
            "\nNo available rescue teams found."
        )