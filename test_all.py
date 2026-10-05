#!/usr/bin/env python3
"""
EventRoute // Enterprise Test Verification Suite.
Run directly to execute all institutional quantitative and microstructure tests:
    python3 test_all.py
"""

import sys
from pathlib import Path

# Ensure project root is first in path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tests.test_sor import TestSmartOrderRouter
from tests.test_matcher import TestMatcherSafety
from tests.test_parity import TestParityEngine


def run_all():
    print("=" * 70)
    print("EVENTROUTE // INSTITUTIONAL QUANTITATIVE TEST SUITE")
    print("=" * 70)

    # 1. Smart Order Router Tests
    print("\n[1/3] Running Smart Order Router (SOR) Mathematical Optimality Tests...")
    ts = TestSmartOrderRouter()
    ts.setup_method()
    ts.test_single_venue_cheapest_fill()
    print("  [PASS] Single Venue Cheapest Fill Allocation")
    ts.test_multi_venue_waterfilling_split()
    print("  [PASS] Multi-Venue Discrete Waterfilling Split")
    ts.test_sor_strictly_dominates_worst_single_venue()
    print("  [PASS] SOR Strictly Dominates Single-Venue Worst Case")
    ts.test_partial_fill_handling()
    print("  [PASS] Partial Fill & Capacity Handling")

    # 2. Matcher & Temporal Safety Tests
    print("\n[2/3] Running Matcher & Temporal Horizon Conflict Tests...")
    tm = TestMatcherSafety()
    tm.test_year_horizon_mismatch_strictly_rejected()
    print("  [PASS] Year Horizon Mismatch Strictly Rejected (2026 vs 2027)")
    tm.test_directional_conflict_rejected()
    print("  [PASS] Directional Conflict Guard (Hike vs Cut)")
    tm.test_month_horizon_mismatch_rejected()
    print("  [PASS] Date/Month Horizon Guard (July vs December)")
    tm.test_identical_events_pass()
    print("  [PASS] Equivalent Economic Events Pass Verification")

    # 3. Parity & Synthetic Arbitrage Tests
    print("\n[3/3] Running Binary Parity & Capital Efficiency Tests...")
    tp = TestParityEngine()
    tp.setup_method()
    tp.test_discount_arbitrage_detection()
    print("  [PASS] Discount Buy Arbitrage & SOFR Hurdle Evaluation")
    tp.test_no_arbitrage_when_spreads_wide()
    print("  [PASS] Normal Market Spread Invariance")

    print("\n" + "=" * 70)
    print(">>> ALL 10 QUANTITATIVE & MICROSTRUCTURE TESTS PASSED WITH 100% SUCCESS! <<<")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
