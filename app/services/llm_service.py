"""LLM and vision services for the AI Emergency Resource Coordinator.

Gemini is the primary provider for emergency recommendations and image
analysis. Groq Vision is used as the image-analysis fallback.
"""

import base64
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

# Do not overwrite values supplied by the deployment environment.
load_dotenv(dotenv_path=ENV_FILE, override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _strip_json_fence(text):
    """Remove optional Markdown code fences from a model response."""
    if not isinstance(text, str):
        return ""

    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return cleaned


def _parse_json_object(text, provider):
    """Parse a model response and require a JSON object."""
    cleaned = _strip_json_fence(text)
    if not cleaned:
        raise ValueError(f"{provider} returned an empty response.")

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{provider} returned invalid JSON: {exc}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(
            f"{provider} returned invalid JSON: expected a JSON object."
        )

    return parsed


def _missing_fields(data, required_fields):
    return [field for field in required_fields if field not in data]


def _is_rate_limit_error(error):
    message = str(error).lower()
    return (
        "429" in message
        or "rate_limit_exceeded" in message
        or "resource_exhausted" in message
        or "quota" in message
        or "rate limit" in message
    )


def _format_optional_number(value, suffix="", decimals=2):
    """Format a numeric value safely for fallback recommendations."""
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


# ---------------------------------------------------------------------------
# Rule-based emergency recommendation fallback
# ---------------------------------------------------------------------------


def generate_fallback_response(
    emergency_data,
    reason="Gemini API unavailable."
):
    """Generate a rule-based recommendation when Gemini is unavailable."""
    emergency_data = emergency_data or {}

    ambulance = emergency_data.get("ambulance")
    hospital = emergency_data.get("hospital")
    rescue_team = emergency_data.get("rescue_team")

    recommendation = f"""
### Emergency Response Recommendation

**1. Emergency Situation Summary**

- **Incident Type:** {emergency_data.get('incident_type', 'Emergency')}
- **Severity:** {emergency_data.get('severity', 'Unknown')}

**2. Predicted Demand**

- **Demand Value:** {emergency_data.get('predicted_demand', 'N/A')}

**3. Recommended Ambulance**

- **Unit:** {ambulance or 'No ambulance available'}
- **Distance:** {_format_optional_number(emergency_data.get('ambulance_distance_km'), ' km')}

**4. Recommended Hospital**

- **Facility:** {hospital or 'No suitable hospital available'}
- **Distance:** {_format_optional_number(emergency_data.get('hospital_distance_km'), ' km')}
- **Available Beds:** {emergency_data.get('available_beds', 0)}

**5. Recommended Rescue Team**

- **Unit:** {rescue_team or 'No rescue team available'}
- **Type:** {emergency_data.get('rescue_team_type') or 'N/A'}
- **Distance:** {_format_optional_number(emergency_data.get('rescue_team_distance_km'), ' km')}

**6. Route Distance and Estimated Travel Time**

- **Route Distance:** {_format_optional_number(emergency_data.get('route_distance_km'), ' km')}
- **Estimated Travel Time:** {_format_optional_number(emergency_data.get('estimated_travel_time_minutes'), ' minutes')}

**7. Immediate Recommended Action**

- Dispatch a selected ambulance only when one is available.
- Dispatch an available rescue team when appropriate.
- Notify the selected hospital only when a suitable hospital is available.
- Confirm the route before dispatching emergency resources.

> **Fallback Mode:** {reason}
"""

    return recommendation


# ---------------------------------------------------------------------------
# Gemini emergency response recommendation
# ---------------------------------------------------------------------------


def generate_emergency_response(emergency_data):
    """Generate an emergency response recommendation using Gemini.

    Returns the existing project contract:
      * success dict when Gemini returns a valid recommendation
      * fallback recommendation text when Gemini is unavailable
      * error dict for invalid or incomplete model JSON
    """
    emergency_data = emergency_data or {}

    if not GEMINI_API_KEY:
        return generate_fallback_response(
            emergency_data,
            "GEMINI_API_KEY is missing from the environment."
        )

    prompt = f"""
You are an AI Emergency Response Coordinator.

Analyze the following emergency response information:
{json.dumps(emergency_data, ensure_ascii=False, default=str)}

Return ONLY a valid JSON object with exactly these fields:
{{
  "summary": "Brief emergency situation summary",
  "predicted_demand": 0,
  "recommended_ambulance": "AMB-XXXX or No ambulance available",
  "recommended_hospital": "Hospital name or No suitable hospital available",
  "recommended_rescue_team": "Team name or No rescue team available",
  "route_distance_km": 0,
  "estimated_travel_time_minutes": 0,
  "immediate_action": "Practical immediate recommended action"
}}

Rules:
- Return only JSON. Do not use Markdown fences.
- Do not invent a resource that is missing from the supplied data.
- If a resource is unavailable, state that it is unavailable.
- Keep the response practical and concise.
- Consider weather information when it is provided.
"""

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=512,
                temperature=0,
            ),
        )

        response_text = getattr(response, "text", None)
        if not response_text:
            return generate_fallback_response(
                emergency_data,
                "Gemini returned an empty response."
            )

        try:
            analysis_data = _parse_json_object(
                response_text,
                "Gemini"
            )
        except ValueError as exc:
            return {
                "success": False,
                "error": str(exc),
                "raw_response": response_text,
            }

        required_fields = [
            "summary",
            "predicted_demand",
            "recommended_ambulance",
            "recommended_hospital",
            "recommended_rescue_team",
            "route_distance_km",
            "estimated_travel_time_minutes",
            "immediate_action",
        ]
        missing = _missing_fields(analysis_data, required_fields)
        if missing:
            return {
                "success": False,
                "error": (
                    "Missing fields in Gemini response: "
                    + ", ".join(missing)
                ),
                "raw_response": response_text,
            }

        return {
            "success": True,
            "recommendation": analysis_data,
            "provider": "Gemini",
        }

    except Exception as error:
        if _is_rate_limit_error(error):
            reason = "Gemini API quota/rate limit exceeded."
        else:
            reason = f"Gemini API error: {error}"

        return generate_fallback_response(emergency_data, reason)


# ---------------------------------------------------------------------------
# Groq Vision fallback
# ---------------------------------------------------------------------------


def analyze_emergency_image_with_groq(image_path, prompt):
    """Analyze an emergency image with Groq Vision as a fallback provider."""
    if not GROQ_API_KEY:
        return {
            "success": False,
            "error": "GROQ_API_KEY is missing from the environment.",
            "error_type": "missing_api_key",
        }

    image_path = Path(image_path)
    if not image_path.is_file():
        return {
            "success": False,
            "error": f"Image file not found: {image_path}",
            "error_type": "missing_file",
        }

    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(image_path.suffix.lower())
    if mime_type is None:
        return {
            "success": False,
            "error": "Unsupported image type. Use JPG, JPEG, PNG, or WEBP.",
            "error_type": "unsupported_image_type",
        }

    try:
        image_bytes = image_path.read_bytes()
        image_base64 = base64.b64encode(image_bytes).decode("ascii")

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            temperature=0,
            # The free/on-demand OTPM limit in the reported error is 1,000.
            # Keep each response budget well below that per-request ceiling.
            max_completion_tokens=512,
            reasoning_effort="none",
            response_format={"type": "json_object"},
        )

        if not response.choices:
            return {
                "success": False,
                "error": "Groq Vision returned no choices.",
                "error_type": "empty_response",
            }

        response_text = response.choices[0].message.content
        if not response_text:
            return {
                "success": False,
                "error": "Groq Vision returned an empty response.",
                "error_type": "empty_response",
            }

        try:
            analysis_data = _parse_json_object(response_text, "Groq Vision")
        except ValueError as exc:
            return {
                "success": False,
                "error": str(exc),
                "raw_response": response_text,
                "error_type": "invalid_response",
            }

        required_fields = [
            "incident_type",
            "severity",
            "possible_victims",
            "vehicles_detected",
            "visible_hazards",
            "description",
            "confidence",
        ]
        missing = _missing_fields(analysis_data, required_fields)
        if missing:
            return {
                "success": False,
                "error": (
                    "Missing fields in Groq response: "
                    + ", ".join(missing)
                ),
                "raw_response": response_text,
                "error_type": "incomplete_response",
            }

        return {
            "success": True,
            "analysis": analysis_data,
            "provider": "Groq",
        }

    except Exception as error:
        if _is_rate_limit_error(error):
            error_type = "rate_limit_error"
        else:
            error_type = "api_error"

        return {
            "success": False,
            "error": f"Groq Vision API error: {error}",
            "error_type": error_type,
        }


# ---------------------------------------------------------------------------
# Primary image analysis: Gemini, then Groq fallback
# ---------------------------------------------------------------------------


def analyze_emergency_image(image_path):
    """Analyze an uploaded image using Gemini first and Groq as fallback."""
    image_path = Path(image_path)
    if not image_path.is_file():
        return {
            "success": False,
            "error": f"Image file not found: {image_path}",
            "error_type": "missing_file",
        }

    prompt = """
You are an AI Emergency Image Analysis Assistant.
Analyze the uploaded emergency image carefully. Identify only information
that can reasonably be observed from the image.

Return ONLY a valid JSON object with these fields:
{
  "incident_type": "Road Accident",
  "severity": "High",
  "possible_victims": 2,
  "vehicles_detected": 3,
  "visible_hazards": ["Damaged vehicle", "Road obstruction"],
  "description": "Brief description of the visible emergency.",
  "confidence": 85
}

Rules:
1. Do not invent information.
2. Estimate possible_victims only from people who may actually be victims.
3. Do not count police, rescuers, or bystanders as victims unless there is
   visible evidence that they are injured.
4. If victims cannot be reliably identified, use 0.
5. possible_victims and vehicles_detected must be numeric integers.
6. severity must be Low, Medium, High, Critical, or Unknown.
7. confidence must be a number from 0 to 100.
8. visible_hazards must be a JSON list of short strings.
9. Keep description concise.
10. Return only JSON, without Markdown code fences.
"""

    gemini_errors = []

    if GEMINI_API_KEY:
        client = None
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            uploaded_file = client.files.upload(file=image_path)

            # Try both configured Gemini model IDs. Record errors so the
            # final UI message shows why Gemini failed, not only Groq's error.
            models_to_try = ["gemini-3.8-flash", "gemini-3.7-flash"]

            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[uploaded_file, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            max_output_tokens=512,
                            temperature=0,
                        ),
                    )

                    response_text = getattr(response, "text", None)
                    if not response_text:
                        gemini_errors.append(
                            f"{model_name}: empty response"
                        )
                        continue

                    try:
                        analysis_data = _parse_json_object(
                            response_text,
                            f"Gemini Vision ({model_name})",
                        )
                    except ValueError as exc:
                        gemini_errors.append(str(exc))
                        continue

                    required_fields = [
                        "incident_type",
                        "severity",
                        "possible_victims",
                        "vehicles_detected",
                        "visible_hazards",
                        "description",
                        "confidence",
                    ]
                    missing = _missing_fields(analysis_data, required_fields)
                    if missing:
                        gemini_errors.append(
                            f"{model_name}: missing fields: "
                            + ", ".join(missing)
                        )
                        continue

                    return {
                        "success": True,
                        "analysis": analysis_data,
                        "provider": "Gemini",
                    }

                except Exception as error:
                    gemini_errors.append(f"{model_name}: {error}")
                    # Try the next Gemini model before falling back to Groq.
                    continue

        except Exception as error:
            gemini_errors.append(f"Gemini client/upload: {error}")

    else:
        gemini_errors.append("GEMINI_API_KEY is missing from the environment.")

    # Gemini failed; try Groq Vision with a capped output-token budget.
    groq_result = analyze_emergency_image_with_groq(image_path, prompt)
    if groq_result.get("success"):
        return groq_result

    gemini_error_text = " | ".join(gemini_errors) or "No Gemini error details available."
    groq_error_text = groq_result.get("error", "Unknown Groq error.")

    return {
        "success": False,
        "error": (
            "Gemini Vision and Groq Vision both failed. "
            f"Gemini details: {gemini_error_text}. "
            f"Groq details: {groq_error_text}"
        ),
        "error_type": (
            "rate_limit_error"
            if groq_result.get("error_type") == "rate_limit_error"
            else "vision_providers_failed"
        ),
        "gemini_errors": gemini_errors,
        "groq_error": groq_error_text,
    }


# ---------------------------------------------------------------------------
# Direct smoke test for Gemini text recommendation
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_emergency_data = {
        "incident_type": "Road Accident",
        "severity": "Medium",
        "predicted_demand": 1.0,
        "ambulance": "AMB-1042",
        "ambulance_distance_km": 1.17,
        "hospital": "Sunrise Hospital",
        "hospital_distance_km": 2.73,
        "available_beds": 162,
        "rescue_team": "Rescue Team 27",
        "rescue_team_type": "Flood Rescue",
        "rescue_team_distance_km": 3.2,
        "route_distance_km": 1.43,
        "estimated_travel_time_minutes": 1.71,
    }

    recommendation = generate_emergency_response(sample_emergency_data)
    print("\n===== Gemini Emergency Recommendation =====")
    print(recommendation)
