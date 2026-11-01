import os
import json
from dotenv import load_dotenv
from google import genai
from pathlib import Path
import time
import base64
from groq import Groq
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


# Read Groq API key.
GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
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

Provide the emergency response recommendation as VALID JSON ONLY.

Use exactly this structure:

{{
    "summary": "Brief emergency situation summary",
    "predicted_demand": 0,
    "recommended_ambulance": "AMB-XXXX",
    "recommended_hospital": "Hospital name",
    "recommended_rescue_team": "Rescue Team name",
    "route_distance_km": 0,
    "estimated_travel_time_minutes": 0,
    "immediate_action": "Practical immediate recommended action"
}}

Important rules:

- Return ONLY valid JSON.
- Do not use Markdown code fences.
- Do not add explanations before or after the JSON.
- Do not invent information.
- Use only the values provided in the emergency data.
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
                # PARSE GEMINI JSON RESPONSE
        # ----------------------------------------------------

        response_text = response.text.strip()

        try:
            analysis_data = json.loads(
                response_text
            )

            if not isinstance(analysis_data, dict):
                return {
                    "success": False,
                    "error": "Invalid JSON response: expected a JSON object."
                }

        except json.JSONDecodeError as error:
            return {
                "success": False,
                "error": (
                    "Gemini returned invalid JSON: "
                    f"{str(error)}"
                ),
                "raw_response": response_text
            }
        # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

        required_fields = [
            "summary",
            "predicted_demand",
            "recommended_ambulance",
            "recommended_hospital",
            "recommended_rescue_team",
            "route_distance_km",
            "estimated_travel_time_minutes",
            "immediate_action"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in analysis_data
        ]

        if missing_fields:

            return {
                "success": False,
                "error": (
                    "Missing fields in Gemini response: "
                    + ", ".join(missing_fields)
                ),
                "raw_response": response_text
            }

        return {
            "success": True,
            "recommendation": analysis_data,
            "provider": "Gemini"
        }


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
# GEMINI EMERGENCY IMAGE ANALYSIS
# ============================================================

def analyze_emergency_image_with_groq(
    image_path,
    prompt
):
    """
    Analyze an emergency image using Groq Vision.

    Returns the same JSON-compatible structure used by
    the existing emergency image workflow.
    """

    if not GROQ_API_KEY:

        return {
            "success": False,
            "error": "GROQ_API_KEY is missing from .env."
        }


    image_path = Path(image_path)

    if not image_path.exists():

        return {
            "success": False,
            "error": f"Image file not found: {image_path}"
        }


    try:

        # ----------------------------------------------------
        # READ IMAGE
        # ----------------------------------------------------

        with open(
            image_path,
            "rb"
        ) as image_file:

            image_bytes = image_file.read()


        # ----------------------------------------------------
        # CONVERT IMAGE TO BASE64
        # ----------------------------------------------------

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")


        # ----------------------------------------------------
        # DETECT IMAGE MIME TYPE
        # ----------------------------------------------------

        suffix = image_path.suffix.lower()

        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp"
        }

        mime_type = mime_types.get(
            suffix,
            "image/jpeg"
        )


        # ----------------------------------------------------
        # CREATE GROQ CLIENT
        # ----------------------------------------------------

        client = Groq(
            api_key=GROQ_API_KEY
        )


        # ----------------------------------------------------
        # GROQ VISION REQUEST
        # ----------------------------------------------------

        response = client.chat.completions.create(

            model="qwen/qwen3.8-27b",

            messages=[

                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url": (
                                    f"data:{mime_type};base64,"
                                    f"{image_base64}"
                                )
                            }
                        }

                    ]
                }

            ],

            temperature=0
        )


        # ----------------------------------------------------
        # READ RESPONSE
        # ----------------------------------------------------

        if not response.choices:

            return {
                "success": False,
                "error": "Groq Vision returned no choices."
            }


        response_text = (
            response.choices[0]
            .message
            .content
        )

        if not response_text:

            return {
                "success": False,
                "error": "Groq Vision returned an empty response."
            }

        response_text = response_text.strip()


        # ----------------------------------------------------
        # REMOVE MARKDOWN JSON CODE FENCES
        # ----------------------------------------------------

        if response_text.startswith("```"):

            response_text = response_text.replace(
                "```json",
                "",
                1
            )

            response_text = response_text.replace(
                "```",
                "",
                1
            )

            response_text = response_text.strip()


        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            analysis_data = json.loads(
                response_text
            )

        except json.JSONDecodeError as parse_error:

            return {
                "success": False,
                "error": (
                    "Groq Vision returned invalid JSON: "
                    f"{str(parse_error)}"
                ),
                "raw_response": response_text
            }


                # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

        required_fields = [
            "incident_type",
            "severity",
            "possible_victims",
            "vehicles_detected",
            "visible_hazards",
            "description",
            "confidence"
        ]

        if not isinstance(analysis_data, dict):
            return {
                "success": False,
                "error": "Invalid JSON response: expected a JSON object.",
                "raw_response": response_text
            }

        missing_fields = [
            field
            for field in required_fields
            if field not in analysis_data
        ]

        if missing_fields:
            return {
                "success": False,
                "error": (
                    "Missing fields in Groq response: "
                    + ", ".join(missing_fields)
                ),
                "raw_response": response_text
            }

        print(
            "Groq Vision analysis succeeded."
        )

        return {
            "success": True,
            "analysis": analysis_data,
            "provider": "Groq"
        }

    except Exception as error:
        return {
            "success": False,
            "error": (
                f"Groq Vision API error: {str(error)}"
            ),
            "error_type": "api_error"
        }


def analyze_emergency_image(
    image_path
):
    """
    Analyze an emergency image.

    Primary provider:
        Gemini Vision

    Fallback provider:
        Groq Vision

    The function keeps the existing response structure so
    the dashboard can continue using the same result.
    """

    # --------------------------------------------------------
    # CHECK IMAGE FILE
    # --------------------------------------------------------

    image_path = Path(image_path)

    if not image_path.exists():

        return {
            "success": False,
            "error": f"Image file not found: {image_path}"
        }


    # --------------------------------------------------------
    # CREATE COMMON VISION PROMPT
    # --------------------------------------------------------

    prompt = """
You are an AI Emergency Image Analysis Assistant.

Analyze the uploaded emergency image carefully.

Identify only information that can reasonably be observed
from the image.

Return ONLY valid JSON.

Use exactly this structure:

{
    "incident_type": "Road Accident",
    "severity": "High",
    "possible_victims": 2,
    "vehicles_detected": 3,
    "visible_hazards": [
        "Damaged vehicle",
        "Road obstruction"
    ],
    "description": "Brief description of the visible emergency.",
    "confidence": 85
}

Rules:

1. Do not invent information.

2. For possible_victims, estimate only people who may actually be
   victims of the emergency.

3. Do NOT count police officers, rescuers, or ordinary bystanders
   as victims unless there is visible evidence that they are injured.

4. If a victim cannot be reliably identified from the image, use 0.

5. possible_victims must always be a numeric integer.

6. severity must be one of:
   Low, Medium, High, Critical, Unknown.

7. vehicles_detected must be an estimated visible count.

8. confidence must be a number between 0 and 100.

9. visible_hazards must be a JSON list.

10. Keep description concise.

11. Return ONLY JSON.

12. Do not use Markdown code fences.
"""


    # --------------------------------------------------------
    # TRY GEMINI FIRST
    # --------------------------------------------------------

    if GEMINI_API_KEY:

        try:

            client = genai.Client(
                api_key=GEMINI_API_KEY
            )


            # ------------------------------------------------
            # UPLOAD IMAGE
            # ------------------------------------------------

            uploaded_file = client.files.upload(
                file=image_path
            )


            # ------------------------------------------------
            # GEMINI MODEL FALLBACK
            # ------------------------------------------------

            models_to_try = [
                "gemini-3.8-flash",
                "gemini-3.7-flash"
            ]


            for model_name in models_to_try:

                try:

                    response = client.models.generate_content(

                        model=model_name,

                        contents=[
                            uploaded_file,
                            prompt
                        ]

                    )


                    if not getattr(
                        response,
                        "text",
                        None
                    ):

                        print(
                            f"Gemini Vision {model_name} "
                            "returned an empty response."
                        )

                        continue


                    response_text = (
                        response.text.strip()
                    )


                    # ----------------------------------------
                    # PARSE GEMINI JSON
                    # ----------------------------------------

                    try:

                        analysis_data = json.loads(
                            response_text
                        )

                    except json.JSONDecodeError as parse_error:

                        print(
                            f"Gemini Vision {model_name} "
                            f"returned invalid JSON: {parse_error}"
                        )

                        continue


                                        # ----------------------------------------
                    # VALIDATE GEMINI FIELDS
                    # ----------------------------------------

                    required_fields = [
                        "incident_type",
                        "severity",
                        "possible_victims",
                        "vehicles_detected",
                        "visible_hazards",
                        "description",
                        "confidence"
                    ]

                    if not isinstance(analysis_data, dict):
                        print(
                            f"Gemini Vision {model_name} "
                            "returned invalid JSON: "
                            "expected a JSON object."
                        )
                        continue

                    missing_fields = [
                        field
                        for field in required_fields
                        if field not in analysis_data
                    ]

                    if missing_fields:
                        print(
                            f"Gemini Vision {model_name} "
                            "missing fields: "
                            + ", ".join(missing_fields)
                        )
                        continue

                    print(
                        "Gemini Vision analysis succeeded "
                        f"with {model_name}."
                    )

                    return {
                        "success": True,
                        "analysis": analysis_data,
                        "provider": "Gemini"
                    }

                except Exception as error:
                    error_message = str(error)

                    is_quota_error = (
                        "429" in error_message
                        or "RESOURCE_EXHAUSTED" in error_message
                        or "quota" in error_message.lower()
                        or "rate limit" in error_message.lower()
                    )

                    is_temporary_error = (
                        "503" in error_message
                        or "UNAVAILABLE" in error_message
                        or "high demand" in error_message.lower()
                    )

                    if is_quota_error:
                        print(
                            f"Gemini Vision {model_name} "
                            "quota/rate limit reached. "
                            "Moving to fallback."
                        )
                        break

                    if is_temporary_error:
                        print(
                            f"Gemini Vision {model_name} "
                            "temporarily unavailable."
                        )
                        continue

                    print(
                        f"Gemini Vision {model_name} "
                        f"error: {error_message}"
                    )
                    break

        except Exception as error:
            print(
                "Gemini Vision initialization/upload failed: "
                f"{str(error)}"
            )

    else:
        print(
            "GEMINI_API_KEY is missing. "
            "Skipping Gemini Vision."
        )

    # --------------------------------------------------------
    # GEMINI FAILED -> GROQ FALLBACK
    # --------------------------------------------------------
    print(
        "Using Groq Vision fallback."
    )


    groq_result = analyze_emergency_image_with_groq(
        image_path,
        prompt
    )


    if groq_result.get("success"):

        return groq_result


    # --------------------------------------------------------
    # BOTH PROVIDERS FAILED
    # --------------------------------------------------------

    return {
        "success": False,
        "error": (
            "Gemini Vision and Groq Vision both failed. "
            f"Groq error: {groq_result.get('error', 'Unknown error')}"
        ),
        "error_type": "vision_providers_failed"
    }

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
