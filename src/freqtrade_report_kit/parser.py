from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Union

from .models import PairSummary, ReportBundle, StrategySummary, TradeSummary


def load_report(path: Union[str, Path]) -> ReportBundle:
    report_path = Path(path)
    with report_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return ReportBundle(source_path=str(report_path), strategies=parse_strategies(payload))


def parse_strategies(payload: Mapping[str, Any]) -> List[StrategySummary]:
    if "strategy" in payload and isinstance(payload["strategy"], Mapping):
        return [
            _parse_strategy(name, data)
            for name, data in payload["strategy"].items()
            if isinstance(data, Mapping)
        ]

    if "strategies" in payload and isinstance(payload["strategies"], Mapping):
        return [
            _parse_strategy(name, data)
            for name, data in payload["strategies"].items()
            if isinstance(data, Mapping)
        ]

    name = str(payload.get("strategy_name") or payload.get("strategy") or "Strategy")
    return [_parse_strategy(name, payload)]


def _parse_strategy(name: str, data: Mapping[str, Any]) -> StrategySummary:
    wins = _number(data, ["wins", "winning_trades", "total_profit_trades", "win_trades"])
    losses = _number(data, ["losses", "losing_trades", "total_loss_trades", "loss_trades"])
    draws = _number(data, ["draws", "draw_trades"])
    trades = _number(data, ["total_trades", "trade_count", "trades_count"]) or int(
        wins + losses + draws
    )

    trade_rows = _as_list(
        data.get("trades")
        or data.get("closed_trades")
        or data.get("results")
        or data.get("trade_list")
    )
    parsed_trades = [_parse_trade(item) for item in trade_rows if isinstance(item, Mapping)]
    if not trades and parsed_trades:
        trades = len(parsed_trades)
    if not wins and not losses and not draws and parsed_trades:
        wins = sum(1 for item in parsed_trades if item.profit_abs > 0)
        losses = sum(1 for item in parsed_trades if item.profit_abs < 0)
        draws = sum(1 for item in parsed_trades if item.profit_abs == 0)

    pairs = _parse_pairs(data, parsed_trades)

    return StrategySummary(
        name=name,
        trades=int(trades),
        wins=int(wins),
        losses=int(losses),
        draws=int(draws),
        profit_abs=_number(
            data,
            ["profit_total_abs", "total_profit_abs", "profit_abs", "absolute_profit", "profit"],
        ),
        profit_pct=_ratio_to_percent(
            _number(
                data,
                ["profit_total", "total_profit", "profit_total_pct", "profit_pct", "total_profit_pct"],
            )
        ),
        profit_factor=_optional_number(data, ["profit_factor"]),
        expectancy=_optional_number(data, ["expectancy", "expectancy_ratio"]),
        max_drawdown_abs=_number(
            data,
            ["max_drawdown_abs", "max_drawdown_account", "max_drawdown_value", "drawdown_abs"],
        ),
        max_drawdown_pct=abs(
            _ratio_to_percent(
                _number(
                    data,
                    ["max_drawdown", "max_drawdown_pct", "max_relative_drawdown", "drawdown_pct"],
                )
            )
        ),
        sharpe=_optional_number(data, ["sharpe", "sharpe_ratio"]),
        sortino=_optional_number(data, ["sortino", "sortino_ratio"]),
        calmar=_optional_number(data, ["calmar", "calmar_ratio"]),
        market_change_pct=_optional_ratio_to_percent(
            _optional_number(data, ["market_change", "market_change_pct"])
        ),
        backtest_start=str(data.get("backtest_start") or data.get("start_date") or ""),
        backtest_end=str(data.get("backtest_end") or data.get("end_date") or ""),
        stake_currency=str(data.get("stake_currency") or data.get("currency") or "USDT"),
        pairs=pairs,
        trades_sample=parsed_trades[:20],
        raw=dict(data),
    )


def _parse_trade(item: Mapping[str, Any]) -> TradeSummary:
    return TradeSummary(
        pair=str(item.get("pair") or item.get("symbol") or ""),
        open_date=str(item.get("open_date") or item.get("open_time") or item.get("date") or ""),
        close_date=str(item.get("close_date") or item.get("close_time") or ""),
        profit_abs=_number(
            item,
            ["profit_abs", "profit_amount", "profit_abs_total", "realized_profit", "pnl"],
        ),
        profit_ratio=_ratio_to_percent(
            _number(item, ["profit_ratio", "profit_pct", "profit_percent"])
        ),
        open_rate=_number(item, ["open_rate", "entry_price", "open_price"]),
        close_rate=_number(item, ["close_rate", "exit_price", "close_price"]),
        enter_tag=str(item.get("enter_tag") or item.get("entry_tag") or ""),
        exit_reason=str(item.get("exit_reason") or item.get("sell_reason") or ""),
        duration=str(item.get("trade_duration") or item.get("duration") or ""),
        is_open=bool(item.get("is_open") or item.get("open")),
    )


def _parse_pairs(data: Mapping[str, Any], parsed_trades: List[TradeSummary]) -> List[PairSummary]:
    candidate = (
        data.get("results_per_pair")
        or data.get("pair_results")
        or data.get("pairlist")
        or data.get("pairs")
    )
    pairs: List[PairSummary] = []
    for item in _as_list(candidate):
        if not isinstance(item, Mapping):
            continue
        pair_name = str(item.get("key") or item.get("pair") or item.get("symbol") or item.get("name") or "")
        if pair_name.upper() == "TOTAL" or not pair_name:
            continue
        pairs.append(
            PairSummary(
                pair=pair_name,
                trades=int(_number(item, ["trades", "total_trades", "trade_count"])),
                wins=int(_number(item, ["wins", "winning_trades"])),
                losses=int(_number(item, ["losses", "losing_trades"])),
                draws=int(_number(item, ["draws"])),
                profit_abs=_number(
                    item,
                    ["profit_abs", "profit_total_abs", "absolute_profit", "profit"],
                ),
                profit_pct=_ratio_to_percent(
                    _number(item, ["profit_pct", "profit_total", "profit_total_pct"])
                ),
                avg_profit_pct=_ratio_to_percent(
                    _number(item, ["profit_mean", "avg_profit", "avg_profit_pct"])
                ),
            )
        )
    if pairs:
        return sorted(pairs, key=lambda item: item.profit_abs, reverse=True)

    by_pair: Dict[str, List[TradeSummary]] = {}
    for trade in parsed_trades:
        if trade.pair:
            by_pair.setdefault(trade.pair, []).append(trade)
    for pair, trades in by_pair.items():
        profit = sum(item.profit_abs for item in trades)
        wins = sum(1 for item in trades if item.profit_abs > 0)
        losses = sum(1 for item in trades if item.profit_abs < 0)
        draws = sum(1 for item in trades if item.profit_abs == 0)
        pairs.append(
            PairSummary(
                pair=pair,
                trades=len(trades),
                wins=wins,
                losses=losses,
                draws=draws,
                profit_abs=profit,
                profit_pct=sum(item.profit_ratio for item in trades),
                avg_profit_pct=sum(item.profit_ratio for item in trades) / len(trades),
            )
        )
    return sorted(pairs, key=lambda item: item.profit_abs, reverse=True)


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _number(data: Mapping[str, Any], keys: Iterable[str]) -> float:
    value = _optional_number(data, keys)
    return value if value is not None else 0.0


def _optional_number(data: Mapping[str, Any], keys: Iterable[str]) -> Optional[float]:
    for key in keys:
        if key not in data:
            continue
        value = data[key]
        if value is None or value == "":
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _ratio_to_percent(value: float) -> float:
    if abs(value) <= 1:
        return value * 100.0
    return value


def _optional_ratio_to_percent(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return _ratio_to_percent(value)
