"""
Pydantic v2 domain schemas for PortGuard AI.
Enforces strict schema compliance with extra='forbid' to eliminate hallucinated fields.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentType(str, Enum):
    BILL_OF_LADING = "BILL_OF_LADING"
    BOOKING_CONFIRMATION = "BOOKING_CONFIRMATION"
    CUSTOMER_EMAIL = "CUSTOMER_EMAIL"
    DELIVERY_ORDER = "DELIVERY_ORDER"
    COMMERCIAL_INVOICE = "COMMERCIAL_INVOICE"
    UNKNOWN = "UNKNOWN"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PolicyDecision(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED_INJECTION = "BLOCKED_INJECTION"
    REQUIRES_HUMAN_APPROVAL = "REQUIRES_HUMAN_APPROVAL"
    REJECTED_SCHEMA_ERROR = "REJECTED_SCHEMA_ERROR"


class ActionType(str, Enum):
    UPDATE_DELIVERY_ADDRESS = "UPDATE_DELIVERY_ADDRESS"
    CHANGE_BANK_DETAILS = "CHANGE_BANK_DETAILS"
    RELEASE_CONTAINER = "RELEASE_CONTAINER"
    CONFIRM_BOOKING = "CONFIRM_BOOKING"
    SEND_NOTIFICATION = "SEND_NOTIFICATION"
    ROUTINE_STATUS_UPDATE = "ROUTINE_STATUS_UPDATE"
    REQUEST_DOCUMENTATION = "REQUEST_DOCUMENTATION"


class ExtractedShippingData(BaseModel):
    """Normalized logistics entities extracted from documents."""

    model_config = ConfigDict(extra="forbid")

    booking_reference: Optional[str] = Field(
        None, description="Booking or Bill of Lading reference number (e.g. BK-ABJ-8912)"
    )
    container_numbers: List[str] = Field(
        default_factory=list,
        description="ISO 6346 container identification numbers (e.g. MSKU9012345)",
    )
    vessel_name: Optional[str] = Field(
        None, description="Vessel / feeder name (e.g. CMA CGM DAKAR)"
    )
    port_of_loading: Optional[str] = Field(
        None, description="Origin port name or UN/LOCODE (e.g. Abidjan, CIABJ)"
    )
    port_of_discharge: Optional[str] = Field(
        None, description="Destination port name or UN/LOCODE (e.g. Le Havre, FRLEH)"
    )
    shipper_name: Optional[str] = Field(
        None, description="Name of the shipping company or exporter"
    )
    consignee_name: Optional[str] = Field(
        None, description="Recipient company or importer"
    )
    cargo_description: Optional[str] = Field(
        None, description="Type of goods (e.g. Fèves de cacao / Cocoa beans)"
    )
    declared_weight_kg: Optional[float] = Field(
        None, description="Gross cargo weight in kilograms"
    )
    estimated_arrival: Optional[str] = Field(
        None, description="Estimated time of arrival (ETA) if specified"
    )


class SuggestedAction(BaseModel):
    """Potential downstream operational action suggested by copilot."""

    model_config = ConfigDict(extra="forbid")

    action_type: ActionType = Field(
        ..., description="Specific, controlled operational action"
    )
    target_entity: str = Field(
        ..., description="Target entity impacted (e.g., container ID, booking ref)"
    )
    details: str = Field(
        ..., description="Concise description of the recommended action"
    )
    risk_level: RiskLevel = Field(
        ..., description="Initial model-assessed operational risk level"
    )
    justification: str = Field(
        ..., description="Rationale for recommending this action"
    )


class ShippingCopilotOutput(BaseModel):
    """
    Strict validated schema for LLM structured output.
    Any unknown fields cause immediate validation rejection.
    """

    model_config = ConfigDict(extra="forbid")

    document_type: DocumentType = Field(..., description="Categorized document type")
    language: str = Field(
        ..., description="Primary language of the document ('fr' or 'en')"
    )
    summary: str = Field(
        ..., description="Factual, neutral summary of the document contents"
    )
    extracted_data: ExtractedShippingData = Field(
        ..., description="Extracted logistics entities"
    )
    suggested_actions: List[SuggestedAction] = Field(
        default_factory=list,
        description="Suggested actions strictly requiring downstream policy validation",
    )
    draft_reply_fr: str = Field(
        ..., description="Professional draft reply in French for West African logistics"
    )
    draft_reply_en: str = Field(
        ..., description="Professional draft reply in English for international maritime"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Self-evaluated extraction confidence between 0.0 and 1.0",
    )


class PipelineResult(BaseModel):
    """Complete end-to-end audit artifact for a single processed document."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    input_hash: str
    sanitized_input: str
    redacted_input: str
    stripped_zero_width_chars: int
    injection_flags: List[str]
    pii_redacted_count: int
    pii_types_detected: List[str]
    copilot_output: Optional[ShippingCopilotOutput] = None
    policy_decision: PolicyDecision
    policy_violations: List[str] = Field(default_factory=list)
    high_risk_actions: List[SuggestedAction] = Field(default_factory=list)
    requires_human_approval: bool
    latency_ms: float
    cache_hit: bool
    error_message: Optional[str] = None
