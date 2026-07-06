# GitHub Actions Example

`freqtrade-report-kit` can run as a lightweight CI gate for public or private Freqtrade strategy repositories. A typical workflow is:

1. Run or commit a Freqtrade backtest export, for example `backtests/latest.json`.
2. Generate Markdown, HTML, and CSV reports.
3. Fail the workflow if the best strategy misses your minimum risk thresholds.
4. Upload the reports as artifacts for review.

Copy the example workflow from:

```text
examples/github-actions/freqtrade-report.yml
```

into your strategy repository:

```text
.github/workflows/freqtrade-report.yml
```

The important part is the risk gate:

```bash
ft-report-kit backtests/latest.json \
  --output reports/backtest-report.md \
  --html reports/backtest-report.html \
  --csv reports/backtest-summary.csv \
  --fail-under-profit-factor 1.30 \
  --fail-over-drawdown 20 \
  --fail-under-trades 30
```

The command exits with code `2` when any gate fails. The report files are still written before the failure, so the workflow can upload them with `if: always()` for debugging.

Tune the thresholds for your own strategy family. A scalping strategy, trend-following strategy, and low-frequency portfolio strategy should not share the same minimum trade count or drawdown limit.
