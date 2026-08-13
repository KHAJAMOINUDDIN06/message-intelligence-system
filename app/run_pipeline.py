from pathlib import Path
import json

import pandas as pd

from sensitive_detector import (
    detect_sensitive_information,
    mask_sensitive_information,
)

from classifier import classify_message

from extractor import extract_task_or_event


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

MESSAGES_FILE = DATA_DIR / "messages.csv"


# ============================================================
# LOAD AND VALIDATE MESSAGES
# ============================================================

def load_messages():
    """
    Load and validate the assignment dataset.

    Messages are processed chronologically.
    """

    messages = pd.read_csv(
        MESSAGES_FILE
    )

    required_columns = [
        "message_id",
        "timestamp",
        "sender",
        "message",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in messages.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    messages["timestamp"] = pd.to_datetime(
        messages["timestamp"]
    )

    # --------------------------------------------------------
    # Chronological processing
    # --------------------------------------------------------

    messages = (
        messages
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    return messages


# ============================================================
# SENSITIVE INFORMATION PROCESSING
# ============================================================

def process_sensitive_information(
    message_id,
    message
):
    """
    Detect and mask sensitive information.

    IMPORTANT:
    Raw sensitive values are never returned in the output.
    """

    detections = detect_sensitive_information(
        message
    )

    if not detections:
        return []

    masked_message = mask_sensitive_information(
        message
    )

    results = []

    for detection in detections:

        results.append(
            {
                "message_id": message_id,

                "sensitivity_type": detection[
                    "sensitivity_type"
                ],

                "risk": detection[
                    "risk"
                ],

                "masked_text": masked_message,

                "recommended_action": (
                    "do_not_store"
                    if detection["risk"] == "high"
                    else "ask_for_confirmation"
                ),
            }
        )

    return results


# ============================================================
# PROCESS ALL MESSAGES
# ============================================================

def process_messages(messages):
    """
    Process every message chronologically.

    Returns:

    1. Classification results
    2. Extracted tasks/events
    3. Sensitive information results
    """

    classifications = []

    extracted_items = []

    sensitive_results = []

    # --------------------------------------------------------
    # IMPORTANT:
    # messages is already sorted chronologically.
    # --------------------------------------------------------

    for _, row in messages.iterrows():

        message_id = str(
            row["message_id"]
        )

        message = str(
            row["message"]
        )

        sender = str(
            row["sender"]
        )

        # ====================================================
        # PART 3
        # Sensitive Information Detection
        # ====================================================

        message_sensitive_results = (
            process_sensitive_information(
                message_id,
                message
            )
        )

        sensitive_results.extend(
            message_sensitive_results
        )

        # ====================================================
        # PART 1
        # Message Classification
        # ====================================================

        classification = classify_message(
            message_id,
            message
        )

        classifications.append(
            classification
        )

        # ====================================================
        # PART 2
        # Task/Event Extraction
        # ====================================================

        extracted_item = extract_task_or_event(
            message_id=message_id,
            message=message,
            sender=sender,
        )

        if extracted_item:

            # ------------------------------------------------
            # Security:
            # Never place raw sensitive message text
            # into generated output.
            # ------------------------------------------------

            if message_sensitive_results:

                extracted_item[
                    "description"
                ] = mask_sensitive_information(
                    message
                )

            extracted_items.append(
                extracted_item
            )

    return (
        classifications,
        extracted_items,
        sensitive_results,
    )


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    data,
    filepath
):
    """
    Save structured JSON.
    """

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# SAVE OUTPUTS
# ============================================================

def save_outputs(
    classifications,
    extracted_items,
    sensitive_results
):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Classification results
    # --------------------------------------------------------

    classifications_file = (
        OUTPUT_DIR /
        "classifications.csv"
    )

    pd.DataFrame(
        classifications
    ).to_csv(
        classifications_file,
        index=False
    )

    # --------------------------------------------------------
    # Task/Event results
    # --------------------------------------------------------

    extracted_items_file = (
        OUTPUT_DIR /
        "extracted_items.json"
    )

    save_json(
        extracted_items,
        extracted_items_file
    )

    # --------------------------------------------------------
    # Sensitive information results
    # --------------------------------------------------------

    sensitive_file = (
        OUTPUT_DIR /
        "sensitive_information.json"
    )

    save_json(
        sensitive_results,
        sensitive_file
    )

    return (
        classifications_file,
        extracted_items_file,
        sensitive_file
    )


# ============================================================
# SAFE SUMMARY
# ============================================================

def print_summary(
    messages,
    classifications,
    extracted_items,
    sensitive_results
):

    print()
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(
        f"Messages processed: {len(messages)}"
    )

    print(
        f"Classification results: "
        f"{len(classifications)}"
    )

    print(
        f"Tasks/events extracted: "
        f"{len(extracted_items)}"
    )

    print(
        f"Sensitive detections: "
        f"{len(sensitive_results)}"
    )

    # --------------------------------------------------------
    # Classification summary
    # --------------------------------------------------------

    print()
    print("Classification summary:")

    category_counts = {}

    for result in classifications:

        category = result[
            "category"
        ]

        category_counts[category] = (
            category_counts.get(
                category,
                0
            ) + 1
        )

    for category, count in sorted(
        category_counts.items()
    ):

        print(
            f"- {category}: {count}"
        )

    # --------------------------------------------------------
    # Extraction summary
    # --------------------------------------------------------

    print()
    print("Task/Event summary:")

    type_counts = {}

    for item in extracted_items:

        item_type = item[
            "type"
        ]

        type_counts[item_type] = (
            type_counts.get(
                item_type,
                0
            ) + 1
        )

    for item_type, count in sorted(
        type_counts.items()
    ):

        print(
            f"- {item_type}: {count}"
        )

    # --------------------------------------------------------
    # Security
    # --------------------------------------------------------

    print()
    print(
        "Security check: "
        "sensitive values are masked."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MESSAGE INTELLIGENCE SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------

    messages = load_messages()

    print(
        f"Total messages: {len(messages)}"
    )

    print()
    print("Dataset columns:")

    for column in messages.columns:

        print(
            f"- {column}"
        )

    # --------------------------------------------------------
    # SAFE PREVIEW
    # --------------------------------------------------------

    print()
    print("Safe preview:")

    print(
        messages[
            [
                "message_id",
                "timestamp",
                "sender"
            ]
        ]
        .head()
        .to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Process
    # --------------------------------------------------------

    print()
    print(
        "Processing messages "
        "chronologically..."
    )

    (
        classifications,
        extracted_items,
        sensitive_results
    ) = process_messages(
        messages
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    (
        classifications_file,
        extracted_items_file,
        sensitive_file
    ) = save_outputs(
        classifications,
        extracted_items,
        sensitive_results
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_summary(
        messages,
        classifications,
        extracted_items,
        sensitive_results
    )

    # --------------------------------------------------------
    # Output locations
    # --------------------------------------------------------

    print()
    print("Generated output files:")

    print(
        f"- {classifications_file}"
    )

    print(
        f"- {extracted_items_file}"
    )

    print(
        f"- {sensitive_file}"
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()