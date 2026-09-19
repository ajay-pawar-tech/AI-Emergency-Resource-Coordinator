from pathlib import Path

import pandas as pd

from app.database.db import SessionLocal
from app.database.models import (
    Ambulance,
    Hospital,
    RescueTeam
)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"


# ============================================================
# CSV FILE PATHS
# ============================================================

AMBULANCE_FILE = (
    RAW_DATA_DIR / "ambulances.csv"
)

HOSPITAL_FILE = (
    RAW_DATA_DIR / "hospitals.csv"
)

RESCUE_TEAM_FILE = (
    RAW_DATA_DIR / "rescue_teams.csv"
)


# ============================================================
# DATABASE SESSION
# ============================================================

db = SessionLocal()


try:

    # ========================================================
    # IMPORT AMBULANCES
    # ========================================================

    print(
        "\n===== IMPORTING AMBULANCES ====="
    )

    ambulance_df = pd.read_csv(
        AMBULANCE_FILE
    )

    ambulance_count = 0


    for _, row in ambulance_df.iterrows():

        vehicle_number = str(
            row["vehicle_number"]
        ).strip()


        # Check whether the ambulance already exists.
        existing = (
            db.query(Ambulance)
            .filter(
                Ambulance.vehicle_number
                == vehicle_number
            )
            .first()
        )


        # Skip duplicate ambulance.
        if existing:

            continue


        new_ambulance = Ambulance(

            vehicle_number=vehicle_number,

            vehicle_type="Ambulance",

            latitude=float(
                row["latitude"]
            ),

            longitude=float(
                row["longitude"]
            ),

            city="Hyderabad",

            status=str(
                row["status"]
            ).strip().lower(),

            capacity=int(
                row["capacity"]
            )
        )


        db.add(
            new_ambulance
        )

        ambulance_count += 1


    # ========================================================
    # IMPORT HOSPITALS
    # ========================================================

    print(
        "\n===== IMPORTING HOSPITALS ====="
    )

    hospital_df = pd.read_csv(
        HOSPITAL_FILE
    )

    hospital_count = 0


    for _, row in hospital_df.iterrows():

        hospital_name = str(
            row["name"]
        ).strip()


        # Check whether hospital already exists.
        existing = (
            db.query(Hospital)
            .filter(
                Hospital.name
                == hospital_name
            )
            .first()
        )


        # Skip duplicate hospital.
        if existing:

            continue


        new_hospital = Hospital(

            name=hospital_name,

            city="Hyderabad",

            latitude=float(
                row["latitude"]
            ),

            longitude=float(
                row["longitude"]
            ),

            total_beds=int(
                row["total_beds"]
            ),

            available_beds=int(
                row["available_beds"]
            ),

            status=str(
                row["status"]
            ).strip().lower()
        )


        db.add(
            new_hospital
        )

        hospital_count += 1


    # ========================================================
    # IMPORT RESCUE TEAMS
    # ========================================================

    print(
        "\n===== IMPORTING RESCUE TEAMS ====="
    )

    rescue_df = pd.read_csv(
        RESCUE_TEAM_FILE
    )

    rescue_count = 0


    for _, row in rescue_df.iterrows():

        team_name = str(
            row["team_name"]
        ).strip()


        # Check whether the rescue team already exists.
        existing = (
            db.query(RescueTeam)
            .filter(
                RescueTeam.team_name
                == team_name
            )
            .first()
        )


        # Skip duplicate team.
        if existing:

            continue


        new_rescue_team = RescueTeam(

            team_name=team_name,

            team_type=str(
                row["team_type"]
            ).strip(),

            members=int(
                row["members"]
            ),

            latitude=float(
                row["latitude"]
            ),

            longitude=float(
                row["longitude"]
            ),

            city="Hyderabad",

            status=str(
                row["status"]
            ).strip().lower()
        )


        db.add(
            new_rescue_team
        )

        rescue_count += 1


    # ========================================================
    # COMMIT DATA
    # ========================================================

    db.commit()


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "      DATABASE SEEDING COMPLETED"
    )

    print(
        "======================================"
    )

    print(
        "Ambulances Imported:",
        ambulance_count
    )

    print(
        "Hospitals Imported:",
        hospital_count
    )

    print(
        "Rescue Teams Imported:",
        rescue_count
    )

    print(
        "======================================"
    )


except Exception as error:

    # Roll back all changes if anything fails.
    db.rollback()

    print(
        "\n======================================"
    )

    print(
        "      DATABASE SEEDING FAILED"
    )

    print(
        "======================================"
    )

    print(
        "Error:",
        error
    )


finally:

    # Always close the database session.
    db.close()