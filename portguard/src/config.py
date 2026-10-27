"""
Configuration management for PortGuard AI.
Loads settings from environment variables using python-dotenv.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env from the project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    # API Credentials & Model
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    model_name: str = os.getenv("PORTGUARD_MODEL", "gemini-2.5-flash").strip()

    # Free-tier & Resilience Settings
    inter_call_delay_seconds: float = float(
        os.getenv("PORTGUARD_INTER_CALL_DELAY_SECONDS", "4.0")
    )
    max_retries: int = int(os.getenv("PORTGUARD_MAX_RETRIES", "4"))
    cache_enabled: bool = (
        os.getenv("PORTGUARD_CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    cache_dir: Path = ROOT_DIR / os.getenv("PORTGUARD_CACHE_DIR", ".cache_portguard")

    # Rate Limiting (Session/Tenant sliding window)
    max_calls_per_minute: int = int(os.getenv("PORTGUARD_MAX_CALLS_PER_MINUTE", "10"))

    # Operational Guards & Bandwidth Adaptation
    max_input_length: int = int(os.getenv("PORTGUARD_MAX_INPUT_LENGTH", "8000"))
    low_bandwidth_mode: bool = (
        os.getenv("PORTGUARD_LOW_BANDWIDTH_MODE", "false").lower()
        in ("true", "1", "yes")
    )

    # Audit Logging
    audit_log_path: Path = ROOT_DIR / os.getenv(
        "PORTGUARD_AUDIT_LOG_PATH", "logs/audit_log.jsonl"
    )

    def validate_api_key(self) -> None:
        """Ensure an API key is present before attempting LLM network calls."""
        if not self.gemini_api_key or self.gemini_api_key == "your-gemini-api-key-here":
            raise ValueError(
                "GEMINI_API_KEY is missing or unconfigured in .env file. "
                "Please configure a valid Google Gemini API key to run live inference."
            )


# Global singleton configuration
CONFIG = AppConfig()
