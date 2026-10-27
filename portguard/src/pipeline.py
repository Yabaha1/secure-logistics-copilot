"""
End-to-End Orchestrator: PortGuard AI Defense-in-Depth Pipeline.
Combines 7 security layers to enforce safe LLM execution for maritime shipping operations.
"""

from __future__ import annotations

import hashlib
import re
import time
from typing import Optional

from src.audit_logger import AuditLogger
from src.config import CONFIG
from src.instruction_data_separator import InstructionDataSeparator
from src.llm_client import GeminiLogisticsClient
from src.models import PipelineResult, PolicyDecision, ShippingCopilotOutput
from src.pii_redactor import PIIRedactor
from src.policy_engine import PolicyEngine
from src.rate_limiter import SessionRateLimiter
from src.sanitizer import InputSanitizer


class PortGuardPipeline:
    """
    Main defensive pipeline for processing untrusted logistics documents.
    Enforces strict zero-trust principles:
    Untrusted Input -> Rate Limiter -> Sanitizer -> PII Redaction ->
    Data Boundary Demarcation -> Cached/Throttled LLM Call ->
    Strict Pydantic Validation -> Policy Engine (Risk Scoring & HITL) ->
    Append-Only Audit Logging.
    """

    def __init__(self) -> None:
        self.config = CONFIG
        self.sanitizer = InputSanitizer(max_length=self.config.max_input_length)
        self.redactor = PIIRedactor()
        self.separator = InstructionDataSeparator()
        self.llm_client = GeminiLogisticsClient()
        self.policy_engine = PolicyEngine()
        self.audit_logger = AuditLogger(self.config.audit_log_path)
        self.rate_limiter = SessionRateLimiter(self.config.max_calls_per_minute)

    def process_document(
        self,
        raw_text: str,
        session_id: str = "default_session",
        low_bandwidth_override: Optional[bool] = None,
    ) -> PipelineResult:
        """
        Executes complete defensive workflow for an incoming shipping document or customer message.
        """
        start_time = time.time()
        input_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

        # Layer 7: Session Rate Limiting Check
        allowed, remaining, wait_secs = self.rate_limiter.check_and_consume(session_id)
        if not allowed:
            latency_ms = (time.time() - start_time) * 1000.0
            result = PipelineResult(
                session_id=session_id,
                input_hash=input_hash,
                sanitized_input="",
                redacted_input="",
                stripped_zero_width_chars=0,
                injection_flags=[],
                pii_redacted_count=0,
                pii_types_detected=[],
                copilot_output=None,
                policy_decision=PolicyDecision.REJECTED_SCHEMA_ERROR,
                policy_violations=[
                    f"Rate limit exceeded for session {session_id}. Please wait {wait_secs:.1f}s before retrying."
                ],
                high_risk_actions=[],
                requires_human_approval=True,
                latency_ms=latency_ms,
                cache_hit=False,
                error_message="HTTP_429_SESSION_RATE_LIMIT_EXCEEDED",
            )
            self.audit_logger.log_event(result)
            return result

        # Layer 1: Input Sanitization (Strip zero-width characters, cap length, scan signatures)
        sanitized_text, stripped_count, injection_flags = self.sanitizer.sanitize(raw_text)

        # Low-Bandwidth Mode: Whitespace compaction to save tokens & payload bytes
        is_low_bandwidth = (
            low_bandwidth_override
            if low_bandwidth_override is not None
            else self.config.low_bandwidth_mode
        )
        if is_low_bandwidth:
            sanitized_text = re.sub(r"[ \t]+", " ", sanitized_text)
            sanitized_text = re.sub(r"\n{3,}", "\n\n", sanitized_text)

        # Layer 2: PII & Financial Credential Redaction (Preserving ISO container IDs)
        redacted_text, pii_count, pii_types = self.redactor.redact(sanitized_text)

        # Layer 3: Instruction / Data Separation (Enclose inside XML tags)
        formatted_prompt = self.separator.build_prompt(redacted_text)

        # Layer 4: LLM Structured Execution (with caching, retry backoff, Pydantic validation)
        copilot_output: Optional[ShippingCopilotOutput] = None
        cache_hit = False
        error_msg: Optional[str] = None
        llm_latency_ms = 0.0

        try:
            copilot_output, cache_hit, llm_latency_ms = (
                self.llm_client.generate_shipping_copilot_output(formatted_prompt)
            )
        except Exception as exc:
            error_msg = str(exc)

        # If LLM execution failed or threw validation error
        if copilot_output is None or error_msg is not None:
            total_latency_ms = (time.time() - start_time) * 1000.0
            result = PipelineResult(
                session_id=session_id,
                input_hash=input_hash,
                sanitized_input=sanitized_text,
                redacted_input=redacted_text,
                stripped_zero_width_chars=stripped_count,
                injection_flags=injection_flags,
                pii_redacted_count=pii_count,
                pii_types_detected=pii_types,
                copilot_output=None,
                policy_decision=PolicyDecision.REJECTED_SCHEMA_ERROR,
                policy_violations=[
                    f"LLM extraction or schema validation rejected: {error_msg}"
                ],
                high_risk_actions=[],
                requires_human_approval=True,
                latency_ms=total_latency_ms,
                cache_hit=cache_hit,
                error_message=error_msg,
            )
            self.audit_logger.log_event(result)
            return result

        # Layer 5: Policy Engine Evaluation (Risk scoring & Human Approval Queue)
        decision, violations, high_risk_actions, requires_human = (
            self.policy_engine.evaluate(copilot_output, injection_flags, pii_types)
        )

        total_latency_ms = (time.time() - start_time) * 1000.0

        # Construct final audit artifact
        final_result = PipelineResult(
            session_id=session_id,
            input_hash=input_hash,
            sanitized_input=sanitized_text,
            redacted_input=redacted_text,
            stripped_zero_width_chars=stripped_count,
            injection_flags=injection_flags,
            pii_redacted_count=pii_count,
            pii_types_detected=pii_types,
            copilot_output=copilot_output,
            policy_decision=decision,
            policy_violations=violations,
            high_risk_actions=high_risk_actions,
            requires_human_approval=requires_human,
            latency_ms=total_latency_ms,
            cache_hit=cache_hit,
            error_message=None,
        )

        # Layer 6: Append-Only Immutable Audit Log
        self.audit_logger.log_event(final_result)

        return final_result
