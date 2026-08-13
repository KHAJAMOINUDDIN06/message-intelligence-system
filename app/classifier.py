import re
from typing import Dict, List


# ============================================================
# MESSAGE CLASSIFIER
# ============================================================
#
# The classifier uses local keyword/pattern scoring.
# No raw messages are sent to external AI services.
#
# Categories:
# 1. Action Required
# 2. Meeting or Event
# 3. Personal Information
# 4. General Information
# 5. Promotional
# 6. Sensitive Information
#
# Sensitive messages are checked first.
# ============================================================


CATEGORIES = [
    "Action Required",
    "Meeting or Event",
    "Personal Information",
    "General Information",
    "Promotional",
    "Sensitive Information",
]


# ============================================================
# KEYWORDS
# ============================================================

ACTION_KEYWORDS = [
    "please",
    "can you",
    "could you",
    "need you to",
    "you need to",
    "review",
    "submit",
    "complete",
    "finish",
    "send",
    "update",
    "confirm",
    "reply",
    "respond",
    "check",
    "call",
    "upload",
    "download",
    "prepare",
    "approve",
    "fill",
    "register",
    "remind",
    "before",
    "deadline",
    "due",
    "required",
    "action required",
]


MEETING_EVENT_KEYWORDS = [
    "meeting",
    "meet",
    "catch-up",
    "catch up",
    "appointment",
    "seminar",
    "event",
    "dinner",
    "lunch",
    "conference",
    "workshop",
    "training",
    "session",
    "webinar",
    "interview",
    "call at",
    "meet at",
    "calendar",
    "scheduled",
    "happens on",
    "at 10:00",
    "at 11:00",
    "at 12:00",
    "at 13:00",
    "at 14:00",
    "at 15:00",
    "at 16:00",
    "at 17:00",
    "at 18:00",
]


PERSONAL_KEYWORDS = [
    "my home address",
    "my address",
    "home address",
    "my phone",
    "my mobile",
    "my email",
    "my birthday",
    "my date of birth",
    "my profile",
    "my family",
    "my college",
    "my university",
    "my room",
    "my location",
    "my personal",
    "my contact",
    "i live",
    "i stay",
    "i am from",
]


PROMOTIONAL_KEYWORDS = [
    "promotion",
    "promotional",
    "offer",
    "discount",
    "sale",
    "limited time",
    "special offer",
    "exclusive",
    "deal",
    "coupon",
    "cashback",
    "free",
    "reward",
    "bonus",
    "subscribe",
    "join our",
    "buy now",
    "shop now",
    "save",
    "launch offer",
]


GENERAL_KEYWORDS = [
    "fyi",
    "for your information",
    "just checking",
    "quick update",
    "update:",
    "information",
    "note:",
    "please note",
    "the",
    "is on the portal",
    "available",
    "status",
    "details",
    "reminder",
]


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

DATE_PATTERN = re.compile(
    r"\b\d{4}-\d{2}-\d{2}\b"
)

TIME_PATTERN = re.compile(
    r"\b\d{1,2}:\d{2}\b"
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(message: str) -> str:
    """
    Convert message into lowercase normalized text.
    """

    return re.sub(
        r"\s+",
        " ",
        message.lower().strip()
    )


def contains_date(message: str) -> bool:
    """
    Check whether the message contains an explicit
    YYYY-MM-DD date.
    """

    return bool(DATE_PATTERN.search(message))


def contains_time(message: str) -> bool:
    """
    Check whether the message contains an explicit time.
    """

    return bool(TIME_PATTERN.search(message))


def keyword_score(
    text: str,
    keywords: List[str]
) -> int:
    """
    Count matching keywords.
    """

    score = 0

    for keyword in keywords:

        if keyword in text:
            score += 1

    return score


# ============================================================
# SENSITIVE MESSAGE HEURISTICS
# ============================================================

def looks_sensitive(message: str) -> bool:
    """
    Lightweight local check used by the classifier.

    The detailed sensitive detector remains responsible
    for actual sensitive-value detection.
    """

    text = normalize_text(message)

    sensitive_terms = [
        "password",
        "passcode",
        "pin",
        "otp",
        "one-time password",
        "verification code",
        "bank account",
        "account number",
        "card number",
        "credit card",
        "debit card",
        "api key",
        "access token",
        "auth token",
        "recovery code",
        "home address",
        "private address",
    ]

    for term in sensitive_terms:

        if term in text:
            return True

    # Long numeric sequences can indicate financial/
    # identification information.
    if re.search(r"\b\d{8,18}\b", text):
        return True

    return False


# ============================================================
# CATEGORY SCORING
# ============================================================

def calculate_scores(message: str) -> Dict[str, float]:
    """
    Calculate local evidence scores for each category.
    """

    text = normalize_text(message)

    scores = {
        "Action Required": 0.0,
        "Meeting or Event": 0.0,
        "Personal Information": 0.0,
        "General Information": 0.0,
        "Promotional": 0.0,
        "Sensitive Information": 0.0,
    }

    # --------------------------------------------------------
    # Sensitive
    # --------------------------------------------------------

    if looks_sensitive(message):
        scores["Sensitive Information"] += 10.0

    # --------------------------------------------------------
    # Action Required
    # --------------------------------------------------------

    action_matches = keyword_score(
        text,
        ACTION_KEYWORDS
    )

    scores["Action Required"] += (
        action_matches * 2.0
    )

    # Explicit deadline is strong evidence.
    if "deadline" in text:
        scores["Action Required"] += 4.0

    if "due" in text:
        scores["Action Required"] += 3.0

    if "before" in text and contains_date(message):
        scores["Action Required"] += 3.0

    # --------------------------------------------------------
    # Meeting / Event
    # --------------------------------------------------------

    event_matches = keyword_score(
        text,
        MEETING_EVENT_KEYWORDS
    )

    scores["Meeting or Event"] += (
        event_matches * 2.0
    )

    # A date + time is strong evidence of an event.
    if contains_date(message) and contains_time(message):
        scores["Meeting or Event"] += 6.0

    # Calendar language is strong evidence.
    if "calendar" in text:
        scores["Meeting or Event"] += 4.0

    if "scheduled" in text:
        scores["Meeting or Event"] += 4.0

    # --------------------------------------------------------
    # Personal Information
    # --------------------------------------------------------

    personal_matches = keyword_score(
        text,
        PERSONAL_KEYWORDS
    )

    scores["Personal Information"] += (
        personal_matches * 3.0
    )

    # --------------------------------------------------------
    # Promotional
    # --------------------------------------------------------

    promotional_matches = keyword_score(
        text,
        PROMOTIONAL_KEYWORDS
    )

    scores["Promotional"] += (
        promotional_matches * 3.0
    )

    # --------------------------------------------------------
    # General Information
    # --------------------------------------------------------

    general_matches = keyword_score(
        text,
        GENERAL_KEYWORDS
    )

    scores["General Information"] += (
        general_matches * 1.5
    )

    # FYI is particularly strong evidence.
    if text.startswith("fyi"):
        scores["General Information"] += 4.0

    # Quick update is generally informational.
    if "quick update" in text:
        scores["General Information"] += 3.0

    return scores


# ============================================================
# REASON GENERATION
# ============================================================

def generate_reason(
    category: str,
    message: str
) -> str:
    """
    Generate a short human-readable explanation.
    """

    text = normalize_text(message)

    if category == "Sensitive Information":

        if "otp" in text or "one-time password" in text:
            return (
                "The message contains an authentication "
                "code or OTP."
            )

        if "password" in text or "passcode" in text:
            return (
                "The message contains password or "
                "authentication information."
            )

        if "pin" in text:
            return (
                "The message contains a PIN or security code."
            )

        if (
            "card number" in text
            or "credit card" in text
            or "debit card" in text
        ):
            return (
                "The message contains payment card information."
            )

        if "bank account" in text or "account number" in text:
            return (
                "The message contains financial account information."
            )

        if "address" in text:
            return (
                "The message contains private address information."
            )

        return (
            "The message contains information that may "
            "require sensitive-data handling."
        )

    if category == "Action Required":

        if "deadline" in text or "due" in text:
            return (
                "The sender is asking the recipient to complete "
                "an action by a specified deadline."
            )

        if "please" in text:
            return (
                "The sender is requesting an action from "
                "the recipient."
            )

        return (
            "The message contains a request or action "
            "that the recipient needs to complete."
        )

    if category == "Meeting or Event":

        if contains_date(message) and contains_time(message):
            return (
                "The message contains an event or meeting "
                "with an explicit date and time."
            )

        return (
            "The message refers to a meeting, appointment, "
            "event, or scheduled activity."
        )

    if category == "Personal Information":

        if "address" in text:
            return (
                "The message contains personal address "
                "information."
            )

        if "phone" in text or "mobile" in text:
            return (
                "The message contains personal contact "
                "information."
            )

        return (
            "The message contains information about a "
            "person's personal details."
        )

    if category == "Promotional":

        return (
            "The message contains an offer, promotion, "
            "discount, reward, or marketing content."
        )

    return (
        "The message mainly provides information or an update "
        "without a clear required action or event."
    )


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_confidence(
    scores: Dict[str, float]
) -> float:
    """
    Convert category scores into a confidence value.

    This is an explainable heuristic confidence score,
    not a probability produced by a trained ML model.
    """

    sorted_scores = sorted(
        scores.values(),
        reverse=True
    )

    best_score = sorted_scores[0]

    second_score = (
        sorted_scores[1]
        if len(sorted_scores) > 1
        else 0
    )

    if best_score <= 0:
        return 0.50

    # Margin between best and second-best category.
    margin = best_score - second_score

    confidence = (
        0.55
        + min(best_score / 30.0, 0.30)
        + min(margin / 20.0, 0.15)
    )

    return round(
        min(confidence, 0.99),
        2
    )


# ============================================================
# MAIN CLASSIFICATION FUNCTION
# ============================================================

def classify_message(
    message_id: str,
    message: str
) -> Dict:
    """
    Classify one message.

    Returns:
        message_id
        category
        confidence
        reason
    """

    # --------------------------------------------------------
    # Sensitive information gets highest priority.
    # --------------------------------------------------------

    if looks_sensitive(message):

        return {
            "message_id": message_id,
            "category": "Sensitive Information",
            "confidence": 0.95,
            "reason": generate_reason(
                "Sensitive Information",
                message
            ),
        }

    # --------------------------------------------------------
    # Calculate all category scores.
    # --------------------------------------------------------

    scores = calculate_scores(message)

    # --------------------------------------------------------
    # Remove sensitive category because the message
    # was already checked above.
    # --------------------------------------------------------

    scores["Sensitive Information"] = 0.0

    # --------------------------------------------------------
    # Select highest-scoring category.
    # --------------------------------------------------------

    category = max(
        scores,
        key=scores.get
    )

    # --------------------------------------------------------
    # If there is no evidence, classify as General Information.
    # --------------------------------------------------------

    if scores[category] <= 0:

        category = "General Information"

    confidence = calculate_confidence(scores)

    reason = generate_reason(
        category,
        message
    )

    return {
        "message_id": message_id,
        "category": category,
        "confidence": confidence,
        "reason": reason,
    }


# ============================================================
# BATCH CLASSIFICATION
# ============================================================

def classify_messages(
    messages: List[Dict]
) -> List[Dict]:
    """
    Classify multiple messages.

    Messages are processed in the order received.
    """

    results = []

    for message in messages:

        result = classify_message(
            message_id=message["message_id"],
            message=message["message"],
        )

        results.append(result)

    return results