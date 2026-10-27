"""
Layer 1: Input Sanitizer for PortGuard AI.
Strips invisible/zero-width Unicode bypasses, normalizes whitespace,
enforces character length limits, and flags prompt injection signatures in English and French.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Comprehensive set of invisible, zero-width, and directional Unicode characters
ZERO_WIDTH_CHARS = (
    "\u200b"  # Zero-width space
    "\u200c"  # Zero-width non-joiner
    "\u200d"  # Zero-width joiner
    "\ufeff"  # Zero-width no-break space (BOM)
    "\u200e"  # Left-to-right mark
    "\u200f"  # Right-to-left mark
    "\u202a"  # Left-to-right embedding
    "\u202b"  # Right-to-left embedding
    "\u202c"  # Pop directional formatting
    "\u202d"  # Left-to-right override
    "\u202e"  # Right-to-left override
    "\u2060"  # Word joiner
    "\u2061"  # Function application
    "\u2062"  # Invisible times
    "\u2063"  # Invisible separator
    "\u2064"  # Invisible plus
    "\x00"    # Null byte
)

ZERO_WIDTH_REGEX = re.compile(f"[{re.escape(''.join(ZERO_WIDTH_CHARS))}]")

# Injection heuristic rules for Maritime logistics workflows (Bilingual French / English)
INJECTION_SIGNATURES: List[Tuple[str, str]] = [
    # English direct and indirect injection
    (r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", "INJECTION_EN_IGNORE_INSTRUCTIONS"),
    (r"disregard\s+(all\s+)?(previous|safety|system)\s+rules?", "INJECTION_EN_DISREGARD_RULES"),
    (r"(reveal|print|leak|show|output)\s+(your\s+)?(system\s+prompt|instructions|initial\s+prompt)", "INJECTION_EN_SYSTEM_PROMPT_LEAK"),
    (r"you\s+are\s+now\s+(an?\s+)?(unrestricted|dan|developer|root|jailbreak)", "INJECTION_EN_ROLEPLAY_OVERRIDE"),
    (r"bypass\s+(all\s+)?(human|policy|security|guardrail)\s+(review|approval|checks?)", "INJECTION_EN_BYPASS_APPROVAL"),
    (r"approve\s+(release|payment|transfer|delivery)\s+immediately\s+without\s+verification", "INJECTION_EN_FORCED_APPROVAL"),
    (r"new\s+system\s+directive\s*:", "INJECTION_EN_SYSTEM_DIRECTIVE"),
    (r"emergency\s+override\s+code\s*:", "INJECTION_EN_EMERGENCY_OVERRIDE"),
    
    # French direct and indirect injection
    (r"ignore[zr]?\s+(toutes?\s+)?les\s+instructions?\s+pr[ée]c[ée]dentes?", "INJECTION_FR_IGNORE_INSTRUCTIONS"),
    (r"oublie\s+(toutes?\s+)?les\s+consignes?", "INJECTION_FR_FORGET_CONSIGNS"),
    (r"(r[ée]v[èe]le|affiche|donne|partage)\s+(le\s+)?(prompt\s+syst[èe]me|instructions?\s+initiales?)", "INJECTION_FR_SYSTEM_PROMPT_LEAK"),
    (r"tu\s+es\s+maintenant\s+(en\s+mode\s+)?(d[ée]veloppeur|dan|sans\s+filtre|administrateur)", "INJECTION_FR_ROLEPLAY_OVERRIDE"),
    (r"contourne[zr]?\s+(la\s+s[ée]curit[ée]|les\s+r[èe]gles|la\s+politique)", "INJECTION_FR_BYPASS_SECURITY"),
    (r"valide[zr]?\s+(la\s+lib[ée]ration|le\s+virement|le\s+paiement)\s+sans\s+v[ée]rification", "INJECTION_FR_FORCED_APPROVAL"),
    (r"directive\s+prioritaire\s+du\s+si[èe]ge\s*:", "INJECTION_FR_HEADQUARTERS_DIRECTIVE"),
]


class InputSanitizer:
    """Sanitizes untrusted logistics inputs before downstream processing."""

    def __init__(self, max_length: int = 8000) -> None:
        self.max_length = max_length

    def sanitize(self, raw_input: str) -> Tuple[str, int, List[str]]:
        """
        Executes sanitization pipeline:
        1. Strips zero-width and invisible control characters.
        2. Normalizes line breaks and trailing spaces.
        3. Enforces length caps.
        4. Detects injection signatures in French & English.

        Returns:
            Tuple of (sanitized_text, stripped_char_count, list_of_flagged_signatures)
        """
        if not raw_input:
            return "", 0, []

        # Step 1: Count and strip zero-width characters
        matches = ZERO_WIDTH_REGEX.findall(raw_input)
        stripped_count = len(matches)
        cleaned_text = ZERO_WIDTH_REGEX.sub("", raw_input)

        # Step 2: Normalize line endings
        cleaned_text = cleaned_text.replace("\r\n", "\n").replace("\r", "\n")

        # Step 3: Enforce strict length cap
        if len(cleaned_text) > self.max_length:
            cleaned_text = cleaned_text[: self.max_length]

        # Step 4: Scan for injection patterns (case-insensitive)
        flagged_signatures: List[str] = []
        for pattern, sig_id in INJECTION_SIGNATURES:
            if re.search(pattern, cleaned_text, re.IGNORECASE):
                flagged_signatures.append(sig_id)

        return cleaned_text, stripped_count, flagged_signatures
