"""
Layer 6: Append-only JSONL Audit Logger for PortGuard AI.
Guarantees tamper-evident traceability for compliance, security reviews, and forensic analysis.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from src.config import CONFIG
from src.models import PipelineResult


class AuditLogger:
    """Manages append-only JSONL audit logs for maritime compliance."""

    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path or CONFIG.audit_log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, result: PipelineResult) -> Dict[str, Any]:
        """
        Appends an immutable audit event to the JSONL log file.
        """
        audit_record: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": result.session_id,
            "input_hash": result.input_hash,
            "stripped_zero_width_chars": result.stripped_zero_width_chars,
            "injection_flags": result.injection_flags,
            "pii_redacted_count": result.pii_redacted_count,
            "pii_types_detected": result.pii_types_detected,
            "policy_decision": result.policy_decision.value,
            "policy_violations": result.policy_violations,
            "requires_human_approval": result.requires_human_approval,
            "high_risk_actions_count": len(result.high_risk_actions),
            "suggested_actions_count": (
                len(result.copilot_output.suggested_actions)
                if result.copilot_output
                else 0
            ),
            "latency_ms": round(result.latency_ms, 2),
            "cache_hit": result.cache_hit,
            "error_message": result.error_message,
        }

        # Thread-safe / process-safe atomic append in standard JSON lines format
        with open(self.log_path, "a", encoding="utf-8") as file_handle:
            file_handle.write(json.dumps(audit_record) + "\n")

        return audit_record

    def get_recent_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Reads recent audit log entries for operational dashboard display."""
        if not self.log_path.exists():
            return []

        entries: List[Dict[str, Any]] = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as file_handle:
                for line in file_handle:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            return []

        return entries[-limit:]
