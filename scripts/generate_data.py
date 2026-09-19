import csv
import random
from pathlib import Path
from datetime import datetime, timedelta


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# CONSTANTS
# --------------------------------------------------

INCIDENT_TYPES = [
    "Flood",
    "Fire",
    "Road Accident",
    "Building Collapse",
    "Medical Emergency",
    "Industrial Accident"
]

CONDITIONS = [
    "Critical",
    "Serious",
    "Moderate",
    "Stable"
]

SEVERITIES = [
    "Low",
    "Medium",
    "High",
    "Critical"
]

HOSPITAL_NAMES = [
    "City Emergency Hospital",
    "Hyderabad General Hospital",
    "Metro Care Hospital",
    "Central Medical Center",
    "Apollo Emergency Center",
    "Sunrise Hospital",
    "LifeCare Hospital",
    "Global Emergency Hospital"
]

RESCUE_TYPES = [
    "Fire Rescue",
    "Flood Rescue",
    "Medical Rescue",
    "Search and Rescue",
    "Disaster Response"
]

STATUSES = [
    "available",
    "busy",
    "maintenance"
]


# Hyderabad approximate area
HYDERABAD_LAT = 17.3850
HYDERABAD_LON = 78.4867


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def random_location():

    latitude = HYDERABAD_LAT + random.uniform(-0.12, 0.12)
    longitude = HYDERABAD_LON + random.uniform(-0.12, 0.12)

    return round(latitude, 6), round(longitude, 6)


def random_date():

    start_date = datetime.now() - timedelta(days=365)

    random_days = random.randint(0, 365)

    random_seconds = random.randint(0, 86400)

    date = start_date + timedelta(
        days=random_days,
        seconds=random_seconds
    )

    return date.strftime("%Y-%m-%d %H:%M:%S")


# --------------------------------------------------
# INCIDENT DATA
# --------------------------------------------------

def generate_incidents(count=500):

    file_path = RAW_DATA_DIR / "incidents.csv"

    incidents = []

    for incident_id in range(1, count + 1):

        incident_type = random.choice(INCIDENT_TYPES)

        latitude, longitude = random_location()

        victims = random.randint(1, 30)

        severity = random.choices(
            SEVERITIES,
            weights=[25, 35, 25, 15]
        )[0]

        weather_condition = random.choice([
            "Clear",
            "Cloudy",
            "Rain",
            "Heavy Rain",
            "Storm"
        ])

        response_time = random.randint(5, 60)

        incidents.append({
            "incident_id": incident_id,
            "incident_type": incident_type,
            "latitude": latitude,
            "longitude": longitude,
            "reported_victims": victims,
            "severity": severity,
            "weather_condition": weather_condition,
            "response_time_minutes": response_time,
            "status": random.choice([
                "active",
                "resolved",
                "in_progress"
            ]),
            "created_at": random_date()
        })

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=incidents[0].keys()
        )

        writer.writeheader()
        writer.writerows(incidents)

    print(f"Created: {file_path}")
    print(f"Incidents: {count}")

    return incidents


# --------------------------------------------------
# VICTIM DATA
# --------------------------------------------------

def generate_victims(incidents, count=1500):

    file_path = RAW_DATA_DIR / "victims.csv"

    victims = []

    for victim_id in range(1, count + 1):

        incident = random.choice(incidents)

        age = random.randint(1, 85)

        condition = random.choice(CONDITIONS)

        if condition == "Critical":
            priority = 1

        elif condition == "Serious":
            priority = 2

        elif condition == "Moderate":
            priority = 3

        else:
            priority = 4

        latitude = incident["latitude"] + random.uniform(
            -0.002,
            0.002
        )

        longitude = incident["longitude"] + random.uniform(
            -0.002,
            0.002
        )

        victims.append({
            "victim_id": victim_id,
            "incident_id": incident["incident_id"],
            "age": age,
            "condition": condition,
            "priority": priority,
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6)
        })

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=victims[0].keys()
        )

        writer.writeheader()
        writer.writerows(victims)

    print(f"Created: {file_path}")
    print(f"Victims: {count}")

    return victims


# --------------------------------------------------
# HOSPITAL DATA
# --------------------------------------------------

def generate_hospitals(count=50):

    file_path = RAW_DATA_DIR / "hospitals.csv"

    hospitals = []

    for hospital_id in range(1, count + 1):

        latitude, longitude = random_location()

        total_beds = random.randint(50, 500)

        available_beds = random.randint(
            5,
            total_beds
        )

        emergency_capacity = random.randint(
            5,
            50
        )

        hospitals.append({
            "hospital_id": hospital_id,
            "name": random.choice(HOSPITAL_NAMES),
            "latitude": latitude,
            "longitude": longitude,
            "total_beds": total_beds,
            "available_beds": available_beds,
            "emergency_capacity": emergency_capacity,
            "status": "active"
        })

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=hospitals[0].keys()
        )

        writer.writeheader()
        writer.writerows(hospitals)

    print(f"Created: {file_path}")
    print(f"Hospitals: {count}")

    return hospitals


# --------------------------------------------------
# AMBULANCE DATA
# --------------------------------------------------

def generate_ambulances(count=100):

    file_path = RAW_DATA_DIR / "ambulances.csv"

    ambulances = []

    for ambulance_id in range(1, count + 1):

        latitude, longitude = random_location()

        ambulances.append({
            "ambulance_id": ambulance_id,
            "vehicle_number": f"AMB-{1000 + ambulance_id}",
            "latitude": latitude,
            "longitude": longitude,
            "status": random.choice(STATUSES),
            "capacity": random.choice([1, 2, 3, 4])
        })

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=ambulances[0].keys()
        )

        writer.writeheader()
        writer.writerows(ambulances)

    print(f"Created: {file_path}")
    print(f"Ambulances: {count}")

    return ambulances


# --------------------------------------------------
# RESCUE TEAM DATA
# --------------------------------------------------

def generate_rescue_teams(count=30):

    file_path = RAW_DATA_DIR / "rescue_teams.csv"

    teams = []

    for team_id in range(1, count + 1):

        latitude, longitude = random_location()

        teams.append({
            "team_id": team_id,
            "team_name": f"Rescue Team {team_id}",
            "team_type": random.choice(RESCUE_TYPES),
            "members": random.randint(4, 15),
            "latitude": latitude,
            "longitude": longitude,
            "status": random.choice([
                "available",
                "busy"
            ])
        })

    with open(file_path, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(
            file,
            fieldnames=teams[0].keys()
        )

        writer.writeheader()
        writer.writerows(teams)

    print(f"Created: {file_path}")
    print(f"Rescue Teams: {count}")

    return teams


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\n===================================")
    print(" Emergency Dataset Generator")
    print("===================================\n")

    incidents = generate_incidents(500)

    generate_victims(
        incidents,
        1500
    )

    generate_hospitals(50)

    generate_ambulances(100)

    generate_rescue_teams(30)

    print("\n===================================")
    print(" Dataset generation completed!")
    print("===================================")


if __name__ == "__main__":
    main()