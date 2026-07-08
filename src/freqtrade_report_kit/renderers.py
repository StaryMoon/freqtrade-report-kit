from __future__ import annotations

import csv
import html
from pathlib import Path
from typing import Iterable, List, Optional, Union

from .models import PairSummary, ReportBundle, StrategySummary, TradeSummary


def render_markdown(bundle: ReportBundle) -> str:
    lines: List[str] = [
        "# Freqtrade Backtest Risk Report",
        "",
        f"Source: `{bundle.source_path}`",
        "",
    ]
    best = bundle.best_strategy
    if best:
        lines.extend(
            [
                "## Executive Summary",
                "",
                f"- Best strategy by return: **{best.name}**",
                f"- Return: **{fmt_pct(best.profit_pct)}**",
                f"- Realized profit: **{fmt_money(best.profit_abs, best.stake_currency)}**",
                f"- Max drawdown: **{fmt_pct(best.max_drawdown_pct)}**",
                f"- Profit factor: **{fmt_optional(best.profit_factor)}**",
                f"- Risk label: **{best.risk_label}**",
                "",
            ]
        )

    lines.extend(["## Strategy Ranking", "", _strategy_table(bundle.strategies), ""])
    for strategy in bundle.strategies:
        lines.extend(_strategy_section(strategy))
    lines.extend(_review_checklist())
    return "\n".join(lines).rstrip() + "\n"


def render_html(bundle: ReportBundle) -> str:
    markdown = render_markdown(bundle)
    body = _markdown_to_simple_html(markdown)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Freqtrade Backtest Risk Report</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 64px;
      background: #f8fafc;
      color: #172033;
    }}
    h1, h2, h3 {{ letter-spacing: -0.02em; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px; background: white; }}
    th, td {{ border: 1px solid #dbe3ef; padding: 8px 10px; text-align: right; }}
    th:first-child, td:first-child {{ text-align: left; }}
    th {{ background: #edf2f7; }}
    code {{ background: #edf2f7; border-radius: 4px; padding: 2px 4px; }}
    ul {{ padding-left: 24px; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #111827; color: #e5e7eb; }}
      table {{ background: #172033; }}
      th, td {{ border-color: #334155; }}
      th, code {{ background: #1f2937; }}
    }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def write_csv(bundle: ReportBundle, path: Union[str, Path]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "strategy",
                "trades",
                "wins",
                "losses",
                "draws",
                "win_rate_pct",
                "profit_abs",
                "profit_pct",
                "max_drawdown_pct",
                "profit_factor",
                "risk_label",
            ]
        )
        for item in bundle.strategies:
            writer.writerow(
                [
                    item.name,
                    item.trades,
                    item.wins,
                    item.losses,
                    item.draws,
                    round(item.win_rate, 4),
                    round(item.profit_abs, 8),
                    round(item.profit_pct, 4),
                    round(item.max_drawdown_pct, 4),
                    "" if item.profit_factor is None else round(item.profit_factor, 4),
                    item.risk_label,
                ]
            )


def _strategy_table(strategies: Iterable[StrategySummary]) -> str:
    rows = [
        "| Strategy | Trades | Win rate | Return | Profit | Max DD | PF | Label |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in sorted(strategies, key=lambda x: x.profit_pct, reverse=True):
        rows.append(
            "| {name} | {trades} | {win_rate} | {profit_pct} | {profit_abs} | {dd} | {pf} | {label} |".format(
                name=item.name,
                trades=item.trades,
                win_rate=fmt_pct(item.win_rate),
                profit_pct=fmt_pct(item.profit_pct),
                profit_abs=fmt_money(item.profit_abs, item.stake_currency),
                dd=fmt_pct(item.max_drawdown_pct),
                pf=fmt_optional(item.profit_factor),
                label=item.risk_label,
            )
        )
    return "\n".join(rows)


def _strategy_section(strategy: StrategySummary) -> List[str]:
    lines = [
        f"## {strategy.name}",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Trades | {strategy.trades} |",
        f"| Wins / Losses / Draws | {strategy.wins} / {strategy.losses} / {strategy.draws} |",
        f"| Win rate | {fmt_pct(strategy.win_rate)} |",
        f"| Return | {fmt_pct(strategy.profit_pct)} |",
        f"| Realized profit | {fmt_money(strategy.profit_abs, strategy.stake_currency)} |",
        f"| Profit factor | {fmt_optional(strategy.profit_factor)} |",
        f"| Expectancy | {fmt_optional(strategy.expectancy)} |",
        f"| Max drawdown | {fmt_pct(strategy.max_drawdown_pct)} |",
        f"| Max drawdown abs | {fmt_money(strategy.max_drawdown_abs, strategy.stake_currency)} |",
        f"| Sharpe / Sortino / Calmar | {fmt_optional(strategy.sharpe)} / {fmt_optional(strategy.sortino)} / {fmt_optional(strategy.calmar)} |",
        f"| Market change | {fmt_optional_pct(strategy.market_change_pct)} |",
        "",
    ]
    if strategy.pairs:
        lines.extend(["### Pair Contribution", "", _pair_table(strategy.pairs[:12]), ""])
    if strategy.trades_sample:
        lines.extend(["### Trade Sample", "", _trade_table(strategy.trades_sample[:12]), ""])
    return lines


def _pair_table(pairs: Iterable[PairSummary]) -> str:
    rows = [
        "| Pair | Trades | Win rate | Avg profit | Total profit | Profit abs |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in pairs:
        rows.append(
            f"| {item.pair} | {item.trades} | {fmt_pct(item.win_rate)} | {fmt_pct(item.avg_profit_pct)} | {fmt_pct(item.profit_pct)} | {fmt_money(item.profit_abs)} |"
        )
    return "\n".join(rows)


def _trade_table(trades: Iterable[TradeSummary]) -> str:
    rows = [
        "| Pair | Open | Close | Profit | Profit % | Exit |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for item in trades:
        rows.append(
            f"| {item.pair} | {item.open_date} | {item.close_date} | {fmt_money(item.profit_abs)} | {fmt_pct(item.profit_ratio)} | {item.exit_reason or '-'} |"
        )
    return "\n".join(rows)


def _review_checklist() -> List[str]:
    return [
        "## Risk Review Checklist",
        "",
        "- Check whether profit comes from one pair or from broad pair contribution.",
        "- Treat high return with high drawdown as a fragile candidate, not a finished strategy.",
        "- Compare the strategy return with market change before trusting the alpha.",
        "- Re-run the backtest with fresh data, fees, realistic slippage, and at least one out-of-sample period.",
        "- Never enable live trading from a single pretty report.",
        "",
    ]


def _markdown_to_simple_html(markdown: str) -> str:
    html_lines: List[str] = []
    in_ul = False
    in_table = False
    table_rows: List[str] = []

    for line in markdown.splitlines():
        if line.startswith("|") and line.endswith("|"):
            table_rows.append(line)
            in_table = True
            continue
        if in_table:
            html_lines.append(_table_to_html(table_rows))
            table_rows = []
            in_table = False

        if line.startswith("- "):
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            html_lines.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if in_ul:
            html_lines.append("</ul>")
            in_ul = False

        if line.startswith("# "):
            html_lines.append(f"<h1>{_inline(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{_inline(line[4:])}</h3>")
        elif not line.strip():
            html_lines.append("")
        else:
            html_lines.append(f"<p>{_inline(line)}</p>")

    if in_table:
        html_lines.append(_table_to_html(table_rows))
    if in_ul:
        html_lines.append("</ul>")
    return "\n".join(html_lines)


def _table_to_html(rows: List[str]) -> str:
    if len(rows) <= 2:
        return ""
    parsed = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    header = parsed[0]
    body = parsed[2:]
    out = ["<table>", "<thead><tr>"]
    out.extend(f"<th>{_inline(cell)}</th>" for cell in header)
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        out.extend(f"<td>{_inline(cell)}</td>" for cell in row)
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def _inline(text: str) -> str:
    escaped = html.escape(text)
    escaped = escaped.replace("**", "")
    if "`" in escaped:
        parts = escaped.split("`")
        for index in range(1, len(parts), 2):
            parts[index] = f"<code>{parts[index]}</code>"
        return "".join(parts)
    return escaped


def fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def fmt_optional_pct(value: Optional[float]) -> str:
    return "-" if value is None else fmt_pct(value)


def fmt_optional(value: Optional[float]) -> str:
    return "-" if value is None else f"{value:.3f}"


def fmt_money(value: float, currency: str = "USDT") -> str:
    return f"{value:.4f} {currency}".strip()
