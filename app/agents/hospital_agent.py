from app.database.db import SessionLocal
from app.database.models import Hospital


# ============================================================
# GET ACTIVE HOSPITALS
# ============================================================

def get_active_hospitals():
    """
    Return all active hospitals from SQLite database.
    """

    db = SessionLocal()

    try:

        hospitals = (
            db.query(Hospital)
            .filter(
                Hospital.status.ilike("active")
            )
            .order_by(
                Hospital.id.desc()
            )
            .all()
        )

        return hospitals

    finally:

        db.close()


# ============================================================
# FIND HOSPITALS WITH REQUIRED BEDS
# ============================================================

def find_hospitals_with_beds(
    required_beds=1
):
    """
    Return active hospitals having at least
    the required number of available beds.
    """

    db = SessionLocal()

    try:

        hospitals = (
            db.query(Hospital)
            .filter(
                Hospital.status.ilike("active"),
                Hospital.available_beds >= required_beds
            )
            .order_by(
                Hospital.available_beds.desc()
            )
            .all()
        )

        return hospitals

    finally:

        db.close()


# ============================================================
# GET HOSPITAL SUMMARY
# ============================================================

def get_hospital_summary():
    """
    Get hospital statistics from SQLite database.
    """

    db = SessionLocal()

    try:

        # Load all hospitals.
        hospitals = (
            db.query(Hospital)
            .all()
        )


        # Total hospitals.
        total_hospitals = len(
            hospitals
        )


        # Active hospitals.
        active_hospitals = sum(
            1
            for hospital in hospitals
            if str(
                hospital.status
            ).lower() == "active"
        )


        # Total beds.
        total_beds = sum(
            hospital.total_beds or 0
            for hospital in hospitals
        )


        # Available beds.
        available_beds = sum(
            hospital.available_beds or 0
            for hospital in hospitals
        )


        # Hospitals having at least 2 beds.
        hospitals_with_2_beds = sum(
            1
            for hospital in hospitals
            if (hospital.available_beds or 0) >= 2
        )


        # Hospitals having any available bed.
        hospitals_with_beds = sum(
            1
            for hospital in hospitals
            if (hospital.available_beds or 0) > 0
        )


        return {

            "total_hospitals":
                total_hospitals,

            "active_hospitals":
                active_hospitals,

            "total_beds":
                total_beds,

            "available_beds":
                available_beds,

            "hospitals_with_2_beds":
                hospitals_with_2_beds,

            "hospitals_with_beds":
                hospitals_with_beds
        }

    finally:

        db.close()


# ============================================================
# GET HOSPITAL BY ID
# ============================================================

def get_hospital_by_id(
    hospital_id
):
    """
    Return a hospital by database ID.
    """

    db = SessionLocal()

    try:

        hospital = (
            db.query(Hospital)
            .filter(
                Hospital.id == hospital_id
            )
            .first()
        )

        return hospital

    finally:

        db.close()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # HOSPITAL SUMMARY
    # --------------------------------------------------------

    summary = get_hospital_summary()


    print(
        "===== Hospital Summary ====="
    )


    print(
        "Total Hospitals:",
        summary["total_hospitals"]
    )


    print(
        "Active Hospitals:",
        summary["active_hospitals"]
    )


    print(
        "Total Beds:",
        summary["total_beds"]
    )


    print(
        "Total Available Beds:",
        summary["available_beds"]
    )


    print(
        "Hospitals with at least 2 beds:",
        summary["hospitals_with_2_beds"]
    )


    # --------------------------------------------------------
    # ACTIVE HOSPITALS
    # --------------------------------------------------------

    active_hospitals = (
        get_active_hospitals()
    )


    print(
        "\nActive Hospital Records:",
        len(active_hospitals)
    )


    # --------------------------------------------------------
    # HOSPITALS WITH 2 BEDS
    # --------------------------------------------------------

    suitable_hospitals = (
        find_hospitals_with_beds(
            required_beds=2
        )
    )


    print(
        "Hospitals with at least 2 available beds:",
        len(suitable_hospitals)
    )


    # --------------------------------------------------------
    # DISPLAY FIRST HOSPITAL
    # --------------------------------------------------------

    if active_hospitals:

        hospital = active_hospitals[0]

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
            "City:",
            hospital.city
        )

        print(
            "Status:",
            hospital.status
        )

        print(
            "Total Beds:",
            hospital.total_beds
        )

        print(
            "Available Beds:",
            hospital.available_beds
        )

    else:

        print(
            "\nNo active hospitals found."
        )