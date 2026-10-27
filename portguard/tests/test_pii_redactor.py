"""
Unit tests for Layer 2: PII Redactor.
Verifies sensitive identity and banking redaction while strictly protecting ISO container numbers.
"""

from __future__ import annotations

import pytest
from src.pii_redactor import PIIRedactor


@pytest.fixture
def redactor() -> PIIRedactor:
    return PIIRedactor()


def test_email_redaction(redactor: PIIRedactor):
    """Ensure contact emails are redacted."""
    raw = "Shipper contact is export.officer@sinc-cacao.ci for documentation."
    redacted, count, types = redactor.redact(raw)

    assert "[EMAIL_REDACTED]" in redacted
    assert "export.officer@sinc-cacao.ci" not in redacted
    assert "EMAIL_ADDRESS" in types
    assert count == 1


def test_phone_number_redaction(redactor: PIIRedactor):
    """Ensure West African and European phone numbers are masked."""
    raw = "Call Abidjan agency at +225 07 48 99 21 00 or Paris desk at +33 1 42 68 00 00."
    redacted, count, types = redactor.redact(raw)

    assert "[PHONE_REDACTED]" in redacted
    assert "+225" not in redacted
    assert "PHONE_NUMBER" in types
    assert count >= 2


def test_bank_iban_redaction(redactor: PIIRedactor):
    """Ensure bank account IBANs (Ivorian, French, Senegalese) are sanitized."""
    raw = "Beneficiary bank account: CI61 0012 3456 7890 1234 5678 901 for settlement."
    redacted, count, types = redactor.redact(raw)

    assert "[IBAN_REDACTED]" in redacted
    assert "CI61" not in redacted
    assert "BANK_IBAN" in types
    assert count == 1


def test_identity_document_redaction(redactor: PIIRedactor):
    """Ensure government IDs and passports are masked."""
    raw = "Signatory Amadou Touré with PASSEPORT: C01928341 and CNI: 009281729."
    redacted, count, types = redactor.redact(raw)

    assert "[GOV_ID_REDACTED]" in redacted
    assert "C01928341" not in redacted
    assert "IDENTITY_DOCUMENT" in types


def test_container_numbers_strictly_preserved(redactor: PIIRedactor):
    """
    CRITICAL DOMAIN GUARD:
    ISO 6346 shipping container IDs (e.g. MSKU4412098, CMAU7182934) must NEVER
    be misclassified as phone numbers, card numbers, or IDs.
    """
    raw = """B/L BL-ABJ-90412
Containers to discharge:
- CMAU7182934 (Dry High Cube)
- MSKU4412098 (Reefer)
- TGHU8912340 (Standard)
Consignee email: imports@europe-choc.fr
Disbursement IBAN: FR76 3000 6000 0112 3456 7890 189"""

    redacted, count, types = redactor.redact(raw)

    # Maritime container numbers must be 100% intact
    assert "CMAU7182934" in redacted
    assert "MSKU4412098" in redacted
    assert "TGHU8912340" in redacted

    # PII must be redacted
    assert "[EMAIL_REDACTED]" in redacted
    assert "[IBAN_REDACTED]" in redacted
    assert "imports@europe-choc.fr" not in redacted
