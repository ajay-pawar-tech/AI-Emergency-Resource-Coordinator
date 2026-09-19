import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

# Get the project root directory.
BASE_DIR = Path(__file__).resolve().parents[2]

# Path to the .env file.
ENV_FILE = BASE_DIR / ".env"


# Load environment variables.
load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# Read Gemini API key.
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# ============================================================
# BASIC CONFIGURATION LOG
# ============================================================

print(
    "ENV file exists:",
    ENV_FILE.exists()
)

print(
    "Gemini key length:",
    len(GEMINI_API_KEY)
    if GEMINI_API_KEY
    else 0
)


# ============================================================
# FALLBACK RESPONSE
# ============================================================

def generate_fallback_response(
    emergency_data,
    reason="Gemini API unavailable."
):
    """
    Generate a rule-based emergency recommendation
    when Gemini is unavailable.
    """

    ambulance = emergency_data.get(
        "ambulance"
    )

    ambulance_distance = emergency_data.get(
        "ambulance_distance_km"
    )

    hospital = emergency_data.get(
        "hospital"
    )

    hospital_distance = emergency_data.get(
        "hospital_distance_km"
    )

    available_beds = emergency_data.get(
        "available_beds",
        0
    )

    rescue_team = emergency_data.get(
        "rescue_team"
    )

    rescue_team_type = emergency_data.get(
        "rescue_team_type"
    )

    rescue_team_distance = emergency_data.get(
        "rescue_team_distance_km"
    )

    route_distance = emergency_data.get(
        "route_distance_km"
    )

    travel_time = emergency_data.get(
        "estimated_travel_time_minutes"
    )

    incident_type = emergency_data.get(
        "incident_type",
        "Emergency"
    )

    severity = emergency_data.get(
        "severity",
        "Unknown"
    )

    predicted_demand = emergency_data.get(
        "predicted_demand"
    )


    # --------------------------------------------------------
    # BUILD RECOMMENDATION
    # --------------------------------------------------------

    recommendation = f"""
### Emergency Response Recommendation

**1. Emergency Situation Summary**

- **Incident Type:** {incident_type}
- **Severity:** {severity}

**2. Predicted Demand**

- **Demand Value:** {predicted_demand}

**3. Recommended Ambulance**

- **Unit:** {ambulance if ambulance else "No ambulance available"}
- **Distance:** {
    f"{ambulance_distance:.2f} km"
    if ambulance_distance is not None
    else "N/A"
}

**4. Recommended Hospital**

- **Facility:** {hospital if hospital else "No suitable hospital available"}
- **Distance:** {
    f"{hospital_distance:.2f} km"
    if hospital_distance is not None
    else "N/A"
}
- **Available Beds:** {available_beds}

**5. Recommended Rescue Team**

- **Unit:** {rescue_team if rescue_team else "No rescue team available"}
- **Type:** {rescue_team_type if rescue_team_type else "N/A"}
- **Distance:** {
    f"{rescue_team_distance:.2f} km"
    if rescue_team_distance is not None
    else "N/A"
}

**6. Route Distance and Estimated Travel Time**

- **Route Distance:** {
    f"{route_distance:.2f} km"
    if route_distance is not None
    else "N/A"
}
- **Estimated Travel Time:** {
    f"{travel_time:.2f} minutes"
    if travel_time is not None
    else "N/A"
}

**7. Immediate Recommended Action**

- Dispatch the recommended ambulance to the incident location.
- Dispatch the available rescue team when appropriate.
- Notify the selected hospital to prepare for incoming patient(s).
- Use the calculated emergency route for response.

> **Fallback Mode:** {reason}
"""

    return recommendation


# ============================================================
# GEMINI EMERGENCY RESPONSE
# ============================================================

def generate_emergency_response(
    emergency_data
):
    """
    Generate an AI emergency recommendation using Gemini.

    If Gemini is unavailable or quota is exceeded,
    automatically return a rule-based fallback response.
    """

    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    if not GEMINI_API_KEY:

        return generate_fallback_response(
            emergency_data,
            "GEMINI_API_KEY is missing from .env."
        )


    try:

        # ----------------------------------------------------
        # CREATE GEMINI CLIENT
        # ----------------------------------------------------

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )


        # ----------------------------------------------------
        # CREATE PROMPT
        # ----------------------------------------------------

        prompt = f"""
You are an AI Emergency Response Coordinator.

Analyze the following emergency response information:

{emergency_data}

Provide a concise emergency response recommendation.

Include:

1. Emergency situation summary
2. Predicted demand
3. Recommended ambulance
4. Recommended hospital
5. Recommended rescue team
6. Route distance and estimated travel time
7. Immediate recommended action

Important rules:

- Do not invent information.
- Use only the values provided.
- Keep the recommendation practical and concise.
- Consider weather information when it is provided.
"""


        # ----------------------------------------------------
        # GEMINI REQUEST
        # ----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # ----------------------------------------------------
        # VALIDATE RESPONSE
        # ----------------------------------------------------

        if response is None:

            return generate_fallback_response(
                emergency_data,
                "Gemini returned no response."
            )


        if not getattr(
            response,
            "text",
            None
        ):

            return generate_fallback_response(
                emergency_data,
                "Gemini returned an empty response."
            )


        # ----------------------------------------------------
        # RETURN GEMINI RESPONSE
        # ----------------------------------------------------

        return response.text


    except Exception as error:

        error_message = str(
            error
        )

        # ----------------------------------------------------
        # HANDLE QUOTA ERROR
        # ----------------------------------------------------

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED"
            in error_message
            or "quota"
            in error_message.lower()
            or "rate limit"
            in error_message.lower()
        ):

            return generate_fallback_response(
                emergency_data,
                "Gemini API quota/rate limit exceeded."
            )


        # ----------------------------------------------------
        # HANDLE OTHER API ERRORS
        # ----------------------------------------------------

        return generate_fallback_response(
            emergency_data,
            f"Gemini API error: {error_message}"
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    # Sample emergency data.
    test_data = {

        "incident_type":
            "Road Accident",

        "severity":
            "Medium",

        "predicted_demand":
            1.0,

        "ambulance":
            "AMB-1042",

        "ambulance_distance_km":
            1.17,

        "hospital":
            "Sunrise Hospital",

        "hospital_distance_km":
            2.73,

        "available_beds":
            162,

        "rescue_team":
            "Rescue Team 27",

        "rescue_team_type":
            "Flood Rescue",

        "rescue_team_distance_km":
            3.2,

        "route_distance_km":
            1.43,

        "estimated_travel_time_minutes":
            1.71
    }


    # Generate recommendation.
    result = generate_emergency_response(
        test_data
    )


    print(
        "\n===== Gemini Emergency Recommendation ====="
    )

    print(
        result
    )