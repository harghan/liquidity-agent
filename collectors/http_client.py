"""
Resilient JSON HTTP client shared by the collectors.

Provides retry with exponential backoff, per-call timestamped logging, and a
session with sensible defaults. Every outbound request is logged so the run is
fully auditable, and transient failures never crash the pipeline — callers get
``None`` and decide how to degrade.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests

import config

logger = logging.getLogger("liquidity_agent.http")

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        s.headers.update({"User-Agent": config.HTTP_USER_AGENT, "Accept": "application/json"})
        _session = s
    return _session


def get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    context: str = "",
) -> Optional[Any]:
    """GET ``url`` and return parsed JSON, or ``None`` on persistent failure.

    Retries transient errors (timeouts, connection errors, 5xx, 429) with
    exponential backoff up to ``config.HTTP_MAX_RETRIES``. Redirects are
    followed (Kalshi 301-redirects trailing-slash paths).
    """
    session = _get_session()
    label = context or url
    last_error: Optional[str] = None

    for attempt in range(1, config.HTTP_MAX_RETRIES + 1):
        started = time.time()
        try:
            resp = session.get(
                url,
                params=params,
                timeout=config.HTTP_TIMEOUT,
                allow_redirects=True,
            )
            elapsed = time.time() - started
            if resp.status_code == 200:
                logger.info("GET %s -> 200 (%.2fs, attempt %d)", label, elapsed, attempt)
                try:
                    return resp.json()
                except ValueError as exc:
                    logger.error("GET %s returned non-JSON body: %s", label, exc)
                    return None

            # Retry on rate limiting / server errors; fail fast on other 4xx.
            if resp.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {resp.status_code}"
                logger.warning(
                    "GET %s -> %d (%.2fs, attempt %d/%d) — retrying",
                    label, resp.status_code, elapsed, attempt, config.HTTP_MAX_RETRIES,
                )
            else:
                logger.error("GET %s -> %d (%.2fs) — not retryable", label, resp.status_code, elapsed)
                return None

        except requests.RequestException as exc:
            last_error = str(exc)
            logger.warning(
                "GET %s failed (attempt %d/%d): %s",
                label, attempt, config.HTTP_MAX_RETRIES, exc,
            )

        if attempt < config.HTTP_MAX_RETRIES:
            backoff = config.HTTP_BACKOFF_BASE ** attempt
            time.sleep(backoff)

    logger.error("GET %s exhausted retries (%s)", label, last_error)
    return None
