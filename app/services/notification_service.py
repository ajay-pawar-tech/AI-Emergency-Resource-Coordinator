
from datetime import datetime


def _get_value(resource, key, default="N/A"):
    """Safely read a value from an optional resource dictionary."""
    if resource is None:
        return default

    if isinstance(resource, dict):
        return resource.get(key, default)

    return default


def _format_distance(resource):
    """Safely format resource distance."""
    distance = _get_value(resource, "distance_km", None)

    try:
        if distance is None:
            return "N/A"

        return f"{float(distance):.2f} km"

    except (TypeError, ValueError):
        return "N/A"


def _format_minutes(resource):
    """Safely format estimated travel time."""
    time_minutes = _get_value(resource, "time_minutes", None)

    try:
        if time_minutes is None:
            return "N/A"

        return f"{float(time_minutes):.2f}"

    except (TypeError, ValueError):
        return "N/A"


def create_emergency_notification(
    incident_type,
    severity,
    ambulance,
    hospital,
    rescue_team,
    route,
    gemini_recommendation
):
    """Create an emergency notification safely."""

    notification_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Format AI recommendation.
    if isinstance(gemini_recommendation, dict):

        if gemini_recommendation.get("success"):

            recommendation_data = gemini_recommendation.get(
                "recommendation",
                gemini_recommendation.get("analysis", {})
            )

            if isinstance(recommendation_data, dict):
                gemini_recommendation = "\n".join(
                    f"{key.replace('_', ' ').title()}: {value}"
                    for key, value in recommendation_data.items()
                )
            else:
                gemini_recommendation = str(recommendation_data)

        else:
            gemini_recommendation = gemini_recommendation.get(
                "error",
                "AI recommendation is unavailable."
            )

    elif gemini_recommendation is None:
        gemini_recommendation = "AI recommendation is unavailable."

    else:
        gemini_recommendation = str(gemini_recommendation)

    # Ambulance information.
    ambulance_section = f"""
----- AMBULANCE -----
Vehicle: {_get_value(ambulance, "vehicle_number", "No ambulance available")}
Distance: {_format_distance(ambulance)}
"""

    # Hospital information.
    hospital_section = f"""
----- HOSPITAL -----
Hospital: {_get_value(hospital, "name", "No suitable hospital available")}
Available Beds: {_get_value(hospital, "available_beds")}
Distance: {_format_distance(hospital)}
"""

    # Rescue team information.
    rescue_section = f"""
----- RESCUE TEAM -----
Team: {_get_value(rescue_team, "team_name", "No rescue team available")}
Team Type: {_get_value(rescue_team, "team_type")}
Distance: {_format_distance(rescue_team)}
"""

    # Route information.
    route_section = f"""
----- EMERGENCY ROUTE -----
Distance: {_format_distance(route)}
Estimated Travel Time: {_format_minutes(route)} minutes
"""

    # Clearly identify unavailable resources.
    warnings = []

    if ambulance is None:
        warnings.append("No ambulance was selected.")

    if hospital is None:
        warnings.append("No suitable hospital was selected.")

    if rescue_team is None:
        warnings.append("No rescue team was selected.")

    if route is None:
        warnings.append("Emergency route is unavailable.")

    warning_section = ""

    if warnings:
        warning_section = (
            "\n----- RESOURCE AVAILABILITY WARNINGS -----\n"
            + "\n".join(f"WARNING: {item}" for item in warnings)
            + "\n"
        )

    # Create final emergency notification.
    notification = f"""
========================================
        🚨 EMERGENCY ALERT
========================================

Time: {notification_time}

Incident Type: {incident_type}
Severity: {severity}

{ambulance_section}

{hospital_section}

{rescue_section}

{route_section}

{warning_section}
----- AI RECOMMENDATION -----
{gemini_recommendation}

========================================
        END EMERGENCY ALERT
========================================
"""

    return notification


# Test the notification service directly.
if __name__ == "__main__":

    sample_notification = create_emergency_notification(
        incident_type="Road Accident",
        severity="Critical",
        ambulance=None,
        hospital=None,
        rescue_team=None,
        route=None,
        gemini_recommendation="Emergency response required."
    )

    print(sample_notification)
