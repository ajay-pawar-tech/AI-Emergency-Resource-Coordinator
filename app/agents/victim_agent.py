from app.database.db import SessionLocal
from app.database.models import Incident


# ============================================================
# GET INCIDENTS WITH VICTIMS
# ============================================================

def get_incidents_with_victims():
    """
    Return incidents having one or more victims
    from the SQLite database.
    """

    db = SessionLocal()

    try:

        incidents = (
            db.query(Incident)
            .filter(
                Incident.victims > 0
            )
            .order_by(
                Incident.id.desc()
            )
            .all()
        )

        return incidents

    finally:

        db.close()


# ============================================================
# GET VICTIM SUMMARY
# ============================================================

def get_victim_summary():
    """
    Calculate victim statistics from SQLite.
    """

    db = SessionLocal()

    try:

        incidents = (
            db.query(Incident)
            .all()
        )

        total_victims = sum(
            incident.victims or 0
            for incident in incidents
        )

        critical_victims = sum(
            incident.critical_victims or 0
            for incident in incidents
        )

        non_critical_victims = (
            total_victims
            - critical_victims
        )

        incidents_with_victims = sum(
            1
            for incident in incidents
            if (incident.victims or 0) > 0
        )

        return {
            "total_victims": int(total_victims),
            "critical_victims": int(critical_victims),
            "non_critical_victims": int(
                non_critical_victims
            ),
            "incidents_with_victims": int(
                incidents_with_victims
            )
        }

    finally:

        db.close()


# ============================================================
# GET VICTIM COUNT FOR ONE INCIDENT
# ============================================================

def get_victim_count_by_incident(
    incident_id
):
    """
    Return victim information for a specific incident.
    """

    db = SessionLocal()

    try:

        incident = (
            db.query(Incident)
            .filter(
                Incident.id == incident_id
            )
            .first()
        )

        if incident is None:
            return None

        victims = int(
            incident.victims or 0
        )

        critical_victims = int(
            incident.critical_victims or 0
        )

        return {
            "incident_id": incident.id,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "victims": victims,
            "critical_victims": critical_victims,
            "non_critical_victims": (
                victims - critical_victims
            )
        }

    finally:

        db.close()


# ============================================================
# GET LATEST ACTIVE INCIDENT VICTIMS
# ============================================================

def get_latest_incident_victims():
    """
    Return victim information for the latest active incident.
    """

    db = SessionLocal()

    try:

        incident = (
            db.query(Incident)
            .filter(
                Incident.status.ilike("Active")
            )
            .order_by(
                Incident.id.desc()
            )
            .first()
        )

        if incident is None:
            return None

        victims = int(
            incident.victims or 0
        )

        critical_victims = int(
            incident.critical_victims or 0
        )

        return {
            "incident_id": incident.id,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "victims": victims,
            "critical_victims": critical_victims,
            "non_critical_victims": (
                victims - critical_victims
            )
        }

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
        "         VICTIM SUMMARY"
    )

    print(
        "======================================"
    )


    summary = get_victim_summary()


    print(
        "Total Victims:",
        summary["total_victims"]
    )

    print(
        "Critical Victims:",
        summary["critical_victims"]
    )

    print(
        "Non-Critical Victims:",
        summary["non_critical_victims"]
    )

    print(
        "Incidents With Victims:",
        summary["incidents_with_victims"]
    )


    print(
        "\n===== Latest Active Incident Victims ====="
    )


    latest = get_latest_incident_victims()


    if latest:

        print(
            "Incident ID:",
            latest["incident_id"]
        )

        print(
            "Incident Type:",
            latest["incident_type"]
        )

        print(
            "Severity:",
            latest["severity"]
        )

        print(
            "Victims:",
            latest["victims"]
        )

        print(
            "Critical Victims:",
            latest["critical_victims"]
        )

        print(
            "Non-Critical Victims:",
            latest["non_critical_victims"]
        )

    else:

        print(
            "No active incident found."
        )