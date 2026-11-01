import sys
from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]


# Add the project root to Python path.
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


# ============================================================
# IMPORT AGENTS AND SERVICES
# ============================================================

from app.agents.incident_agent import (
    get_incident_summary,
    get_latest_incident
)

from app.agents.victim_agent import (
    get_victim_summary
)

from app.agents.hospital_agent import (
    get_hospital_summary
)

from app.agents.resource_agent import (
    get_resource_summary
)

from app.agents.forecast_agent import (
    forecast_emergency_demand
)

from app.agents.optimization_agent import (
    optimize_emergency_resources
)

from app.agents.route_agent import (
    get_emergency_route
)

from app.services.weather_service import (
    get_weather
)

from app.services.llm_service import (
    generate_emergency_response
)

from app.services.notification_service import (
    create_emergency_notification
)


# ============================================================
# MAIN EMERGENCY COORDINATION
# ============================================================

def coordinate_emergency(
    incident_data=None,
    incident_id=None
):
    """
    Execute the complete emergency coordination workflow.

    Data flow:

        SQLite Incident
            ↓
        Incident Summary
            ↓
        Victim Summary
            ↓
        Hospital Summary
            ↓
        Resource Summary
            ↓
        ML Demand Forecast
            ↓
        Resource Optimization
            ↓
        Route Calculation
            ↓
        Weather
            ↓
        Gemini / Fallback
            ↓
        Emergency Notification
    """


    # ========================================================
    # GET LATEST ACTIVE INCIDENT
    # ========================================================

    # --------------------------------------------------------
    # LOAD INCIDENT
    # --------------------------------------------------------

    if incident_id is not None:
        from app.database.db import SessionLocal
        from app.database.repositories.incident_repository import IncidentRepository

        db = SessionLocal()

        try:
            latest_incident = IncidentRepository.get_by_id(
                db,
                incident_id
            )

            if latest_incident is None:
                raise RuntimeError(
                    f"Incident #{incident_id} was not found in the database."
                )

        finally:
            db.close()

    else:
        latest_incident = get_latest_incident()


    # --------------------------------------------------------
    # STOP WHEN NO INCIDENT EXISTS
    # --------------------------------------------------------

    if latest_incident is None:

        raise RuntimeError(
            "No active emergency incident found in the database."
        )


    # ========================================================
    # AI IMAGE INCIDENT DATA
    # ========================================================

    if incident_data:

        detected_incident_type = incident_data.get(
            "incident_type",
            "Road Accident"
        )

        detected_severity = incident_data.get(
            "severity",
            "Medium"
        )

        detected_victims = incident_data.get(
            "victims",
            0
        )

    else:

        detected_incident_type = None
        detected_severity = None
        detected_victims = None


    # ========================================================
    # INCIDENT INFORMATION
    # ========================================================

    incident_type = (
        detected_incident_type
        if detected_incident_type
        else latest_incident.incident_type
    )

    severity = (
        detected_severity
        if detected_severity
        else latest_incident.severity
    )

    city = (
        latest_incident.city
    )

    location = (
        latest_incident.location
    )

    emergency_latitude = (
        latest_incident.latitude
    )

    emergency_longitude = (
        latest_incident.longitude
    )

    victims = (
        detected_victims
        if detected_victims is not None
        else (latest_incident.victims or 0)
    )

    critical_victims = (
        latest_incident.critical_victims
        or 0
    )


    # ========================================================
    # VALIDATE INCIDENT COORDINATES
    # ========================================================

    if (
        emergency_latitude is None
        or emergency_longitude is None
    ):

        raise RuntimeError(
            "The latest incident does not contain valid coordinates."
        )


    # ========================================================
    # INCIDENT SUMMARY
    # ========================================================

    incident_summary = (
        get_incident_summary()
    )


    # ========================================================
    # VICTIM SUMMARY
    # ========================================================

    victim_summary = (
        get_victim_summary()
    )


    # ========================================================
    # HOSPITAL SUMMARY
    # ========================================================

    hospital_summary = (
        get_hospital_summary()
    )


    # ========================================================
    # RESOURCE SUMMARY
    # ========================================================

    resource_summary = (
        get_resource_summary()
    )


    # ========================================================
    # DATABASE-DRIVEN DEMAND FORECAST
    # ========================================================

    # IMPORTANT:
    # Do not pass fixed lag values here.
    #
    # forecast_emergency_demand() now calculates:
    #
    # day_of_week
    # day_of_month
    # month
    # week_of_year
    # lag_1
    # lag_7
    # rolling_7
    #
    # using the incident history stored in SQLite.

    demand_forecast = (
        forecast_emergency_demand()
    )


    # ========================================================
    # WEATHER
    # ========================================================

    weather_data = (
        get_weather(city)
    )


    # ========================================================
    # REQUIRED HOSPITAL BEDS
    # ========================================================

    # At least one bed is required.
    #
    # For multiple victims, use the victim count as the
    # requested bed requirement.
    #
    # Keep it at minimum 1.

    try:
        required_beds = max(
            1,
            int(victims)
        )
    except (TypeError, ValueError):
        required_beds = 1


    # ========================================================
    # RESOURCE OPTIMIZATION
    # ========================================================

    optimized_resources = (
    optimize_emergency_resources(
        emergency_latitude,
        emergency_longitude,
        required_beds=required_beds,
        incident_type=incident_type
    )
)


    # ========================================================
    # GET SELECTED AMBULANCE
    # ========================================================

    ambulance = (
        optimized_resources.get(
            "ambulance"
        )
    )


    # ========================================================
    # GET SELECTED HOSPITAL
    # ========================================================

    hospital = (
        optimized_resources.get(
            "hospital"
        )
    )


    # ========================================================
    # GET SELECTED RESCUE TEAM
    # ========================================================

    rescue_team = (
        optimized_resources.get(
            "rescue_team"
        )
    )


    # ========================================================
    # EMERGENCY ROUTE
    # ========================================================

    route = None


    if ambulance:

        ambulance_latitude = (
            ambulance.get(
                "latitude"
            )
        )

        ambulance_longitude = (
            ambulance.get(
                "longitude"
            )
        )


        if (
            ambulance_latitude is not None
            and ambulance_longitude is not None
        ):

            route = get_emergency_route(

                ambulance_latitude,

                ambulance_longitude,

                emergency_latitude,

                emergency_longitude
            )


    # ========================================================
    # PREPARE EMERGENCY DATA FOR GEMINI
    # ========================================================

    emergency_data = {

        # ----------------------------------------------------
        # INCIDENT
        # ----------------------------------------------------

        "incident_id":
            latest_incident.id,

        "incident_type":
            incident_type,

        "severity":
            severity,

        "city":
            city,

        "location":
            location,

        "victims":
            victims,

        "critical_victims":
            critical_victims,


        # ----------------------------------------------------
        # DEMAND
        # ----------------------------------------------------

        "predicted_demand":
            demand_forecast,


        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        "weather":
            weather_data,


        # ----------------------------------------------------
        # AMBULANCE
        # ----------------------------------------------------

        "ambulance":
            (
                ambulance.get(
                    "vehicle_number"
                )
                if ambulance
                else None
            ),

        "ambulance_distance_km":
            (
                round(
                    ambulance.get(
                        "distance_km"
                    ),
                    2
                )
                if ambulance
                and ambulance.get(
                    "distance_km"
                ) is not None
                else None
            ),


        # ----------------------------------------------------
        # HOSPITAL
        # ----------------------------------------------------

        "hospital":
            (
                hospital.get(
                    "name"
                )
                if hospital
                else None
            ),

        "hospital_distance_km":
            (
                round(
                    hospital.get(
                        "distance_km"
                    ),
                    2
                )
                if hospital
                and hospital.get(
                    "distance_km"
                ) is not None
                else None
            ),

        "available_beds":
            (
                hospital.get(
                    "available_beds",
                    0
                )
                if hospital
                else 0
            ),


        # ----------------------------------------------------
        # RESCUE TEAM
        # ----------------------------------------------------

        "rescue_team":
            (
                rescue_team.get(
                    "team_name"
                )
                if rescue_team
                else None
            ),

        "rescue_team_type":
            (
                rescue_team.get(
                    "team_type"
                )
                if rescue_team
                else None
            ),

        "rescue_team_distance_km":
            (
                round(
                    rescue_team.get(
                        "distance_km"
                    ),
                    2
                )
                if rescue_team
                and rescue_team.get(
                    "distance_km"
                ) is not None
                else None
            ),


        # ----------------------------------------------------
        # ROUTE
        # ----------------------------------------------------

        "route_distance_km":
            (
                round(
                    route.get(
                        "distance_km"
                    ),
                    2
                )
                if route
                and route.get(
                    "distance_km"
                ) is not None
                else None
            ),

        "estimated_travel_time_minutes":
            (
                round(
                    route.get(
                        "time_minutes"
                    ),
                    2
                )
                if route
                and route.get(
                    "time_minutes"
                ) is not None
                else None
            )
    }


    # ========================================================
    # GEMINI / FALLBACK RECOMMENDATION
    # ========================================================

    gemini_recommendation = (
        generate_emergency_response(
            emergency_data
        )
    )


    # ========================================================
    # EMERGENCY NOTIFICATION
    # ========================================================

    notification = (
        create_emergency_notification(

            incident_type=incident_type,

            severity=severity,

            ambulance=ambulance,

            hospital=hospital,

            rescue_team=rescue_team,

            route=route,

            gemini_recommendation=(
                gemini_recommendation
            )
        )
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        # ----------------------------------------------------
        # DATABASE SUMMARIES
        # ----------------------------------------------------

        "incident_summary":
            incident_summary,

        "victim_summary":
            victim_summary,

        "hospital_summary":
            hospital_summary,

        "resource_summary":
            resource_summary,


        # ----------------------------------------------------
        # ML FORECAST
        # ----------------------------------------------------

        "demand_forecast":
            demand_forecast,


        # ----------------------------------------------------
        # WEATHER
        # ----------------------------------------------------

        "weather":
            weather_data,


        # ----------------------------------------------------
        # OPTIMIZATION
        # ----------------------------------------------------

        "optimized_resources":
            optimized_resources,


        # ----------------------------------------------------
        # ROUTE
        # ----------------------------------------------------

        "route":
            route,


        # ----------------------------------------------------
        # AI
        # ----------------------------------------------------

        "gemini_recommendation":
            gemini_recommendation,


        # ----------------------------------------------------
        # NOTIFICATION
        # ----------------------------------------------------

        "notification":
            notification,


        # ----------------------------------------------------
        # CURRENT INCIDENT
        # ----------------------------------------------------

        "current_incident": {

            "id":
                latest_incident.id,

            "incident_type":
                incident_type,

            "severity":
                severity,

            "city":
                city,

            "location":
                location,

            "latitude":
                emergency_latitude,

            "longitude":
                emergency_longitude,

            "victims":
                victims,

            "critical_victims":
                critical_victims,

            "status":
                latest_incident.status
        }
    }


# ============================================================
# PRINT RESULT (CONSOLE OUTPUT)
# ============================================================

def print_emergency_result(
    result
):
    """
    Print the emergency coordination result in the console.
    """


    # ========================================================
    # SYSTEM HEADER
    # ========================================================

    print(
        "======================================"
    )

    print(
        "   AI EMERGENCY COORDINATION SYSTEM"
    )

    print(
        "======================================"
    )


    # ========================================================
    # CURRENT INCIDENT
    # ========================================================

    current = result[
        "current_incident"
    ]


    print(
        "\n===== CURRENT INCIDENT ====="
    )


    print(
        "Incident ID:",
        current["id"]
    )


    print(
        "Incident:",
        current["incident_type"]
    )


    print(
        "Severity:",
        current["severity"]
    )


    print(
        "City:",
        current["city"]
    )


    print(
        "Location:",
        current["location"]
    )


    print(
        "Victims:",
        current["victims"]
    )


    print(
        "Critical Victims:",
        current["critical_victims"]
    )


    # ========================================================
    # INCIDENT SUMMARY
    # ========================================================

    print(
        "\n===== INCIDENT INFORMATION ====="
    )


    print(
        "Total Incidents:",
        result[
            "incident_summary"
        ][
            "total_incidents"
        ]
    )


    print(
        "Active Incidents:",
        result[
            "incident_summary"
        ].get(
            "active_incidents",
            0
        )
    )


    # ========================================================
    # VICTIM SUMMARY
    # ========================================================

    print(
        "\n===== VICTIM INFORMATION ====="
    )


    print(
        "Total Victims:",
        result[
            "victim_summary"
        ][
            "total_victims"
        ]
    )


    print(
        "Critical Victims:",
        result[
            "victim_summary"
        ].get(
            "critical_victims",
            0
        )
    )


    print(
        "Non-Critical Victims:",
        result[
            "victim_summary"
        ].get(
            "non_critical_victims",
            0
        )
    )


    # ========================================================
    # HOSPITAL SUMMARY
    # ========================================================

    print(
        "\n===== HOSPITAL INFORMATION ====="
    )


    print(
        "Total Hospitals:",
        result[
            "hospital_summary"
        ].get(
            "total_hospitals",
            0
        )
    )


    print(
        "Active Hospitals:",
        result[
            "hospital_summary"
        ].get(
            "active_hospitals",
            0
        )
    )


    print(
        "Available Beds:",
        result[
            "hospital_summary"
        ].get(
            "available_beds",
            0
        )
    )


    # ========================================================
    # RESOURCE SUMMARY
    # ========================================================

    print(
        "\n===== RESOURCE INFORMATION ====="
    )


    print(
        "Available Ambulances:",
        result[
            "resource_summary"
        ].get(
            "available_ambulances",
            0
        )
    )


    print(
        "Available Rescue Teams:",
        result[
            "resource_summary"
        ].get(
            "available_rescue_teams",
            0
        )
    )


    # ========================================================
    # DEMAND FORECAST
    # ========================================================

    print(
        "\n===== DEMAND FORECAST ====="
    )


    print(
        "Predicted Emergency Demand:",
        round(
            result[
                "demand_forecast"
            ],
            2
        )
    )


    # ========================================================
    # SELECTED AMBULANCE
    # ========================================================

    print(
        "\n===== SELECTED AMBULANCE ====="
    )


    selected_ambulance = (
        result[
            "optimized_resources"
        ].get(
            "ambulance"
        )
    )


    if selected_ambulance:

        print(
            "Vehicle:",
            selected_ambulance[
                "vehicle_number"
            ]
        )

        print(
            "Distance:",
            round(
                selected_ambulance[
                    "distance_km"
                ],
                2
            ),
            "km"
        )

    else:

        print(
            "No ambulance available."
        )


    # ========================================================
    # SELECTED HOSPITAL
    # ========================================================

    print(
        "\n===== SELECTED HOSPITAL ====="
    )


    selected_hospital = (
        result[
            "optimized_resources"
        ].get(
            "hospital"
        )
    )


    if selected_hospital:

        print(
            "Hospital:",
            selected_hospital[
                "name"
            ]
        )

        print(
            "Available Beds:",
            selected_hospital[
                "available_beds"
            ]
        )

        print(
            "Distance:",
            round(
                selected_hospital[
                    "distance_km"
                ],
                2
            ),
            "km"
        )

    else:

        print(
            "No suitable hospital available."
        )


    # ========================================================
    # SELECTED RESCUE TEAM
    # ========================================================

    print(
        "\n===== SELECTED RESCUE TEAM ====="
    )


    selected_rescue_team = (
        result[
            "optimized_resources"
        ].get(
            "rescue_team"
        )
    )


    if selected_rescue_team:

        print(
            "Team:",
            selected_rescue_team[
                "team_name"
            ]
        )

        print(
            "Team Type:",
            selected_rescue_team[
                "team_type"
            ]
        )

        print(
            "Distance:",
            round(
                selected_rescue_team[
                    "distance_km"
                ],
                2
            ),
            "km"
        )

    else:

        print(
            "No rescue team available."
        )


    # ========================================================
    # ROUTE
    # ========================================================

    print(
        "\n===== EMERGENCY ROUTE ====="
    )


    if result["route"]:

        print(
            "Distance:",
            round(
                result[
                    "route"
                ][
                    "distance_km"
                ],
                2
            ),
            "km"
        )


        print(
            "Estimated Travel Time:",
            round(
                result[
                    "route"
                ][
                    "time_minutes"
                ],
                2
            ),
            "minutes"
        )

    else:

        print(
            "Route unavailable."
        )


    # ========================================================
    # AI RECOMMENDATION
    # ========================================================

    print(
        "\n===== AI EMERGENCY RECOMMENDATION ====="
    )


    print(
        result[
            "gemini_recommendation"
        ]
    )


    # ========================================================
    # NOTIFICATION
    # ========================================================

    print(
        "\n===== EMERGENCY NOTIFICATION ====="
    )


    print(
        result[
            "notification"
        ]
    )


    # ========================================================
    # COMPLETION
    # ========================================================

    print(
        "\n======================================"
    )

    print(
        "       COORDINATION COMPLETED"
    )

    print(
        "======================================"
    )


# ============================================================
# RUN FILE DIRECTLY
# ============================================================

if __name__ == "__main__":
    result = coordinate_emergency()
    print_emergency_result(result)
