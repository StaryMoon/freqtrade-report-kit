# Changelog

## v0.2.0 - 2026-07-05

- Add CLI risk gates for profit factor, drawdown, and minimum trade count.
- Return exit code `2` when a generated report fails any configured risk gate.
- Document CI-style usage for turning backtest reports into automated review checks.

## v0.1.0 - 2026-06-25

- Initial release.
- Parse common Freqtrade backtest JSON layouts.
- Generate Markdown reports for GitHub, Obsidian, and trading notebooks.
- Generate standalone HTML reports without JavaScript.
- Export a CSV strategy summary for spreadsheets.
- Include a sample multi-strategy backtest export and tests.
