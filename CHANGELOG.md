# Changelog

## v0.2.3 - 2026-07-08

- Add the `dev` optional dependency group used by CI.
- Include `ruff` in `.[dev]` so the workflow lint step installs its toolchain explicitly.

## v0.2.2 - 2026-07-08

- Add GitHub Actions CI for Python 3.9, 3.10, 3.11, and 3.12.
- Keep public type annotations compatible with the declared Python 3.9 support window.
- Add README CI badge.
- Add a CI smoke test that exercises report generation and passing risk gates.

## v0.2.1 - 2026-07-06

- Add a copy-paste GitHub Actions workflow for generating backtest reports.
- Document how to use risk gates as CI checks while still uploading report artifacts.

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
