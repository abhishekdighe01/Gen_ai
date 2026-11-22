"""
Day 13 - Observability, Caching, and Security
==============================================
Latency + token logging, TTL cache, input validation, and prompt-injection defense.
"""

import hashlib
import json
import os
import re
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_INPUT_CHARS = 500
REQUEST_LOG_PATH = Path("data/request_logs.jsonl")

INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions",
    r"disregard\s+(?:all\s+)?(?:previous|above|prior)\s+instructions",
    r"reveal\s+(?:your\s+)?system\s+prompt",
    r"print\s+(?:your\s+)?system\s+prompt",
    r"what\s+is\s+your\s+system\s+prompt",
    r"override\s+(?:safety|rules|instructions)",
    r"act\s+as\s+dan\b",
    r"developer\s+mode\s+enabled",
    r"jailbreak",
]


def estimate_tokens(text: str) -> int:
    """Approximates token count (~4 characters per token for English text)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def validate_user_input(question: str, max_chars: int = MAX_INPUT_CHARS) -> str:
    """
    Validates user input length and blocks prompt-injection attempts.
    Raises ValueError on empty/oversized input and PermissionError on prompt injection.
    """
    if question is None or not str(question).strip():
        raise ValueError("Question cannot be empty.")
    
    cleaned = str(question).strip()
    
    if len(cleaned) > max_chars:
        raise ValueError(
            f"Input exceeds maximum allowed length of {max_chars} characters (got {len(cleaned)})."
        )
    
    lowered = cleaned.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            raise PermissionError(
                "Prompt injection detected: request blocked by SuryaGharSathi security guardrail."
            )
    
    return cleaned


class SimpleTTLCache:
    """Lightweight in-memory LRU + TTL cache for repeated RAG/Agent queries."""
    
    def __init__(self, max_size: int = 128, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    @staticmethod
    def make_key(namespace: str, payload: str) -> str:
        digest = hashlib.sha256(f"{namespace}:{payload.strip().lower()}".encode()).hexdigest()
        return digest[:24]
    
    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        
        if time.time() - entry["created_at"] > self.ttl_seconds:
            del self._store[key]
            self.misses += 1
            return None
        
        self._store.move_to_end(key)
        self.hits += 1
        return entry["value"]
    
    def set(self, key: str, value: Any) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = {"value": value, "created_at": time.time()}
        
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)
    
    def stats(self) -> dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = round((self.hits / total) * 100.0, 1) if total > 0 else 0.0
        return {
            "entries": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": hit_rate,
        }


# Global cache instance
RESPONSE_CACHE = SimpleTTLCache(max_size=128, ttl_seconds=3600)

# In-memory metrics store
_IN_MEMORY_METRICS: list[dict[str, Any]] = []


def log_request_metric(
    endpoint: str,
    latency_ms: float,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    cached: bool = False,
    status_code: int = 200,
) -> dict[str, Any]:
    """Log request metrics to JSONL and in-memory store."""
    record = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "endpoint": endpoint,
        "latency_ms": round(float(latency_ms), 2),
        "prompt_tokens": int(prompt_tokens),
        "completion_tokens": int(completion_tokens),
        "total_tokens": int(prompt_tokens + completion_tokens),
        "cached": bool(cached),
        "status_code": int(status_code),
    }
    
    _IN_MEMORY_METRICS.append(record)
    
    # Write to JSONL file (non-critical, allow silent failure for resilience)
    try:
        os.makedirs(REQUEST_LOG_PATH.parent, exist_ok=True)
        with open(REQUEST_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:  # noqa: S110
        # Intentionally suppress file write errors - metrics still stored in memory
        pass
    
    return record


def get_metrics_summary() -> dict[str, Any]:
    """Get aggregated metrics summary."""
    total_reqs = len(_IN_MEMORY_METRICS)
    avg_latency = (
        round(sum(m["latency_ms"] for m in _IN_MEMORY_METRICS) / total_reqs, 2)
        if total_reqs > 0
        else 0.0
    )
    total_tokens = sum(m["total_tokens"] for m in _IN_MEMORY_METRICS)
    
    return {
        "total_requests": total_reqs,
        "avg_latency_ms": avg_latency,
        "total_tokens": total_tokens,
        "max_input_chars": MAX_INPUT_CHARS,
        "cache": RESPONSE_CACHE.stats(),
    }
