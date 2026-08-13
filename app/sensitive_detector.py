import re
from typing import List, Dict


# ============================================================
# SENSITIVE INFORMATION DETECTOR
# ============================================================

# All detection happens locally.
# Raw messages are NOT sent to external AI services.


SENSITIVE_PATTERNS = [

    # --------------------------------------------------------
    # OTP
    # Examples:
    # OTP is 482193
    # OTP is 482193-50
    # --------------------------------------------------------
    {
        "type": "one_time_password",
        "pattern": (
            r"\b(?:otp|one[- ]time password)\b"
            r"\s*(?:is|:|=)?\s*"
            r"\d{4,8}(?:-\d{2})?\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # PIN
    # --------------------------------------------------------
    {
        "type": "pin",
        "pattern": (
            r"\bpin\b"
            r"\s*(?:is|:|=)?\s*"
            r"\d{4,6}(?:-\d{2})?\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------
    {
        "type": "password",
        "pattern": (
            r"\bpassword\b"
            r"\s*(?:is|:|=)\s*\S+"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # BANK ACCOUNT
    # Examples:
    # 006418220145
    # 006418220145-38
    # --------------------------------------------------------
    {
        "type": "bank_account",
        "pattern": (
            r"\b(?:account number|account no|a/c no)\b"
            r"\s*(?:is|:|=)?\s*"
            r"\d{8,18}(?:-\d{2})?\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # CARD NUMBER
    # Examples:
    # 4111 1111 1111 1111
    # 4111 1111 1111 1111-92
    # --------------------------------------------------------
    {
        "type": "card_number",
        "pattern": (
            r"\b(?:\d{4}[ -]?){3}"
            r"\d{4}(?:-\d{2})?\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------
    {
        "type": "email_address",
        "pattern": (
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "risk": "medium",
    },

    # --------------------------------------------------------
    # PHONE NUMBER
    #
    # Supports:
    # 9876543210
    # 98765 43210
    # 98765 43210-86
    # --------------------------------------------------------
    {
        "type": "phone_number",
        "pattern": (
            r"(?<!\d)"
            r"(?:\+91[\s-]?)?"
            r"[6-9]\d{4}\s?\d{5}"
            r"(?:-\d{2})?"
            r"(?!\d)"
        ),
        "risk": "medium",
    },

    # --------------------------------------------------------
    # AUTHENTICATION TOKEN
    # --------------------------------------------------------
    {
        "type": "authentication_token",
        "pattern": (
            r"\b(?:token|auth token|access token|api key)\b"
            r"\s*(?:is|:|=)?\s*"
            r"[A-Za-z0-9_\-]{12,}\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # ACCOUNT RECOVERY CODE
    # Examples:
    # RC-88-KL-19
    # RC-88-KL-19-59
    # --------------------------------------------------------
    {
        "type": "account_recovery_code",
        "pattern": (
            r"\b(?:account recovery code|recovery code)\b"
            r"\s*(?:is|:|=)?\s*"
            r"RC-[A-Z0-9-]{8,}\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # IDENTIFICATION NUMBER
    # Examples:
    # ID-7842-XY
    # ID-7842-XY-94
    # --------------------------------------------------------
    {
        "type": "identification_number",
        "pattern": (
            r"\bID-\d{4}-[A-Z]{2}(?:-\d{2})?\b"
        ),
        "risk": "high",
    },

    # --------------------------------------------------------
    # PRIVATE ADDRESS
    # --------------------------------------------------------
    {
        "type": "private_address",
        "pattern": (
            r"\b(?:home address|my address|private address)\b"
            r"\s*(?:is|:)?\s*"
            r"[^.!?\n]+"
        ),
        "risk": "high",
    },
]


# ============================================================
# DETECTION
# ============================================================

def detect_sensitive_information(message: str) -> List[Dict]:
    """
    Detect sensitive information in a message.

    Only metadata about the detection is returned.
    The actual sensitive value is never returned.
    """

    detections = []

    for rule in SENSITIVE_PATTERNS:

        matches = re.finditer(
            rule["pattern"],
            message,
            flags=re.IGNORECASE
        )

        for match in matches:

            detections.append(
                {
                    "sensitivity_type": rule["type"],
                    "risk": rule["risk"],
                    "start": match.start(),
                    "end": match.end(),
                }
            )

    return detections


# ============================================================
# MASKING
# ============================================================

def mask_sensitive_information(message: str) -> str:
    """
    Replace every detected sensitive value with ******.
    """

    masked_message = message

    matches_to_replace = []

    for rule in SENSITIVE_PATTERNS:

        matches = re.finditer(
            rule["pattern"],
            message,
            flags=re.IGNORECASE
        )

        for match in matches:

            matches_to_replace.append(
                (
                    match.start(),
                    match.end()
                )
            )

    # Remove duplicate matches
    matches_to_replace = sorted(
        set(matches_to_replace),
        reverse=True
    )

    # Replace from right to left
    for start, end in matches_to_replace:

        masked_message = (
            masked_message[:start]
            + "******"
            + masked_message[end:]
        )

    return masked_message


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def recommended_action(risk: str) -> str:

    if risk == "high":
        return "do_not_store"

    if risk == "medium":
        return "ask_for_confirmation"

    return "safe_to_process_locally"


# ============================================================
# COMPLETE MESSAGE ANALYSIS
# ============================================================

def analyze_message(
    message_id: str,
    message: str
) -> Dict:
    """
    Analyze one message.

    The returned result never contains the raw sensitive value.
    """

    detections = detect_sensitive_information(message)

    if not detections:

        return {
            "message_id": message_id,
            "contains_sensitive_information": False,
            "detections": [],
            "masked_text": message,
        }

    risk_order = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    highest_risk = max(
        detections,
        key=lambda item: risk_order[item["risk"]]
    )

    safe_detections = []

    for detection in detections:

        safe_detections.append(
            {
                "sensitivity_type": (
                    detection["sensitivity_type"]
                ),
                "risk": detection["risk"],
                "recommended_action": (
                    recommended_action(
                        detection["risk"]
                    )
                ),
            }
        )

    return {
        "message_id": message_id,
        "contains_sensitive_information": True,
        "detections": safe_detections,
        "highest_risk": highest_risk["risk"],
        "masked_text": mask_sensitive_information(
            message
        ),
    }