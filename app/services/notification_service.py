"""Safe emergency notification formatting for optional resources and AI output."""

from collections.abc import Mapping
from datetime import datetime


def _get_value(item, key, default=None):
    """Read a value from a dictionary-like object or an attribute safely."""
    if item is None:
        return default
    if isinstance(item, Mapping):
        return item.get(key, default)
    return getattr(item, key, default)


def _format_number(value, suffix="", decimals=2):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def _format_resource_distance(item):
    return _format_number(_get_value(item, "distance_km"), " km")


def _format_gemini_recommendation(value):
    """Accept Gemini success/error dictionaries, fallback strings, or None."""
    unavailable = "AI recommendation is unavailable. Follow verified emergency information and dispatcher instructions."

    if value is None:
        return unavailable

    if isinstance(value, str):
        return value.strip() or unavailable

    if not isinstance(value, Mapping):
        return str(value).strip() or unavailable

    # Current LLM service returns {success: True, recommendation: {...}}.
    # On invalid/incomplete model output it can return {success: False, error: ...}.
    if value.get("success") is False:
        error = value.get("error")
        return f"AI recommendation unavailable: {error}" if error else unavailable

    nested = value.get("recommendation")
    if isinstance(nested, str):
        return nested.strip() or unavailable
    if isinstance(nested, Mapping):
        recommendation = nested
    elif nested is None:
        # Also support an already-unwrapped recommendation dictionary.
        if any(
            key in value
            for key in (
                "summary",
                "immediate_action",
                "recommended_ambulance",
                "recommended_hospital",
            )
        ):
            recommendation = value
        else:
            error = value.get("error")
            return f"AI recommendation unavailable: {error}" if error else unavailable
    else:
        return str(nested).strip() or unavailable

    fields = (
        ("Summary", "summary"),
        ("Predicted Demand", "predicted_demand"),
        ("Recommended Ambulance", "recommended_ambulance"),
        ("Recommended Hospital", "recommended_hospital"),
        ("Recommended Rescue Team", "recommended_rescue_team"),
        ("Route Distance", "route_distance_km"),
        ("Estimated Travel Time", "estimated_travel_time_minutes"),
        ("Immediate Action", "immediate_action"),
    )

    lines = []
    for label, key in fields:
        item = recommendation.get(key)
        if item is not None and str(item).strip():
            if key == "route_distance_km":
                item = _format_number(item, " km")
            elif key == "estimated_travel_time_minutes":
                item = _format_number(item, " minutes")
            lines.append(f"{label}: {item}")

    if lines:
        provider = value.get("provider")
        if provider:
            lines.insert(0, f"Provider: {provider}")
        return "\n".join(lines)

    error = value.get("error")
    return f"AI recommendation unavailable: {error}" if error else unavailable


def create_emergency_notification(
    incident_type,
    severity,
    ambulance,
    hospital,
    rescue_team,
    route,
    gemini_recommendation,
):
    """Create a notification without failing when any optional value is None."""
    notification_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ambulance_number = _get_value(
        ambulance, "vehicle_number", "No ambulance available"
    ) or "No ambulance available"

    hospital_name = _get_value(
        hospital, "name", "No suitable hospital available"
    ) or "No suitable hospital available"

    rescue_name = _get_value(
        rescue_team, "team_name", "No rescue team available"
    ) or "No rescue team available"

    rescue_type = _get_value(rescue_team, "team_type", "N/A") or "N/A"
    available_beds = _get_value(hospital, "available_beds", "N/A")
    if available_beds is None:
        available_beds = "N/A"

    route_distance = _format_number(_get_value(route, "distance_km"), " km")
    route_time = _format_number(_get_value(route, "time_minutes"), " minutes")
    ai_text = _format_gemini_recommendation(gemini_recommendation)

    return f"""
========================================
        🚨 EMERGENCY ALERT
========================================

Time: {notification_time}

Incident Type: {incident_type or 'Emergency'}
Severity: {severity or 'Unknown'}

----- AMBULANCE -----
Vehicle: {ambulance_number}
Distance: {_format_resource_distance(ambulance)}

----- HOSPITAL -----
Hospital: {hospital_name}
Available Beds: {available_beds}
Distance: {_format_resource_distance(hospital)}

----- RESCUE TEAM -----
Team: {rescue_name}
Team Type: {rescue_type}
Distance: {_format_resource_distance(rescue_team)}

----- EMERGENCY ROUTE -----
Distance: {route_distance}
Estimated Travel Time: {route_time}

----- AI RECOMMENDATION -----
{ai_text}

========================================
        END EMERGENCY ALERT
========================================
""".strip()


if __name__ == "__main__":
    print(
        create_emergency_notification(
            incident_type="Road Accident",
            severity="High",
            ambulance=None,
            hospital=None,
            rescue_team=None,
            route=None,
            gemini_recommendation=None,
        )
    )
