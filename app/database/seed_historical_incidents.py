from pathlib import Path

import pandas as pd

from app.database.db import SessionLocal
from app.database.models import Incident


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CSV_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "incidents.csv"
)


# ============================================================
# HISTORICAL INCIDENT SEEDING
# ============================================================

def seed_historical_incidents():
    """
    Import historical incidents from incidents.csv
    into the SQLite Incident table.

    Existing incidents are preserved.
    Duplicate historical records are skipped.
    """

    # ========================================================
    # CHECK CSV FILE
    # ========================================================

    if not CSV_PATH.exists():

        raise FileNotFoundError(
            f"Historical incident CSV not found:\n{CSV_PATH}"
        )


    print("=" * 60)
    print("       HISTORICAL INCIDENT IMPORT")
    print("=" * 60)


    # ========================================================
    # READ CSV
    # ========================================================

    df = pd.read_csv(
        CSV_PATH
    )


    print(
        f"CSV records found: {len(df)}"
    )


    # ========================================================
    # REQUIRED CSV COLUMNS
    # ========================================================

    required_columns = [
        "incident_id",
        "incident_type",
        "latitude",
        "longitude",
        "reported_victims",
        "severity",
        "weather_condition",
        "response_time_minutes",
        "status",
        "created_at",
    ]


    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]


    if missing_columns:

        raise ValueError(
            "Missing CSV columns: "
            + ", ".join(missing_columns)
        )


    # ========================================================
    # DATABASE SESSION
    # ========================================================

    db = SessionLocal()


    imported_count = 0
    skipped_count = 0


    try:

        # ====================================================
        # LOOP THROUGH HISTORICAL INCIDENTS
        # ====================================================

        for _, row in df.iterrows():

            # ------------------------------------------------
            # CLEAN VALUES
            # ------------------------------------------------

            incident_type = str(
                row["incident_type"]
            ).strip()

            severity = str(
                row["severity"]
            ).strip()

            status = str(
                row["status"]
            ).strip().lower()

            latitude = float(
                row["latitude"]
            )

            longitude = float(
                row["longitude"]
            )

            victims = int(
                row["reported_victims"]
            )

            created_at = pd.to_datetime(
                row["created_at"]
            ).to_pydatetime()


            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            existing = (
                db.query(Incident)
                .filter(
                    Incident.incident_type
                    == incident_type,

                    Incident.latitude
                    == latitude,

                    Incident.longitude
                    == longitude,

                    Incident.victims
                    == victims,

                    Incident.created_at
                    == created_at
                )
                .first()
            )


            # ------------------------------------------------
            # SKIP DUPLICATE
            # ------------------------------------------------

            if existing:

                skipped_count += 1

                continue


            # ------------------------------------------------
            # CREATE INCIDENT
            # ------------------------------------------------

            historical_incident = Incident(

                incident_type=incident_type,

                severity=severity,

                city="Hyderabad",

                location="Historical Incident",

                latitude=latitude,

                longitude=longitude,

                victims=victims,

                # ------------------------------------------------
                # Critical victim count is not available
                # in the CSV.
                # ------------------------------------------------

                critical_victims=0,

                # ------------------------------------------------
                # Store additional historical information
                # inside description.
                # ------------------------------------------------

                description=(
                    "Historical incident imported from "
                    "incidents.csv. "
                    f"Incident ID: {row['incident_id']}. "
                    f"Weather: {row['weather_condition']}. "
                    f"Response Time: "
                    f"{row['response_time_minutes']} minutes."
                ),

                status=status,

                created_at=created_at
            )


            db.add(
                historical_incident
            )

            imported_count += 1


        # ====================================================
        # COMMIT
        # ====================================================

        db.commit()


    except Exception as error:

        # ----------------------------------------------------
        # ROLLBACK WHEN ERROR OCCURS
        # ----------------------------------------------------

        db.rollback()

        print()
        print(
            "Historical incident import failed."
        )

        print(
            "Error:",
            error
        )

        raise


    finally:

        # ====================================================
        # CLOSE DATABASE
        # ====================================================

        db.close()


    # ========================================================
    # IMPORT SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("   HISTORICAL INCIDENT IMPORT COMPLETED")
    print("=" * 60)

    print(
        "CSV Records:",
        len(df)
    )

    print(
        "Imported:",
        imported_count
    )

    print(
        "Skipped Duplicates:",
        skipped_count
    )

    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    seed_historical_incidents()