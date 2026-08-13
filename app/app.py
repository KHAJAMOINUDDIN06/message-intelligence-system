from pathlib import Path
import json

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

CLASSIFICATIONS_FILE = OUTPUTS_DIR / "classifications.csv"
EXTRACTED_ITEMS_FILE = OUTPUTS_DIR / "extracted_items.json"
SENSITIVE_FILE = OUTPUTS_DIR / "sensitive_information.json"
MANDATORY_FILE = OUTPUTS_DIR / "mandatory_validation.json"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Message Intelligence System",
    page_icon="🧠",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🧠 Message Intelligence System")

st.write(
    "A local message-processing system for classification, "
    "task/event extraction, and sensitive-information detection."
)

st.info(
    "Security: Raw source messages are not displayed in this dashboard. "
    "Sensitive information is shown only in masked form."
)


# ============================================================
# LOAD DATA FUNCTIONS
# ============================================================

@st.cache_data
def load_classifications():

    return pd.read_csv(
        CLASSIFICATIONS_FILE
    )


@st.cache_data
def load_extracted_items():

    with open(
        EXTRACTED_ITEMS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


@st.cache_data
def load_sensitive_information():

    with open(
        SENSITIVE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


@st.cache_data
def load_mandatory_validation():

    with open(
        MANDATORY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# LOAD OUTPUT DATA
# ============================================================

classifications = load_classifications()

extracted_items = load_extracted_items()

sensitive_information = load_sensitive_information()

mandatory_validation = load_mandatory_validation()


# ============================================================
# OVERVIEW
# ============================================================

st.header("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Messages Processed",
        len(classifications)
    )

with col2:
    st.metric(
        "Tasks / Events",
        len(extracted_items)
    )

with col3:
    st.metric(
        "Sensitive Detections",
        len(sensitive_information)
    )

with col4:
    st.metric(
        "Mandatory IDs",
        len(mandatory_validation)
    )


# ============================================================
# CLASSIFICATION SUMMARY
# ============================================================

st.header("📋 Classification Summary")

category_counts = (
    classifications["category"]
    .value_counts()
    .reset_index()
)

category_counts.columns = [
    "Category",
    "Count"
]

st.bar_chart(
    category_counts.set_index("Category")
)


# ============================================================
# CLASSIFICATION RESULTS
# ============================================================

st.subheader("Classification Results")

classification_columns = [
    "message_id",
    "category",
    "confidence",
    "reason",
]

classification_display = classifications[
    classification_columns
].copy()

classification_display["confidence"] = (
    classification_display["confidence"]
    .round(2)
)

st.dataframe(
    classification_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# TASK AND EVENT SECTION
# ============================================================

st.header("📅 Tasks and Events")

if extracted_items:

    extracted_df = pd.DataFrame(
        extracted_items
    )

    type_counts = (
        extracted_df["type"]
        .value_counts()
        .reset_index()
    )

    type_counts.columns = [
        "Type",
        "Count"
    ]

    st.bar_chart(
        type_counts.set_index("Type")
    )

    st.subheader("Extracted Items")

    display_columns = [
        "item_id",
        "type",
        "title",
        "date_or_deadline",
        "time",
        "person",
        "priority",
        "source_message_id",
    ]

    st.dataframe(
        extracted_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.warning(
        "No tasks or events were extracted."
    )


# ============================================================
# SENSITIVE INFORMATION
# ============================================================

st.header("🔐 Sensitive Information Detection")

st.warning(
    "Sensitive values are masked. "
    "Raw sensitive values are never displayed."
)

if sensitive_information:

    sensitive_df = pd.DataFrame(
        sensitive_information
    )

    sensitive_columns = [
        "message_id",
        "sensitivity_type",
        "risk",
        "masked_text",
        "recommended_action",
    ]

    sensitive_display = sensitive_df[
        sensitive_columns
    ].copy()

    st.dataframe(
        sensitive_display,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.success(
        "No sensitive information detected."
    )


# ============================================================
# MANDATORY DEMONSTRATION IDs
# ============================================================

st.header("🎯 Mandatory Demonstration IDs")

st.write(
    "The following 15 message IDs were supplied for "
    "the mandatory demonstration."
)

if mandatory_validation:

    mandatory_df = pd.DataFrame(
        mandatory_validation
    )

    mandatory_columns = [
    "message_id",
    "category",
    "confidence",
    "reason",
    "item_type",
    "item_title",
    "date_or_deadline",
    "time",
    "priority",
    "sensitive",
]

    available_columns = [
        column
        for column in mandatory_columns
        if column in mandatory_df.columns
    ]

    st.dataframe(
        mandatory_df[available_columns],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.warning(
        "Mandatory validation results are not available."
    )


# ============================================================
# SYSTEM DESIGN
# ============================================================

st.header("⚙️ System Design")

st.markdown(
    """
### Processing Flow

CSV Dataset
↓
Chronological Processing
↓
Sensitive Information Detection
↓
Message Classification
↓
Task / Meeting / Event Extraction
↓
Structured JSON / CSV Outputs
↓
Streamlit Dashboard

### Security Approach

- Message processing is performed locally.
- Raw messages are not displayed in the dashboard.
- Sensitive values are detected using local pattern-based rules.
- Sensitive values are replaced with masked representations.
- The original dataset remains outside the public GitHub repository.
"""
)


# ============================================================
# LIMITATIONS
# ============================================================

st.header("⚠️ Limitations")

st.markdown(
    """
- The classifier uses rule-based and lightweight ML-style logic.
- Keyword-based extraction can produce generic task titles.
- Ambiguous dates and times are kept unresolved rather than guessed.
- Some promotional messages may contain event/task-like language.
- Sensitive-information detection depends on the configured patterns.
"""
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Message Intelligence System | AI/ML Engineer Intern Assignment"
)