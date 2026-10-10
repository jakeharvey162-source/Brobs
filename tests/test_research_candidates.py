"""Vendored public MIT Freqtrade strategy is research-only, not BROBS live execution."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / 'integrations/freqtrade/TrendRiderStrategy.py'
LICENSE = ROOT / 'integrations/freqtrade/TRENDRIDER-LICENSE'

class CandidateAudit(unittest.TestCase):
    def test_upstream_mit_license_is_preserved(self):
        self.assertTrue(STRATEGY.is_file())
        self.assertIn('MIT License', LICENSE.read_text(encoding='utf-8'))
        self.assertIn('Copyright (c) 2026 TrendRider', LICENSE.read_text(encoding='utf-8'))
    def test_strategy_is_parseable_and_has_no_direct_external_order_gate(self):
        code = STRATEGY.read_text(encoding='utf-8')
        tree = ast.parse(code)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        names = [name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
        self.assertNotIn('requests',names)
        self.assertNotIn('subprocess',names)
        self.assertNotIn('urllib.request',imports)
        self.assertIn('freqtrade.strategy',imports)
        self.assertIn('class TrendRiderStrategy',code)
        # This file is a standalone optional Freqtrade strategy, not imported
        # by BROBS trading runners or recognized as broker-connected execution.
        for runner in ('market_runner.py','fx_runner.py'):
            self.assertNotIn('TrendRiderStrategy', (ROOT / 'brobs' / runner).read_text(encoding='utf-8'))
if __name__ == '__main__': unittest.main()
