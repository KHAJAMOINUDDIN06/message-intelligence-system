import re
from typing import Dict, List, Optional


# ============================================================
# TASK AND EVENT EXTRACTOR
# ============================================================
#
# This module extracts:
# - task/event type
# - title
# - description
# - date/deadline
# - time
# - person
# - priority
# - source message ID
#
# IMPORTANT:
# Missing information is stored as None.
# We never invent dates, times, people, or deadlines.
# ============================================================


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

DATE_PATTERN = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2})\b"
)

TIME_PATTERN = re.compile(
    r"\b([01]?\d|2[0-3]):([0-5]\d)\b"
)


# ============================================================
# KEYWORDS
# ============================================================

TASK_KEYWORDS = [
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
    "upload",
    "prepare",
    "approve",
    "fill",
    "register",
    "call",
]


MEETING_KEYWORDS = [
    "meeting",
    "meet",
    "catch-up",
    "catch up",
    "appointment",
    "interview",
    "call",
    "one-on-one",
    "one on one",
]


EVENT_KEYWORDS = [
    "event",
    "dinner",
    "lunch",
    "seminar",
    "conference",
    "workshop",
    "training",
    "webinar",
    "session",
    "birthday",
    "celebration",
    "ceremony",
    "festival",
]

HIGH_PRIORITY_KEYWORDS = [
    "urgent",
    "immediately",
    "asap",
    "critical",
    "high priority",
    "important",
    "deadline",
]


LOW_PRIORITY_KEYWORDS = [
    "optional",
    "whenever",
    "no rush",
    "low priority",
]


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_text(message: str) -> str:
    """
    Normalize whitespace and lowercase text.
    """

    return re.sub(
        r"\s+",
        " ",
        message.strip()
    )


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_date(message: str) -> Optional[str]:
    """
    Extract an explicit YYYY-MM-DD date.

    Returns None if no explicit date is present.
    """

    match = DATE_PATTERN.search(message)

    if match:
        return match.group(1)

    return None


# ============================================================
# TIME EXTRACTION
# ============================================================

def extract_time(message: str) -> Optional[str]:
    """
    Extract an explicit HH:MM time.

    Returns None if no explicit time is present.
    """

    match = TIME_PATTERN.search(message)

    if match:
        return match.group(0)

    return None


# ============================================================
# PERSON EXTRACTION
# ============================================================

def extract_person(
    message: str,
    sender: Optional[str] = None
) -> Optional[str]:
    """
    Extract a person when the message explicitly identifies
    one.

    We use the sender only when the message refers to the
    sender through first-person wording.

    We do not invent people.
    """

    # Explicit "with NAME" pattern.
    match = re.search(
        r"\bwith\s+([A-Z][a-z]+)\b",
        message
    )

    if match:
        return match.group(1)

    # Explicit "for NAME" pattern.
    match = re.search(
        r"\bfor\s+([A-Z][a-z]+)\b",
        message
    )

    if match:
        return match.group(1)

    # Explicit "from NAME" pattern.
    match = re.search(
        r"\bfrom\s+([A-Z][a-z]+)\b",
        message
    )

    if match:
        return match.group(1)

    return None


# ============================================================
# PRIORITY
# ============================================================

def extract_priority(message: str) -> str:
    """
    Determine priority using explicit wording.

    Default priority is medium.

    We do not assume urgency when it is not stated.
    """

    text = message.lower()

    for keyword in HIGH_PRIORITY_KEYWORDS:

        if keyword in text:
            return "high"

    for keyword in LOW_PRIORITY_KEYWORDS:

        if keyword in text:
            return "low"

    return "medium"


# ============================================================
# TYPE DETECTION
# ============================================================

def detect_item_type(message: str) -> Optional[str]:
    """
    Determine whether the message contains a task,
    meeting, or event.

    Informational phrases such as "training material"
    are not treated as events unless there is evidence
    of an actual scheduled activity.
    """

    text = message.lower()

    # --------------------------------------------------------
    # Ignore informational references that are not events.
    # --------------------------------------------------------

    non_event_phrases = [
        "training material",
        "training materials",
        "training document",
        "training documents",
        "training content",
        "training notes",
        "training resources",
    ]

    for phrase in non_event_phrases:

        if phrase in text:
            # If there is no explicit scheduling information,
            # this is informational content rather than an event.
            if (
                not re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text)
                and not re.search(r"\b\d{1,2}:\d{2}\b", text)
                and "scheduled" not in text
                and "happens on" not in text
            ):
                return None

    # --------------------------------------------------------
    # Meeting
    # --------------------------------------------------------

    for keyword in MEETING_KEYWORDS:

        if keyword in text:
            return "meeting"

    # --------------------------------------------------------
    # Event
    # --------------------------------------------------------

    for keyword in EVENT_KEYWORDS:

        if keyword in text:

            # Generic event words need stronger evidence.
            if keyword == "event":

                if (
                    re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text)
                    or re.search(r"\b\d{1,2}:\d{2}\b", text)
                    or "scheduled" in text
                    or "happens on" in text
                    or "calendar" in text
                ):
                    return "event"

                continue

            # Named events such as dinner, seminar, workshop,
            # etc. are accepted when they appear in context.
            return "event"

    # --------------------------------------------------------
    # Task
    # --------------------------------------------------------

    for keyword in TASK_KEYWORDS:

        if keyword in text:
            return "task"

    return None


# ============================================================
# TITLE EXTRACTION
# ============================================================

def extract_title(
    message: str,
    item_type: str
) -> str:
    """
    Generate a concise title using explicit message content.

    This does not invent information.
    """

    text = normalize_text(message)

    # --------------------------------------------------------
    # Meeting
    # --------------------------------------------------------

    if item_type == "meeting":

        if "catch-up" in text.lower():
            return "Catch-up meeting"

        if "catch up" in text.lower():
            return "Catch-up meeting"

        if "appointment" in text.lower():
            return "Appointment"

        if "interview" in text.lower():
            return "Interview"

        if "one-on-one" in text.lower():
            return "One-on-one meeting"

        if "one on one" in text.lower():
            return "One-on-one meeting"

        if "meeting" in text.lower():
            return "Meeting"

        if "call" in text.lower():
            return "Call"

        return "Meeting or appointment"

    # --------------------------------------------------------
    # Event
    # --------------------------------------------------------

    if item_type == "event":

        event_names = [
            "dinner",
            "lunch",
            "seminar",
            "conference",
            "workshop",
            "training",
            "webinar",
            "session",
            "birthday",
            "celebration",
            "ceremony",
            "festival",
        ]

        for event_name in event_names:

            if event_name in text.lower():
                return event_name.capitalize()

        return "Event"

    # --------------------------------------------------------
    # Task
    # --------------------------------------------------------

    task_patterns = [
        (r"\breview\b", "Review task"),
        (r"\bsubmit\b", "Submit task"),
        (r"\bcomplete\b", "Complete task"),
        (r"\bfinish\b", "Finish task"),
        (r"\bsend\b", "Send task"),
        (r"\bupdate\b", "Update task"),
        (r"\bconfirm\b", "Confirmation task"),
        (r"\breply\b", "Reply task"),
        (r"\brespond\b", "Response task"),
        (r"\bcheck\b", "Check task"),
        (r"\bupload\b", "Upload task"),
        (r"\bprepare\b", "Preparation task"),
        (r"\bapprove\b", "Approval task"),
        (r"\bfill\b", "Form completion task"),
        (r"\bregister\b", "Registration task"),
        (r"\bcall\b", "Call task"),
    ]

    for pattern, title in task_patterns:

        if re.search(pattern, text, re.IGNORECASE):
            return title

    return "Task"


# ============================================================
# DESCRIPTION
# ============================================================

def extract_description(
    message: str
) -> str:
    """
    Preserve the original message as the description.

    The source message is kept so the extracted item can
    be traced back to its source.
    """

    return normalize_text(message)


# ============================================================
# COMPLETE EXTRACTION
# ============================================================

def extract_task_or_event(
    message_id: str,
    message: str,
    sender: Optional[str] = None
) -> Optional[Dict]:
    """
    Extract one task/event from a message.

    Returns None when no actionable task/event is detected.
    """

    item_type = detect_item_type(message)

    if item_type is None:
        return None

    date_value = extract_date(message)
    time_value = extract_time(message)
    person_value = extract_person(
        message,
        sender
    )

    title = extract_title(
        message,
        item_type
    )

    description = extract_description(
        message
    )

    priority = extract_priority(
        message
    )

    item_id_prefix = (
        "TASK"
        if item_type == "task"
        else "EVENT"
        if item_type == "event"
        else "MEETING"
    )

    item_id = (
        f"{item_id_prefix}_{message_id}"
    )

    return {
        "item_id": item_id,
        "type": item_type,
        "title": title,
        "description": description,
        "date_or_deadline": date_value,
        "time": time_value,
        "person": person_value,
        "priority": priority,
        "source_message_id": message_id,
    }


# ============================================================
# BATCH EXTRACTION
# ============================================================

def extract_tasks_and_events(
    messages: List[Dict]
) -> List[Dict]:
    """
    Extract tasks/events from messages in chronological order.

    Messages are processed in the order supplied.
    """

    results = []

    for message in messages:

        result = extract_task_or_event(
            message_id=message["message_id"],
            message=message["message"],
            sender=message.get("sender"),
        )

        if result is not None:

            results.append(result)

    return results