from app.extractor import (
    extract_task_or_event,
)


def test_task_with_deadline():

    result = extract_task_or_event(
        "TEST_001",
        "Can you review the privacy checklist before 2026-09-09?",
        "Ishaan"
    )

    assert result is not None
    assert result["type"] == "task"
    assert result["date_or_deadline"] == "2026-09-09"
    assert result["source_message_id"] == "TEST_001"


def test_meeting_with_date_and_time():

    result = extract_task_or_event(
        "TEST_002",
        "Reminder: mentor catch-up happens on 2026-09-16 at 11:00.",
        "Kabir"
    )

    assert result is not None
    assert result["type"] == "meeting"
    assert result["date_or_deadline"] == "2026-09-16"
    assert result["time"] == "11:00"


def test_event_with_date_and_time():

    result = extract_task_or_event(
        "TEST_003",
        "Calendar update: family dinner, 2026-09-19 at 10:00.",
        "Meera"
    )

    assert result is not None
    assert result["type"] == "event"
    assert result["date_or_deadline"] == "2026-09-19"
    assert result["time"] == "10:00"


def test_missing_date_is_not_invented():

    result = extract_task_or_event(
        "TEST_004",
        "Please review the document.",
        "Aarav"
    )

    assert result is not None
    assert result["date_or_deadline"] is None
    assert result["time"] is None


def test_priority_high():

    result = extract_task_or_event(
        "TEST_005",
        "Urgent: please submit the report before 2026-09-10.",
        "Aarav"
    )

    assert result is not None
    assert result["priority"] == "high"


def test_no_task_or_event():

    result = extract_task_or_event(
        "TEST_006",
        "The training material is available on the portal.",
        "Aarav"
    )

    assert result is None