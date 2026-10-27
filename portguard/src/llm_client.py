"""
Layer 4: Resilient LLM Client with Caching, Backoff, and Schema Enforcement.
Uses the modern google-genai SDK, respects free-tier rate limits, and validates output against Pydantic models.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional, Tuple

from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import ValidationError

from src.config import CONFIG
from src.instruction_data_separator import InstructionDataSeparator
from src.models import ShippingCopilotOutput

logger = logging.getLogger(__name__)


class GeminiLogisticsClient:
    """Production client wrapping Gemini API with resilience, caching, and rate limit protections."""

    def __init__(self) -> None:
        self.config = CONFIG
        self._client: Optional[genai.Client] = None
        self._last_call_timestamp: float = 0.0

        if self.config.cache_enabled:
            self.config.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def client(self) -> genai.Client:
        """Lazy-loaded Gemini client instance with validated credentials."""
        if self._client is None:
            self.config.validate_api_key()
            self._client = genai.Client(api_key=self.config.gemini_api_key)
        return self._client

    def _get_cache_path(self, cache_key: str) -> Path:
        return self.config.cache_dir / f"{cache_key}.json"

    def _read_from_cache(self, cache_key: str) -> Optional[str]:
        if not self.config.cache_enabled:
            return None
        cache_file = self._get_cache_path(cache_key)
        if cache_file.exists():
            try:
                return cache_file.read_text(encoding="utf-8")
            except Exception as err:
                logger.warning(f"Cache read failed for key {cache_key}: {err}")
        return None

    def _write_to_cache(self, cache_key: str, content: str) -> None:
        if not self.config.cache_enabled:
            return
        try:
            cache_file = self._get_cache_path(cache_key)
            cache_file.write_text(content, encoding="utf-8")
        except Exception as err:
            logger.warning(f"Cache write failed for key {cache_key}: {err}")

    def _throttle_call(self) -> None:
        """Enforces minimum inter-call delay to prevent free-tier 429 quota exhaustion."""
        elapsed = time.time() - self._last_call_timestamp
        required_delay = self.config.inter_call_delay_seconds
        if elapsed < required_delay:
            time.sleep(required_delay - elapsed)

    def generate_shipping_copilot_output(
        self, prompt_text: str
    ) -> Tuple[ShippingCopilotOutput, bool, float]:
        """
        Executes structured inference with caching, exponential backoff, and Pydantic validation.

        Returns:
            Tuple of (ShippingCopilotOutput, cache_hit_bool, latency_ms)
        """
        start_time = time.time()

        # Cache key combines model name and prompt digest
        digest = hashlib.sha256(
            f"{self.config.model_name}:{prompt_text}".encode("utf-8")
        ).hexdigest()

        # 1. Check local disk cache
        cached_raw = self._read_from_cache(digest)
        if cached_raw:
            try:
                parsed = ShippingCopilotOutput.model_validate_json(cached_raw)
                latency_ms = (time.time() - start_time) * 1000.0
                return parsed, True, latency_ms
            except ValidationError as val_err:
                logger.warning(f"Corrupt cache entry invalidated for {digest}: {val_err}")

        # 2. Free-tier pacing
        self._throttle_call()

        # 3. Call Gemini API with exponential backoff on HTTP 429 / 503
        system_instruction = InstructionDataSeparator.get_system_instruction()
        raw_response_text = ""
        backoff_seconds = 2.0

        for attempt in range(self.config.max_retries):
            try:
                self._last_call_timestamp = time.time()
                response = self.client.models.generate_content(
                    model=self.config.model_name,
                    contents=prompt_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        temperature=0.1,  # Low temperature for deterministic logistics extraction
                    ),
                )
                raw_response_text = response.text or "{}"
                break
            except APIError as api_err:
                # Catch 429 (ResourceExhausted) or 503 (Unavailable)
                is_rate_limit = "429" in str(api_err) or "RESOURCE_EXHAUSTED" in str(api_err)
                is_server_error = "503" in str(api_err) or "UNAVAILABLE" in str(api_err)

                if (is_rate_limit or is_server_error) and attempt < self.config.max_retries - 1:
                    logger.warning(
                        f"API Rate limit or transient error encountered (attempt {attempt + 1}). "
                        f"Retrying in {backoff_seconds:.1f}s... Error: {api_err}"
                    )
                    time.sleep(backoff_seconds)
                    backoff_seconds *= 2.0
                else:
                    raise api_err
            except Exception as unk_err:
                raise unk_err

        # 4. Strip any stray markdown fences if the model included them despite json mode
        clean_json_str = raw_response_text.strip()
        if clean_json_str.startswith("```json"):
            clean_json_str = clean_json_str[7:]
        elif clean_json_str.startswith("```"):
            clean_json_str = clean_json_str[3:]
        if clean_json_str.endswith("```"):
            clean_json_str = clean_json_str[:-3]
        clean_json_str = clean_json_str.strip()

        # 5. Strict schema validation (reject unknown fields and invalid structures)
        try:
            validated_output = ShippingCopilotOutput.model_validate_json(clean_json_str)
        except ValidationError as val_err:
            raise ValueError(
                f"Strict schema validation failed against ShippingCopilotOutput: {val_err}"
            ) from val_err

        # 6. Save valid output to cache
        self._write_to_cache(digest, clean_json_str)

        latency_ms = (time.time() - start_time) * 1000.0
        return validated_output, False, latency_ms
