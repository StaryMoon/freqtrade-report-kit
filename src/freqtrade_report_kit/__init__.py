"""Report generation utilities for Freqtrade backtest exports."""

from .models import PairSummary, ReportBundle, StrategySummary, TradeSummary
from .parser import load_report

__all__ = [
    "PairSummary",
    "ReportBundle",
    "StrategySummary",
    "TradeSummary",
    "load_report",
]

__version__ = "0.2.4"
