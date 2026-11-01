from datetime import datetime


# Create an emergency notification from the coordination result.
def create_emergency_notification(
    incident_type,
    severity,
    ambulance,
    hospital,
    rescue_team,
    route,
    gemini_recommendation
):

    # Get the current date and time for the notification.
    notification_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    # Format the AI recommendation for the notification.
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
    # Create the emergency notification message.
    notification = f"""
========================================
        🚨 EMERGENCY ALERT
========================================

Time: {notification_time}

Incident Type: {incident_type}
Severity: {severity}

----- AMBULANCE -----
Vehicle: {ambulance["vehicle_number"]}
Distance: {ambulance["distance_km"]:.2f} km

----- HOSPITAL -----
Hospital: {hospital["name"]}
Available Beds: {hospital["available_beds"]}
Distance: {hospital["distance_km"]:.2f} km

----- RESCUE TEAM -----
Team: {rescue_team["team_name"]}
Team Type: {rescue_team["team_type"]}
Distance: {rescue_team["distance_km"]:.2f} km

----- EMERGENCY ROUTE -----
Distance: {route["distance_km"]:.2f} km
Estimated Travel Time: {route["time_minutes"]:.2f} minutes

----- AI RECOMMENDATION -----
{gemini_recommendation}

========================================
        END EMERGENCY ALERT
========================================
"""

    # Return the complete emergency notification.
    return notification


# Test the notification service directly.
if __name__ == "__main__":

    # Create sample ambulance information.
    sample_ambulance = {
        "vehicle_number": "AMB-1042",
        "distance_km": 1.17
    }

    # Create sample hospital information.
    sample_hospital = {
        "name": "Sunrise Hospital",
        "available_beds": 162,
        "distance_km": 2.73
    }

    # Create sample rescue team information.
    sample_rescue_team = {
        "team_name": "Rescue Team 27",
        "team_type": "Flood Rescue",
        "distance_km": 3.20
    }

    # Create sample route information.
    sample_route = {
        "distance_km": 1.43,
        "time_minutes": 1.71
    }

    # Create a sample AI recommendation.
    sample_recommendation = (
        "Dispatch the ambulance and rescue team immediately."
    )

    # Generate the emergency notification.
    notification = create_emergency_notification(
        incident_type="Road Accident",
        severity="Medium",
        ambulance=sample_ambulance,
        hospital=sample_hospital,
        rescue_team=sample_rescue_team,
        route=sample_route,
        gemini_recommendation=sample_recommendation
    )

    # Display the emergency notification.
    print(notification)