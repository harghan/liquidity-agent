#!/usr/bin/env python3
"""
Zero-dependency test runner for institutional test verification.
Executes all unit tests in tests/ using standard library unittest.
"""

import sys
import unittest
from pathlib import Path

# Ensure root dir is in path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from tests.test_sor import TestSmartOrderRouter
from tests.test_matcher import TestMatcherSafety
from tests.test_parity import TestParityEngine


class UnitTestCaseAdapter(unittest.TestCase):
    def test_sor_single_venue(self):
        t = TestSmartOrderRouter()
        t.setup_method()
        t.test_single_venue_cheapest_fill()

    def test_sor_multi_venue_split(self):
        t = TestSmartOrderRouter()
        t.setup_method()
        t.test_multi_venue_waterfilling_split()

    def test_sor_dominates_worst(self):
        t = TestSmartOrderRouter()
        t.setup_method()
        t.test_sor_strictly_dominates_worst_single_venue()

    def test_sor_partial_fill(self):
        t = TestSmartOrderRouter()
        t.setup_method()
        t.test_partial_fill_handling()

    def test_matcher_year_mismatch(self):
        t = TestMatcherSafety()
        t.test_year_horizon_mismatch_strictly_rejected()

    def test_matcher_direction_conflict(self):
        t = TestMatcherSafety()
        t.test_directional_conflict_rejected()

    def test_matcher_month_mismatch(self):
        t = TestMatcherSafety()
        t.test_month_horizon_mismatch_rejected()

    def test_matcher_identical_pass(self):
        t = TestMatcherSafety()
        t.test_identical_events_pass()

    def test_parity_discount_arb(self):
        t = TestParityEngine()
        t.setup_method()
        t.test_discount_arbitrage_detection()

    def test_parity_no_arb(self):
        t = TestParityEngine()
        t.setup_method()
        t.test_no_arbitrage_when_spreads_wide()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(UnitTestCaseAdapter)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
