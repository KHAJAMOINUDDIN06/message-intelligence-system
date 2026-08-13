from pathlib import Path
import json

import pandas as pd

from classifier import classify_message
from extractor import extract_task_or_event
from sensitive_detector import (
    detect_sensitive_information,
    mask_sensitive_information,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

MESSAGES_FILE = DATA_DIR / "messages.csv"
MANDATORY_FILE = DATA_DIR / "mandatory_demo_ids.csv"


# ============================================================
# LOAD MESSAGES
# ============================================================

def load_messages():
    """
    Load the assignment messages and sort them chronologically.
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
            f"Missing columns: {missing_columns}"
        )

    messages["timestamp"] = pd.to_datetime(
        messages["timestamp"]
    )

    messages = (
        messages
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    return messages


# ============================================================
# LOAD MANDATORY IDs
# ============================================================

def load_mandatory_ids():
    """
    Load the 15 mandatory demonstration IDs.

    This function supports a CSV containing a message_id column.
    """

    mandatory = pd.read_csv(
        MANDATORY_FILE
    )

    # --------------------------------------------------------
    # Find message_id column
    # --------------------------------------------------------

    if "message_id" in mandatory.columns:

        ids = mandatory["message_id"]

    else:

        # If the file has a different single-column name,
        # use its first column.
        ids = mandatory.iloc[:, 0]

    ids = (
        ids
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    return ids


# ============================================================
# VALIDATE MANDATORY IDs
# ============================================================

def validate_mandatory_ids(
    messages,
    mandatory_ids
):
    """
    Validate every mandatory ID against the dataset.

    Raw message text is NEVER included in the output.
    """

    message_lookup = {
        str(row["message_id"]): row
        for _, row in messages.iterrows()
    }

    results = []

    for message_id in mandatory_ids:

        # ----------------------------------------------------
        # ID exists?
        # ----------------------------------------------------

        if message_id not in message_lookup:

            results.append(
                {
                    "message_id": message_id,
                    "found": False,
                    "category": None,
                    "confidence": None,
                    "reason": "Message ID not found in dataset.",
                    "item_type": None,
                    "item_title": None,
                    "date_or_deadline": None,
                    "time": None,
                    "person": None,
                    "priority": None,
                    "sensitive_detected": False,
                    "sensitivity_types": [],
                    "risk_levels": [],
                    "masked_text": None,
                }
            )

            continue

        # ----------------------------------------------------
        # Retrieve message
        # ----------------------------------------------------

        row = message_lookup[message_id]

        message = str(
            row["message"]
        )

        sender = str(
            row["sender"]
        )

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        classification = classify_message(
            message_id,
            message
        )

        # ----------------------------------------------------
        # Task/Event extraction
        # ----------------------------------------------------

        extracted = extract_task_or_event(
            message_id=message_id,
            message=message,
            sender=sender,
        )

        # ----------------------------------------------------
        # Sensitive detection
        # ----------------------------------------------------

        detections = detect_sensitive_information(
            message
        )

        sensitive_detected = (
            len(detections) > 0
        )

        sensitivity_types = [
            detection["sensitivity_type"]
            for detection in detections
        ]

        risk_levels = [
            detection["risk"]
            for detection in detections
        ]

        # ----------------------------------------------------
        # Masked text
        # ----------------------------------------------------

        if sensitive_detected:

            masked_text = (
                mask_sensitive_information(
                    message
                )
            )

        else:

            masked_text = None

        # ----------------------------------------------------
        # Extraction fields
        # ----------------------------------------------------

        if extracted:

            item_type = extracted.get(
                "type"
            )

            item_title = extracted.get(
                "title"
            )

            date_or_deadline = extracted.get(
                "date_or_deadline"
            )

            time_value = extracted.get(
                "time"
            )

            person = extracted.get(
                "person"
            )

            priority = extracted.get(
                "priority"
            )

        else:

            item_type = None
            item_title = None
            date_or_deadline = None
            time_value = None
            person = None
            priority = None

        # ----------------------------------------------------
        # Store SAFE result
        # ----------------------------------------------------

        results.append(
            {
                "message_id": message_id,

                "found": True,

                "category": classification.get(
                    "category"
                ),

                "confidence": classification.get(
                    "confidence"
                ),

                "reason": classification.get(
                    "reason"
                ),

                "item_type": item_type,

                "item_title": item_title,

                "date_or_deadline": (
                    date_or_deadline
                ),

                "time": time_value,

                "person": person,

                "priority": priority,

                "sensitive_detected": (
                    sensitive_detected
                ),

                "sensitivity_types": (
                    sensitivity_types
                ),

                "risk_levels": (
                    risk_levels
                ),

                "masked_text": masked_text,
            }
        )

    return results


# ============================================================
# SAVE VALIDATION REPORT
# ============================================================

def save_report(results):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        OUTPUT_DIR /
        "mandatory_validation.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file


# ============================================================
# SAFE TERMINAL SUMMARY
# ============================================================

def print_summary(
    mandatory_ids,
    results
):

    found_count = sum(
        1
        for result in results
        if result["found"]
    )

    missing_count = (
        len(results) - found_count
    )

    print()
    print("=" * 60)
    print("MANDATORY DEMO ID VALIDATION")
    print("=" * 60)

    print(
        f"Required IDs: {len(mandatory_ids)}"
    )

    print(
        f"IDs found: {found_count}"
    )

    print(
        f"IDs missing: {missing_count}"
    )

    print()
    print("Mandatory ID results:")
    print("-" * 60)

    for result in results:

        message_id = result[
            "message_id"
        ]

        if not result["found"]:

            print(
                f"{message_id} | NOT FOUND"
            )

            continue

        category = result[
            "category"
        ]

        confidence = result[
            "confidence"
        ]

        item_type = (
            result["item_type"]
            or "-"
        )

        sensitive = (
            "YES"
            if result["sensitive_detected"]
            else "NO"
        )

        print(
            f"{message_id} | "
            f"{category} | "
            f"confidence={confidence} | "
            f"item={item_type} | "
            f"sensitive={sensitive}"
        )

    print("-" * 60)

    # --------------------------------------------------------
    # Coverage
    # --------------------------------------------------------

    categories = sorted(
        {
            result["category"]
            for result in results
            if result["found"]
            and result["category"]
        }
    )

    print()
    print("Categories represented:")

    for category in categories:

        print(
            f"- {category}"
        )

    print()
    print(
        "Security: raw message text is not "
        "printed by this validation script."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Loading dataset..."
    )

    messages = load_messages()

    print(
        f"Dataset messages: {len(messages)}"
    )

    print(
        "Loading mandatory demo IDs..."
    )

    mandatory_ids = load_mandatory_ids()

    print(
        f"Mandatory IDs loaded: "
        f"{len(mandatory_ids)}"
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    results = validate_mandatory_ids(
        messages,
        mandatory_ids
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    output_file = save_report(
        results
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print_summary(
        mandatory_ids,
        results
    )

    print()
    print(
        f"Validation report saved to:"
    )

    print(
        output_file
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()