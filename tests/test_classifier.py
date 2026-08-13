from app.classifier import classify_message


def test_action_required():

    result = classify_message(
        "TEST_001",
        "Can you review the privacy checklist before 2026-09-09?"
    )

    assert result["category"] == "Action Required"
    assert 0 <= result["confidence"] <= 1
    assert result["reason"]


def test_meeting_event():

    result = classify_message(
        "TEST_002",
        "Reminder: mentor catch-up happens on 2026-09-16 at 11:00."
    )

    assert result["category"] == "Meeting or Event"
    assert 0 <= result["confidence"] <= 1


def test_promotional():

    result = classify_message(
        "TEST_003",
        "Limited time offer! Get 20% discount today."
    )

    assert result["category"] == "Promotional"


def test_personal_information():

    result = classify_message(
        "TEST_004",
        "I am from Bengaluru and my college is VTU."
    )

    assert result["category"] == "Personal Information"


def test_general_information():

    result = classify_message(
        "TEST_005",
        "FYI: The training material is available on the portal."
    )

    assert result["category"] == "General Information"


def test_sensitive_information():

    result = classify_message(
        "TEST_006",
        "Your OTP is 482193."
    )

    assert result["category"] == "Sensitive Information"
    assert result["confidence"] >= 0.90