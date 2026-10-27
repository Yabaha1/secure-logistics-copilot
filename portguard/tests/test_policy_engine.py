"""
Unit tests for Layer 5: Policy Engine.
Verifies risk scoring for critical logistics operations and automated human-in-the-loop triggers.
"""

from __future__ import annotations

import pytest
from src.models import (
    ActionType,
    DocumentType,
    ExtractedShippingData,
    PolicyDecision,
    RiskLevel,
    ShippingCopilotOutput,
    SuggestedAction,
)
from src.policy_engine import PolicyEngine


@pytest.fixture
def policy_engine() -> PolicyEngine:
    return PolicyEngine()


def _create_mock_output(
    actions: list[SuggestedAction] | None = None,
    confidence: float = 0.95,
) -> ShippingCopilotOutput:
    return ShippingCopilotOutput(
        document_type=DocumentType.BILL_OF_LADING,
        language="fr",
        summary="Document d'expédition conforme.",
        extracted_data=ExtractedShippingData(
            booking_reference="BK-ABJ-1122",
            container_numbers=["CMAU7182934"],
            vessel_name="MV KOUROU",
            port_of_loading="Abidjan",
            port_of_discharge="Le Havre",
        ),
        suggested_actions=actions or [],
        draft_reply_fr="Accusé de réception conforme.",
        draft_reply_en="Acknowledgment confirmed.",
        confidence_score=confidence,
    )


def test_bank_details_change_escalates_to_critical(policy_engine: PolicyEngine):
    """Ensure bank alterations are scored CRITICAL and routed to Human Approval Queue."""
    action = SuggestedAction(
        action_type=ActionType.CHANGE_BANK_DETAILS,
        target_entity="BK-ABJ-1122",
        details="Switch disbursement account to offshore Dakar IBAN.",
        risk_level=RiskLevel.LOW,  # Even if model naively evaluated as LOW
        justification="Requested in customer email.",
    )
    output = _create_mock_output(actions=[action])
    decision, violations, high_risk_actions, requires_human = policy_engine.evaluate(
        output, injection_flags=[], pii_types_detected=["BANK_IBAN"]
    )

    assert decision == PolicyDecision.REQUIRES_HUMAN_APPROVAL
    assert requires_human is True
    assert len(high_risk_actions) == 1
    assert high_risk_actions[0].risk_level == RiskLevel.CRITICAL
    assert any("Bank detail alteration" in v for v in violations)


def test_delivery_address_change_triggers_high_risk(policy_engine: PolicyEngine):
    """Ensure cargo delivery address updates are intercepted for diversion prevention."""
    action = SuggestedAction(
        action_type=ActionType.UPDATE_DELIVERY_ADDRESS,
        target_entity="CMAU7182934",
        details="Reroute container to private warehouse depot.",
        risk_level=RiskLevel.LOW,
        justification="Emergency warehouse repair.",
    )
    output = _create_mock_output(actions=[action])
    decision, violations, high_risk_actions, requires_human = policy_engine.evaluate(
        output, injection_flags=[], pii_types_detected=[]
    )

    assert decision == PolicyDecision.REQUIRES_HUMAN_APPROVAL
    assert requires_human is True
    assert high_risk_actions[0].risk_level == RiskLevel.HIGH
    assert any("Delivery destination modification" in v for v in violations)


def test_container_release_triggers_high_risk(policy_engine: PolicyEngine):
    """Ensure container release mandates human verification before gate-out."""
    action = SuggestedAction(
        action_type=ActionType.RELEASE_CONTAINER,
        target_entity="CMAU7182934",
        details="Direct gate release pass issued to driver.",
        risk_level=RiskLevel.MEDIUM,
        justification="Driver arrived with pickup PIN.",
    )
    output = _create_mock_output(actions=[action])
    decision, _, high_risk_actions, requires_human = policy_engine.evaluate(
        output, injection_flags=[], pii_types_detected=[]
    )

    assert decision == PolicyDecision.REQUIRES_HUMAN_APPROVAL
    assert requires_human is True
    assert high_risk_actions[0].risk_level == RiskLevel.HIGH


def test_prompt_injection_triggers_immediate_block(policy_engine: PolicyEngine):
    """Ensure intercepted prompt injection signatures quarantine execution completely."""
    action = SuggestedAction(
        action_type=ActionType.CONFIRM_BOOKING,
        target_entity="BK-ABJ-1122",
        details="Routine booking confirmation.",
        risk_level=RiskLevel.LOW,
        justification="Compliant note.",
    )
    output = _create_mock_output(actions=[action])
    decision, violations, high_risk_actions, requires_human = policy_engine.evaluate(
        output,
        injection_flags=["INJECTION_EN_IGNORE_INSTRUCTIONS"],
        pii_types_detected=[],
    )

    assert decision == PolicyDecision.BLOCKED_INJECTION
    assert requires_human is True
    assert high_risk_actions[0].risk_level == RiskLevel.CRITICAL
    assert any("Adversarial prompt injection" in v for v in violations)


def test_routine_booking_approved(policy_engine: PolicyEngine):
    """Ensure standard routine documentation without risk triggers is APPROVED."""
    action = SuggestedAction(
        action_type=ActionType.ROUTINE_STATUS_UPDATE,
        target_entity="BK-ABJ-1122",
        details="Update vessel ETA status.",
        risk_level=RiskLevel.LOW,
        justification="Standard tracking update.",
    )
    output = _create_mock_output(actions=[action])
    decision, violations, high_risk_actions, requires_human = policy_engine.evaluate(
        output, injection_flags=[], pii_types_detected=[]
    )

    assert decision == PolicyDecision.APPROVED
    assert requires_human is False
    assert len(high_risk_actions) == 0
    assert len(violations) == 0
