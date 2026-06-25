from __future__ import annotations

import argparse
from pathlib import Path

from .parser import load_report
from .renderers import render_html, render_markdown, write_csv


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="freqtrade-report-kit",
        description="Generate clean risk reports from Freqtrade backtest JSON exports.",
    )
    parser.add_argument("input", help="Path to a Freqtrade backtest JSON export.")
    parser.add_argument(
        "-o",
        "--output",
        default="reports/backtest-report.md",
        help="Markdown output path. Default: reports/backtest-report.md",
    )
    parser.add_argument("--html", default="", help="Optional HTML output path.")
    parser.add_argument("--csv", default="", help="Optional strategy summary CSV output path.")
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the Markdown report to stdout after writing files.",
    )
    args = parser.parse_args()

    bundle = load_report(args.input)
    markdown = render_markdown(bundle)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    if args.html:
        html_path = Path(args.html)
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(bundle), encoding="utf-8")

    if args.csv:
        write_csv(bundle, args.csv)

    if args.print:
        print(markdown)
    else:
        print(f"Wrote Markdown report to {output_path}")
        if args.html:
            print(f"Wrote HTML report to {args.html}")
        if args.csv:
            print(f"Wrote CSV summary to {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
