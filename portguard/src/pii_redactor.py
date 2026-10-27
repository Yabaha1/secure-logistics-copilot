"""
Layer 2: PII Redactor for PortGuard AI.
Redacts personal and financial identifiers before passing data to the LLM,
while strictly preserving maritime domain identifiers (ISO container numbers, B/L refs).
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple


class PIIRedactor:
    """Masks sensitive PII and financial credentials in shipping documentation."""

    def __init__(self) -> None:
        # Standard email pattern
        self.email_pattern = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
        )

        # West African (Ivory Coast +225, Senegal +221, etc.) & European/International phone patterns
        # Must not match ISO container IDs like MSKU 123456-7
        self.phone_pattern = re.compile(
            r"(?:\+?225[\s.-]?)?(?:0[157]\d{8}|(?:\+?221|\+?33|\+?1|\+?44)[\s.-]?(?:\d{1,4}[\s.-]?){2,4}\d{2,4})\b"
        )

        # International Bank Account Number (IBAN) format (e.g. CI61... or FR76...)
        self.iban_pattern = re.compile(
            r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
            re.IGNORECASE
        )

        # Passport and National ID identifiers
        self.id_pattern = re.compile(
            r"\b(?:PASSPORT|PASSEPORT|CNI|ID\s*CARD|CARTE\s*D'IDENTIT[ÉE])\s*[:#]?\s*([A-Z0-9]{6,12})\b",
            re.IGNORECASE
        )

        # Credit card PAN pattern
        self.credit_card_pattern = re.compile(
            r"\b(?:\d{4}[ -]?){3}\d{4}\b"
        )

        # Maritime Container ID guard pattern (ISO 6346: 4 letters + 7 digits)
        # We ensure container numbers are NEVER redacted as phones or card numbers
        self.container_pattern = re.compile(
            r"\b[A-Z]{4}\d{7}\b",
            re.IGNORECASE
        )

    def redact(self, text: str) -> Tuple[str, int, List[str]]:
        """
        Scans and redacts PII while preserving container numbers.

        Returns:
            Tuple of (redacted_text, total_redactions_count, list_of_detected_types)
        """
        if not text:
            return "", 0, []

        redacted = text
        detected_types: List[str] = []
        total_redactions = 0

        # Temporarily protect ISO container IDs
        container_tokens: Dict[str, str] = {}
        for idx, match in enumerate(self.container_pattern.finditer(redacted)):
            token = f"__CONTAINER_PROTECTED_{idx}__"
            val = match.group(0)
            container_tokens[token] = val
            redacted = redacted.replace(val, token, 1)

        # 1. Redact IBAN / Bank accounts
        iban_matches = list(self.iban_pattern.finditer(redacted))
        if iban_matches:
            detected_types.append("BANK_IBAN")
            total_redactions += len(iban_matches)
            redacted = self.iban_pattern.sub("[IBAN_REDACTED]", redacted)

        # 2. Redact Credit Card PANs
        card_matches = list(self.credit_card_pattern.finditer(redacted))
        if card_matches:
            detected_types.append("CREDIT_CARD")
            total_redactions += len(card_matches)
            redacted = self.credit_card_pattern.sub("[CARD_REDACTED]", redacted)

        # 3. Redact Emails
        email_matches = list(self.email_pattern.finditer(redacted))
        if email_matches:
            detected_types.append("EMAIL_ADDRESS")
            total_redactions += len(email_matches)
            redacted = self.email_pattern.sub("[EMAIL_REDACTED]", redacted)

        # 4. Redact Passports and National IDs
        def id_replacer(match: re.Match) -> str:
            prefix = match.group(0).split(match.group(1))[0]
            return f"{prefix}[GOV_ID_REDACTED]"

        id_matches = list(self.id_pattern.finditer(redacted))
        if id_matches:
            detected_types.append("IDENTITY_DOCUMENT")
            total_redactions += len(id_matches)
            redacted = self.id_pattern.sub(id_replacer, redacted)

        # 5. Redact Phone numbers
        phone_matches = list(self.phone_pattern.finditer(redacted))
        if phone_matches:
            detected_types.append("PHONE_NUMBER")
            total_redactions += len(phone_matches)
            redacted = self.phone_pattern.sub("[PHONE_REDACTED]", redacted)

        # Restore protected container IDs
        for token, val in container_tokens.items():
            redacted = redacted.replace(token, val)

        return redacted, total_redactions, detected_types
