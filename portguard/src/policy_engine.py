"""
Layer 5: Policy Engine & Risk Scorer for PortGuard AI.
Enforces maritime risk governance, overrides model confidence when sensitive operations are detected,
and mandates Human-in-the-Loop (HITL) approval for critical logistics actions.
"""

from __future__ import annotations

from typing import List, Tuple

from src.models import (
    ActionType,
    PolicyDecision,
    RiskLevel,
    ShippingCopilotOutput,
    SuggestedAction,
)

# High-risk maritime actions that MUST trigger human review
CRITICAL_LOGISTICS_ACTIONS = {
    ActionType.CHANGE_BANK_DETAILS: (
        RiskLevel.CRITICAL,
        "Bank detail alteration detected: High-frequency maritime wire fraud attack vector."
    ),
    ActionType.UPDATE_DELIVERY_ADDRESS: (
        RiskLevel.HIGH,
        "Delivery destination modification: Cargo diversion and port theft risk."
    ),
    ActionType.RELEASE_CONTAINER: (
        RiskLevel.HIGH,
        "Container gate release authorization: Irreversible custody transfer requiring bill of lading verification."
    ),
}


class PolicyEngine:
    """Enforces non-negotiable security and business logic policies on copilot outputs."""

    def evaluate(
        self,
        copilot_output: ShippingCopilotOutput,
        injection_flags: List[str],
        pii_types_detected: List[str],
    ) -> Tuple[PolicyDecision, List[str], List[SuggestedAction], bool]:
        """
        Evaluates model proposals against organizational policies.

        Returns:
            Tuple of:
            - PolicyDecision: APPROVED, BLOCKED_INJECTION, or REQUIRES_HUMAN_APPROVAL
            - policy_violations: List of specific policy violations or flags
            - high_risk_actions: List of actions escalated to human approval
            - requires_human_approval: Boolean flag
        """
        violations: List[str] = []
        high_risk_actions: List[SuggestedAction] = []

        # Policy Rule 1: Injection containment
        # If the input contained adversarial injection patterns, reject direct execution
        if injection_flags:
            violations.append(
                f"Adversarial prompt injection pattern(s) intercepted in input: {', '.join(injection_flags)}. "
                "All automated actions suspended."
            )
            # Escalate every suggested action to CRITICAL
            for action in copilot_output.suggested_actions:
                action.risk_level = RiskLevel.CRITICAL
                high_risk_actions.append(action)
            return PolicyDecision.BLOCKED_INJECTION, violations, high_risk_actions, True

        # Policy Rule 2: Maritime fraud & diversion risk scoring
        for action in copilot_output.suggested_actions:
            if action.action_type in CRITICAL_LOGISTICS_ACTIONS:
                enforced_risk, policy_reason = CRITICAL_LOGISTICS_ACTIONS[action.action_type]
                # Enforce minimum risk level defined by policy, overriding any lenient model assessment
                action.risk_level = enforced_risk
                violations.append(
                    f"Action '{action.action_type.value}' intercepted: {policy_reason}"
                )
                high_risk_actions.append(action)
            elif action.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
                violations.append(
                    f"Model-flagged high risk action: '{action.action_type.value}' on '{action.target_entity}'"
                )
                high_risk_actions.append(action)

        # Policy Rule 3: Low confidence threshold
        if copilot_output.confidence_score < 0.70:
            violations.append(
                f"Extraction confidence ({copilot_output.confidence_score:.2f}) below operational threshold (0.70)."
            )

        requires_human = len(high_risk_actions) > 0 or len(violations) > 0

        decision = (
            PolicyDecision.REQUIRES_HUMAN_APPROVAL
            if requires_human
            else PolicyDecision.APPROVED
        )

        return decision, violations, high_risk_actions, requires_human
