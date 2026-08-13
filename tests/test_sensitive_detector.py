import sys
from pathlib import Path

# Allow the test to import modules from the app folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_DIR = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIR))

from sensitive_detector import (
    detect_sensitive_information,
    mask_sensitive_information,
    analyze_message,
)


def test_otp_detection():
    message = "Your OTP is 123456"

    detections = detect_sensitive_information(message)

    assert len(detections) >= 1
    assert detections[0]["sensitivity_type"] == "one_time_password"
    assert detections[0]["risk"] == "high"


def test_pin_detection():
    message = "Your PIN is 1234"

    detections = detect_sensitive_information(message)

    assert len(detections) >= 1
    assert detections[0]["sensitivity_type"] == "pin"
    assert detections[0]["risk"] == "high"


def test_password_detection():
    message = "Your password is MyPassword123"

    detections = detect_sensitive_information(message)

    assert len(detections) >= 1
    assert detections[0]["sensitivity_type"] == "password"
    assert detections[0]["risk"] == "high"


def test_sensitive_information_is_masked():
    message = "Your OTP is 123456"

    masked = mask_sensitive_information(message)

    assert "123456" not in masked
    assert "******" in masked


def test_analysis_does_not_return_raw_sensitive_value():
    message = "Your OTP is 123456"

    result = analyze_message(
        "TEST_001",
        message
    )

    assert result["contains_sensitive_information"] is True
    assert "123456" not in result["masked_text"]
    assert "******" in result["masked_text"]


def test_safe_message():
    message = "The meeting is tomorrow at 10 AM."

    result = analyze_message(
        "TEST_002",
        message
    )

    assert result["contains_sensitive_information"] is False
    assert result["masked_text"] == message