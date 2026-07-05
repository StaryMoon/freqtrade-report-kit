from __future__ import annotations

from typing import List, Optional

from .models import StrategySummary


def evaluate_risk_gates(
    strategy: Optional[StrategySummary],
    *,
    min_profit_factor: float | None = None,
    max_drawdown_pct: float | None = None,
    min_trades: int | None = None,
) -> List[str]:
    failures: List[str] = []
    if min_profit_factor is None and max_drawdown_pct is None and min_trades is None:
        return failures

    if strategy is None:
        return ["No strategy was found in the input report."]

    if min_profit_factor is not None:
        if strategy.profit_factor is None:
            failures.append(
                f"{strategy.name}: profit factor is missing; expected >= {min_profit_factor:.3f}."
            )
        elif strategy.profit_factor < min_profit_factor:
            failures.append(
                f"{strategy.name}: profit factor {strategy.profit_factor:.3f} < {min_profit_factor:.3f}."
            )

    if max_drawdown_pct is not None and strategy.max_drawdown_pct > max_drawdown_pct:
        failures.append(
            f"{strategy.name}: max drawdown {strategy.max_drawdown_pct:.2f}% > {max_drawdown_pct:.2f}%."
        )

    if min_trades is not None and strategy.trades < min_trades:
        failures.append(f"{strategy.name}: trades {strategy.trades} < {min_trades}.")

    return failures
