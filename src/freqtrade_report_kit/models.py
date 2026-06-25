from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TradeSummary:
    pair: str
    open_date: str = ""
    close_date: str = ""
    profit_abs: float = 0.0
    profit_ratio: float = 0.0
    open_rate: float = 0.0
    close_rate: float = 0.0
    enter_tag: str = ""
    exit_reason: str = ""
    duration: str = ""
    is_open: bool = False


@dataclass
class PairSummary:
    pair: str
    trades: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    profit_abs: float = 0.0
    profit_pct: float = 0.0
    avg_profit_pct: float = 0.0

    @property
    def win_rate(self) -> float:
        closed = self.wins + self.losses + self.draws
        return (self.wins / closed * 100.0) if closed else 0.0


@dataclass
class StrategySummary:
    name: str
    trades: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    profit_abs: float = 0.0
    profit_pct: float = 0.0
    profit_factor: Optional[float] = None
    expectancy: Optional[float] = None
    max_drawdown_abs: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe: Optional[float] = None
    sortino: Optional[float] = None
    calmar: Optional[float] = None
    market_change_pct: Optional[float] = None
    backtest_start: str = ""
    backtest_end: str = ""
    stake_currency: str = "USDT"
    pairs: List[PairSummary] = field(default_factory=list)
    trades_sample: List[TradeSummary] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def win_rate(self) -> float:
        closed = self.wins + self.losses + self.draws
        return (self.wins / closed * 100.0) if closed else 0.0

    @property
    def risk_label(self) -> str:
        if self.trades == 0:
            return "No trades"
        if self.max_drawdown_pct >= 35:
            return "High drawdown"
        if self.max_drawdown_pct >= 20:
            return "Elevated drawdown"
        if self.profit_pct < 0:
            return "Losing backtest"
        if self.profit_factor is not None and self.profit_factor >= 1.5 and self.max_drawdown_pct < 15:
            return "Clean candidate"
        return "Needs review"


@dataclass
class ReportBundle:
    source_path: str
    strategies: List[StrategySummary]

    @property
    def best_strategy(self) -> Optional[StrategySummary]:
        if not self.strategies:
            return None
        return sorted(
            self.strategies,
            key=lambda item: (item.profit_pct, -item.max_drawdown_pct, item.profit_abs),
            reverse=True,
        )[0]
