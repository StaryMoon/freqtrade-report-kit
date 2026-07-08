from pathlib import Path
import unittest

from freqtrade_report_kit.gates import evaluate_risk_gates
from freqtrade_report_kit.parser import load_report
from freqtrade_report_kit.renderers import render_html, render_markdown


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "backtest-result.sample.json"


class ParserAndRendererTest(unittest.TestCase):
    def test_loads_multi_strategy_freqtrade_export(self) -> None:
        bundle = load_report(SAMPLE)

        self.assertEqual(len(bundle.strategies), 2)
        self.assertIsNotNone(bundle.best_strategy)
        self.assertEqual(bundle.best_strategy.name, "MomentumScalper")
        self.assertEqual(bundle.best_strategy.trades, 8)
        self.assertEqual(round(bundle.best_strategy.profit_pct, 2), 18.24)
        self.assertEqual(round(bundle.best_strategy.max_drawdown_pct, 2), 11.8)

    def test_markdown_contains_risk_summary_and_pairs(self) -> None:
        bundle = load_report(SAMPLE)
        markdown = render_markdown(bundle)

        self.assertIn("Executive Summary", markdown)
        self.assertIn("Strategy Ranking", markdown)
        self.assertIn("BTC/USDT", markdown)
        self.assertIn("Risk Review Checklist", markdown)
        self.assertIn("Never enable live trading", markdown)

    def test_html_renderer_contains_table(self) -> None:
        bundle = load_report(SAMPLE)
        html = render_html(bundle)

        self.assertIn("<table>", html)
        self.assertIn("MomentumScalper", html)
        self.assertIn("Freqtrade Backtest Risk Report", html)

    def test_risk_gates_pass_and_fail_on_best_strategy(self) -> None:
        bundle = load_report(SAMPLE)

        self.assertEqual(
            evaluate_risk_gates(
                bundle.best_strategy,
                min_profit_factor=1.5,
                max_drawdown_pct=15,
                min_trades=8,
            ),
            [],
        )

        failures = evaluate_risk_gates(
            bundle.best_strategy,
            min_profit_factor=2.0,
            max_drawdown_pct=10,
            min_trades=12,
        )
        self.assertEqual(len(failures), 3)
        self.assertIn("profit factor", failures[0])
        self.assertIn("max drawdown", failures[1])
        self.assertIn("trades", failures[2])


if __name__ == "__main__":
    unittest.main()
