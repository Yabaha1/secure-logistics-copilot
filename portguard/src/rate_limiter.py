"""
Layer 7: In-memory sliding-window Rate Limiter for PortGuard AI.
Guarantees fair resource allocation and shields free-tier APIs from session bursts and DoS floods.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from typing import Dict, List, Tuple

from src.config import CONFIG


class SessionRateLimiter:
    """Sliding-window rate limiter tracking requests per session identifier."""

    def __init__(self, max_calls_per_minute: int | None = None) -> None:
        self.max_calls = max_calls_per_minute or CONFIG.max_calls_per_minute
        self.window_seconds = 60.0
        self._history: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check_and_consume(self, session_id: str) -> Tuple[bool, int, float]:
        """
        Evaluates whether a request from session_id is permitted under the rate limit.

        Returns:
            Tuple of:
            - allowed: bool (True if call permitted, False if rate-limited)
            - remaining_calls: int (number of available calls in current window)
            - wait_seconds: float (seconds until earliest token frees up if blocked)
        """
        now = time.time()
        window_start = now - self.window_seconds

        with self._lock:
            # Purge timestamps outside the 60-second sliding window
            valid_timestamps = [ts for ts in self._history[session_id] if ts > window_start]
            self._history[session_id] = valid_timestamps

            if len(valid_timestamps) >= self.max_calls:
                oldest_ts = valid_timestamps[0]
                wait_seconds = max(0.1, (oldest_ts + self.window_seconds) - now)
                return False, 0, wait_seconds

            # Consume 1 request quota
            self._history[session_id].append(now)
            remaining = self.max_calls - len(self._history[session_id])
            return True, remaining, 0.0

    def reset_session(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._history:
                del self._history[session_id]
