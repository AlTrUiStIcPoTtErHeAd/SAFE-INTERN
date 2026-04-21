# intake/schema.py
"""
Intake schema for SAFE-INTERN.

Responsibilities:
- Define strict structure for intake output
- Validate required fields
- Normalize missing optional fields
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class IntakeSchema:
    # Core
    clean_text: str

    # Company / contact
    company_name: Optional[str]
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    social_media: List[str]

    # Job info
    job_title: Optional[str]
    job_description: Optional[str]
    location: Optional[str]
    duration: Optional[str]
    compensation: Optional[str]
    start_date: Optional[str]

    # Indicators
    payment_mentions: bool
    payment_required: bool
    payment_amount: Optional[str]

    urgency_mentions: bool
    urgency_phrases: List[str]

    interview_process_described: bool
    communication_channels: List[str]

    # Analysis helpers
    missing_information: List[str]
    unusual_patterns: Dict[str, bool]
    entities: Dict[str, List[str]]

    # Metadata
    input_length: int
    language_detected: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__


# ------------------------------------------------------------------
# BUILDER
# ------------------------------------------------------------------

def build_intake_schema(data: Dict[str, Any]) -> IntakeSchema:
    """
    Build IntakeSchema safely from dict.
    """

    required_keys = [
        "clean_text",
        "payment_mentions",
        "urgency_mentions",
        "input_length"
    ]

    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required intake field: {key}")

    return IntakeSchema(
        clean_text=data["clean_text"],

        company_name=data.get("company_name"),
        contact_person=data.get("contact_person"),
        email=data.get("email"),
        phone=data.get("phone"),
        website=data.get("website"),
        social_media=data.get("social_media", []),

        job_title=data.get("job_title"),
        job_description=data.get("job_description"),
        location=data.get("location"),
        duration=data.get("duration"),
        compensation=data.get("compensation"),
        start_date=data.get("start_date"),

        payment_mentions=data.get("payment_mentions", False),
        payment_required=data.get("payment_required", False),
        payment_amount=data.get("payment_amount"),

        urgency_mentions=data.get("urgency_mentions", False),
        urgency_phrases=data.get("urgency_phrases", []),

        interview_process_described=data.get("interview_process_described", False),
        communication_channels=data.get("communication_channels", []),

        missing_information=data.get("missing_information", []),
        unusual_patterns=data.get("unusual_patterns", {}),
        entities=data.get("entities", {}),

        input_length=data.get("input_length", len(data.get("clean_text", ""))),
        language_detected=data.get("language_detected")
    )
