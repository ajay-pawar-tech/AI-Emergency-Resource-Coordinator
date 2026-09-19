from sqlalchemy import func

from app.database.db import SessionLocal
from app.database.models import Incident


# ============================================================
# FIND INCIDENTS BY TYPE
# ============================================================

def find_incidents_by_type(
    incident_type
):
    """
    Return incidents matching the given incident type.
    """

    db = SessionLocal()

    try:

        incidents = (
            db.query(Incident)
            .filter(
                Incident.incident_type
                == incident_type
            )
            .order_by(
                Incident.created_at.desc()
            )
            .all()
        )

        return incidents

    finally:

        db.close()


# ============================================================
# INCIDENT SUMMARY
# ============================================================

def get_incident_summary():
    """
    Return overall incident statistics.

    Historical incidents are included in the overall
    database statistics.
    """

    db = SessionLocal()

    try:

        total_incidents = (
            db.query(Incident)
            .count()
        )

        active_incidents = (
            db.query(Incident)
            .filter(
                func.lower(
                    Incident.status
                )
                .in_(
                    [
                        "active",
                        "in_progress"
                    ]
                )
            )
            .count()
        )

        total_victims = (
            db.query(
                func.coalesce(
                    func.sum(
                        Incident.victims
                    ),
                    0
                )
            )
            .scalar()
        )

        incident_types = (
            db.query(
                Incident.incident_type
            )
            .distinct()
            .all()
        )

        incident_type_list = [
            row[0]
            for row in incident_types
            if row[0]
        ]

        flood_incidents = (
            db.query(Incident)
            .filter(
                func.lower(
                    Incident.incident_type
                ).like("%flood%")
            )
            .count()
        )

        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "total_victims": int(
                total_victims or 0
            ),
            "incident_types": incident_type_list,
            "flood_incidents": flood_incidents,
        }

    finally:

        db.close()


# ============================================================
# GET CURRENT OPERATIONAL INCIDENT
# ============================================================

def get_latest_incident():
    """
    Return the current operational emergency incident.

    Historical records imported from incidents.csv use
    location = "Historical Incident" and are excluded.

    Priority:
        1. Active operational incident
        2. In-progress operational incident
        3. Latest operational incident
        4. Final fallback to latest database record
    """

    db = SessionLocal()

    try:

        # ====================================================
        # PRIORITY 1:
        # ACTIVE OPERATIONAL INCIDENT
        # ====================================================

        incident = (
            db.query(Incident)
            .filter(
                Incident.location
                != "Historical Incident",

                func.lower(
                    Incident.status
                ) == "active"
            )
            .order_by(
                Incident.created_at.desc()
            )
            .first()
        )

        if incident is not None:

            return incident


        # ====================================================
        # PRIORITY 2:
        # IN-PROGRESS OPERATIONAL INCIDENT
        # ====================================================

        incident = (
            db.query(Incident)
            .filter(
                Incident.location
                != "Historical Incident",

                func.lower(
                    Incident.status
                ) == "in_progress"
            )
            .order_by(
                Incident.created_at.desc()
            )
            .first()
        )

        if incident is not None:

            return incident


        # ====================================================
        # PRIORITY 3:
        # LATEST OPERATIONAL INCIDENT
        # ====================================================

        incident = (
            db.query(Incident)
            .filter(
                Incident.location
                != "Historical Incident"
            )
            .order_by(
                Incident.created_at.desc()
            )
            .first()
        )

        if incident is not None:

            return incident


        # ====================================================
        # PRIORITY 4:
        # FINAL FALLBACK
        # ====================================================

        return (
            db.query(Incident)
            .order_by(
                Incident.created_at.desc()
            )
            .first()
        )

    finally:

        db.close()


# ============================================================
# GET INCIDENTS BY STATUS
# ============================================================

def get_incidents_by_status(
    status
):
    """
    Return incidents matching a specific status.
    """

    db = SessionLocal()

    try:

        incidents = (
            db.query(Incident)
            .filter(
                func.lower(
                    Incident.status
                )
                == str(status).lower()
            )
            .order_by(
                Incident.created_at.desc()
            )
            .all()
        )

        return incidents

    finally:

        db.close()


# ============================================================
# GET INCIDENT COUNT
# ============================================================

def get_incident_count():
    """
    Return total incident count.
    """

    db = SessionLocal()

    try:

        return (
            db.query(Incident)
            .count()
        )

    finally:

        db.close()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "======================================"
    )

    print(
        "       INCIDENT AGENT TEST"
    )

    print(
        "======================================"
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = (
        get_incident_summary()
    )

    print(
        "\n===== INCIDENT SUMMARY ====="
    )

    print(
        "Total Incidents:",
        summary["total_incidents"]
    )

    print(
        "Active Incidents:",
        summary["active_incidents"]
    )

    print(
        "Total Victims:",
        summary["total_victims"]
    )

    print(
        "Incident Types:",
        summary["incident_types"]
    )

    print(
        "Flood Incidents:",
        summary["flood_incidents"]
    )


    # --------------------------------------------------------
    # CURRENT INCIDENT
    # --------------------------------------------------------

    latest = (
        get_latest_incident()
    )

    print(
        "\n===== CURRENT OPERATIONAL INCIDENT ====="
    )

    if latest:

        print(
            "ID:",
            latest.id
        )

        print(
            "Type:",
            latest.incident_type
        )

        print(
            "Severity:",
            latest.severity
        )

        print(
            "City:",
            latest.city
        )

        print(
            "Location:",
            latest.location
        )

        print(
            "Victims:",
            latest.victims
        )

        print(
            "Critical Victims:",
            latest.critical_victims
        )

        print(
            "Status:",
            latest.status
        )

    else:

        print(
            "No incident found."
        )


    print(
        "\n======================================"
    )