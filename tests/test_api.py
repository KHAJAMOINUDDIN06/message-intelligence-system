from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


# ============================================================
# ROOT ENDPOINT
# ============================================================

def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    # The root endpoint should return a JSON response.
    assert isinstance(data, dict)


# ============================================================
# HEALTH ENDPOINT
# ============================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


# ============================================================
# ANALYZE - MEETING
# ============================================================

def test_analyze_meeting():
    response = client.post(
        "/analyze",
        json={
            "message": (
                "We have a meeting with Rahul "
                "on 2026-08-20 at 10:30."
            ),
            "sender": "Khaja",
        },
    )

    assert response.status_code == 200

    data = response.json()

    # Classification
    assert data["classification"]["category"] == (
        "Meeting or Event"
    )

    # Extraction
    assert data["extracted_item"]["type"] == "meeting"

    assert data["extracted_item"]["date_or_deadline"] == (
        "2026-08-20"
    )

    assert data["extracted_item"]["time"] == "10:30"

    assert data["extracted_item"]["person"] == "Rahul"


# ============================================================
# ANALYZE - SENSITIVE INFORMATION
# ============================================================

def test_analyze_sensitive_message():
    response = client.post(
        "/analyze",
        json={
            "message": "My OTP is 482193.",
            "sender": "Khaja",
        },
    )

    assert response.status_code == 200

    data = response.json()

    sensitive = data["sensitive_information"]

    # Sensitive information must be detected.
    assert (
        sensitive["contains_sensitive_information"]
        is True
    )

    # OTP is high risk.
    assert sensitive["highest_risk"] == "high"

    # Raw OTP must never appear in masked text.
    assert "482193" not in sensitive["masked_text"]

    # Expected masked output.
    assert sensitive["masked_text"] == "My ******."


# ============================================================
# ANALYZE - NORMAL MESSAGE
# ============================================================

def test_analyze_normal_message():
    response = client.post(
        "/analyze",
        json={
            "message": (
                "The project documentation "
                "is available."
            ),
            "sender": "Khaja",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["validation"]["message_valid"] is True


# ============================================================
# ANALYZE - MISSING MESSAGE
# ============================================================

def test_analyze_missing_message():
    response = client.post(
        "/analyze",
        json={
            "sender": "Khaja",
        },
    )

    # FastAPI validation should reject the request.
    assert response.status_code == 422