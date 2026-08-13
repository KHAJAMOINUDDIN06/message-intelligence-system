from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.classifier import classify_message
from app.extractor import extract_task_or_event
from app.sensitive_detector import analyze_message as analyze_sensitive


app = FastAPI(
    title="Message Intelligence System API",
    description="REST API for analyzing and classifying messages.",
    version="1.0.0",
)


# ============================================================
# REQUEST MODEL
# ============================================================

class MessageRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="Message text to analyze.",
    )

    sender: Optional[str] = Field(
        default=None,
        description="Optional sender name.",
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Message Intelligence System API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ============================================================
# MESSAGE ANALYSIS
# ============================================================

@app.post("/analyze")
def analyze_message(request: MessageRequest):
    """
    Analyze one message using the existing intelligence
    components.
    """

    message = request.message.strip()
    sender = request.sender

    # --------------------------------------------------------
    # Temporary API message ID
    # --------------------------------------------------------

    message_id = "API_MESSAGE_001"

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classification = classify_message(
        message_id=message_id,
        message=message,
    )

    # --------------------------------------------------------
    # Task/Event Extraction
    # --------------------------------------------------------

    extracted = extract_task_or_event(
        message_id=message_id,
        message=message,
        sender=sender,
    )

    # --------------------------------------------------------
    # Sensitive Information Analysis
    # --------------------------------------------------------

    sensitive_analysis = analyze_sensitive(
        message_id=message_id,
        message=message,
    )

    # --------------------------------------------------------
    # Safe API Response
    # --------------------------------------------------------

    return {
        "message_id": message_id,

        "classification": classification,

        "extracted_item": extracted,

        "sensitive_information": sensitive_analysis,

        "validation": {
            "message_valid": True,
            "message_length": len(message),
        },
    }