#!/usr/bin/env python3
"""
Scheduled runner for longitudinal deployment.

Runs the full pipeline (the same one as ``run_agent.py``) and appends a compact
record of this run to ``outputs/timeseries.json`` with a UTC timestamp. Point a
cron job / scheduler at this script to build a time series of cross-platform
liquidity and mispricing for trend analysis.

    python run_scheduled.py
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import config
import run_agent

logger = logging.getLogger("liquidity_agent.scheduled")

TIMESERIES = config.OUTPUT_DIR / "timeseries.json"
SUMMARY = config.OUTPUT_DIR / "summary.json"


def _load_series() -> list:
    if TIMESERIES.exists():
        try:
            with open(TIMESERIES, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and isinstance(data.get("runs"), list):
                return data["runs"]
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read existing timeseries (%s); starting fresh", exc)
    return []


def main() -> int:
    pdf_path = run_agent.run()
    record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "report": pdf_path}

    if SUMMARY.exists():
        try:
            with open(SUMMARY, encoding="utf-8") as f:
                record["summary"] = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read summary.json: %s", exc)

    series = _load_series()
    series.append(record)
    with open(TIMESERIES, "w", encoding="utf-8") as f:
        json.dump({"runs": series, "count": len(series)}, f, indent=2, default=str)
    logger.info("Appended run to %s (now %d runs)", TIMESERIES, len(series))
    return 0 if pdf_path else 1


if __name__ == "__main__":
    raise SystemExit(main())
