import json
from unittest.mock import MagicMock, patch

import pytest

from app.services import llm_service


@pytest.fixture
def emergency_data():
    return {
        "incident_type": "Road Accident",
        "severity": "High",
        "predicted_demand": 2,
        "ambulance": "AMB-101",
        "ambulance_distance_km": 1.5,
        "hospital": "City Hospital",
        "hospital_distance_km": 2.2,
        "available_beds": 10,
        "rescue_team": "Rescue Team 1",
        "rescue_team_type": "Medical",
        "rescue_team_distance_km": 3.0,
        "route_distance_km": 4.5,
        "estimated_travel_time_minutes": 8.0,
    }


def test_fallback_response_contains_emergency_details(emergency_data):
    result = llm_service.generate_fallback_response(
        emergency_data,
        reason="Test fallback",
    )

    assert "Road Accident" in result
    assert "AMB-101" in result
    assert "City Hospital" in result
    assert "Test fallback" in result


def test_fallback_response_handles_missing_values():
    result = llm_service.generate_fallback_response({})

    assert "No ambulance available" in result
    assert "No suitable hospital available" in result
    assert "N/A" in result


def test_emergency_response_without_api_key(emergency_data):
    with patch.object(llm_service, "GEMINI_API_KEY", None):
        result = llm_service.generate_emergency_response(emergency_data)

    assert isinstance(result, str)
    assert "GEMINI_API_KEY is missing" in result


def test_emergency_response_success(emergency_data):
    expected = {
        "summary": "Road accident",
        "predicted_demand": 2,
        "recommended_ambulance": "AMB-101",
        "recommended_hospital": "City Hospital",
        "recommended_rescue_team": "Rescue Team 1",
        "route_distance_km": 4.5,
        "estimated_travel_time_minutes": 8,
        "immediate_action": "Dispatch ambulance",
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(expected)

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch.object(llm_service.genai, "Client", return_value=mock_client),
    ):
        result = llm_service.generate_emergency_response(emergency_data)

    assert result["success"] is True
    assert result["provider"] == "Gemini"
    assert result["recommendation"] == expected


def test_emergency_response_invalid_json(emergency_data):
    mock_response = MagicMock()
    mock_response.text = "{invalid json"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch.object(llm_service.genai, "Client", return_value=mock_client),
    ):
        result = llm_service.generate_emergency_response(emergency_data)

    assert result["success"] is False
    assert "invalid JSON" in result["error"]


def test_emergency_response_missing_fields(emergency_data):
    mock_response = MagicMock()
    mock_response.text = json.dumps({"summary": "Only summary"})

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch.object(llm_service.genai, "Client", return_value=mock_client),
    ):
        result = llm_service.generate_emergency_response(emergency_data)

    assert result["success"] is False
    assert "Missing fields" in result["error"]


def test_emergency_response_empty_response_uses_fallback(emergency_data):
    mock_response = MagicMock()
    mock_response.text = None

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch.object(llm_service.genai, "Client", return_value=mock_client),
    ):
        result = llm_service.generate_emergency_response(emergency_data)

    assert isinstance(result, str)
    assert "Gemini returned an empty response" in result


def test_emergency_response_api_error_uses_fallback(emergency_data):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("API unavailable")

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch.object(llm_service.genai, "Client", return_value=mock_client),
    ):
        result = llm_service.generate_emergency_response(emergency_data)

    assert isinstance(result, str)
    assert "Gemini API error" in result


def test_emergency_image_missing_file():
    result = llm_service.analyze_emergency_image(
        "this_file_does_not_exist.png"
    )

    assert result["success"] is False
    assert "Image file not found" in result["error"]


def test_groq_image_missing_api_key(tmp_path):
    image_file = tmp_path / "sample.png"
    image_file.write_bytes(b"test image")

    with patch.object(llm_service, "GROQ_API_KEY", None):
        result = llm_service.analyze_emergency_image_with_groq(
            image_file,
            "Analyze image",
        )

    assert result["success"] is False
    assert "GROQ_API_KEY is missing" in result["error"]


def test_groq_image_invalid_json(tmp_path):
    image_file = tmp_path / "sample.png"
    image_file.write_bytes(b"test image")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="not json"))
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with (
        patch.object(llm_service, "GROQ_API_KEY", "fake-test-key"),
        patch.object(llm_service, "Groq", return_value=mock_client),
    ):
        result = llm_service.analyze_emergency_image_with_groq(
            image_file,
            "Analyze image",
        )

    assert result["success"] is False
    assert "invalid JSON" in result["error"]


def test_groq_image_valid_response(tmp_path):
    image_file = tmp_path / "sample.jpg"
    image_file.write_bytes(b"test image")

    expected = {
        "incident_type": "Road Accident",
        "severity": "High",
        "possible_victims": 2,
        "vehicles_detected": 3,
        "visible_hazards": ["Damaged vehicle"],
        "description": "A damaged vehicle is visible.",
        "confidence": 85,
    }

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(expected)))
    ]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with (
        patch.object(llm_service, "GROQ_API_KEY", "fake-test-key"),
        patch.object(llm_service, "Groq", return_value=mock_client),
    ):
        result = llm_service.analyze_emergency_image_with_groq(
            image_file,
            "Analyze image",
        )

    assert result["success"] is True
    assert result["provider"] == "Groq"
    assert result["analysis"] == expected


def test_gemini_image_valid_response(tmp_path):
    image_file = tmp_path / "sample.jpg"
    image_file.write_bytes(b"test image")

    expected = {
        "incident_type": "Road Accident",
        "severity": "High",
        "possible_victims": 2,
        "vehicles_detected": 3,
        "visible_hazards": ["Damaged vehicle"],
        "description": "A damaged vehicle is visible.",
        "confidence": 85,
    }

    mock_response = MagicMock()
    mock_response.text = json.dumps(expected)

    mock_client = MagicMock()
    mock_client.files.upload.return_value = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch("app.services.llm_service.genai.Client", return_value=mock_client),
    ):
        result = llm_service.analyze_emergency_image(image_file)

    assert result["success"] is True
    assert result["provider"] == "Gemini"
    assert result["analysis"] == expected

    mock_client.files.upload.assert_called_once()
    mock_client.models.generate_content.assert_called_once()


def test_gemini_image_failure_uses_groq_fallback(tmp_path):
    image_file = tmp_path / "sample.jpg"
    image_file.write_bytes(b"test image")

    expected = {
        "incident_type": "Road Accident",
        "severity": "High",
        "possible_victims": 2,
        "vehicles_detected": 3,
        "visible_hazards": ["Damaged vehicle"],
        "description": "A damaged vehicle is visible.",
        "confidence": 85,
    }

    mock_client = MagicMock()
    mock_client.files.upload.return_value = MagicMock()
    mock_client.models.generate_content.side_effect = Exception(
        "Gemini API unavailable"
    )

    groq_result = {
        "success": True,
        "analysis": expected,
        "provider": "Groq",
    }

    with (
        patch.object(llm_service, "GEMINI_API_KEY", "fake-test-key"),
        patch(
            "app.services.llm_service.genai.Client",
            return_value=mock_client,
        ),
        patch.object(
            llm_service,
            "analyze_emergency_image_with_groq",
            return_value=groq_result,
        ) as mock_groq,
    ):
        result = llm_service.analyze_emergency_image(image_file)

    assert result["success"] is True
    assert result["provider"] == "Groq"
    assert result["analysis"] == expected
    mock_groq.assert_called_once()