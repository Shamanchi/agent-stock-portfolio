"""SMA-сигналы и план ребалансировки."""

from __future__ import annotations

from pydantic import BaseModel

from app.services.market import dividend_yield, history


class TickerSignal(BaseModel):
    ticker: str
    sma_short: float
    sma_long: float
    signal: str
    yield_pct: float


class Trade(BaseModel):
    ticker: str
    action: str
    amount: float


class RebalancePlan(BaseModel):
    total_value: float
    trades: list[Trade]


def sma(values: list[float], window: int) -> float:
    """Простая скользящая средняя. Детерминировано."""
    if window < 1:
        raise ValueError("window must be >= 1")
    if len(values) < window:
        raise ValueError(f"need >= {window} points, got {len(values)}")
    return round(sum(values[-window:]) / window, 2)


def signal_for(ticker: str, short: int = 5, long: int = 20) -> TickerSignal:
    """SMA-сигнал тикера: bullish/bearish/neutral."""
    prices = history(ticker)
    short_ma = sma(prices, short)
    long_ma = sma(prices, long)
    if short_ma > long_ma:
        signal = "bullish"
    elif short_ma < long_ma:
        signal = "bearish"
    else:
        signal = "neutral"
    return TickerSignal(
        ticker=ticker.strip().upper(),
        sma_short=short_ma,
        sma_long=long_ma,
        signal=signal,
        yield_pct=dividend_yield(ticker),
    )


def rebalance(holdings: dict[str, float], targets: dict[str, float]) -> RebalancePlan:
    """План сделок к целевым весам. Детерминировано."""
    if not holdings:
        raise ValueError("holdings must not be empty")
    total = round(sum(holdings.values()), 2)
    if total <= 0:
        raise ValueError("total value must be positive")
    target_sum = round(sum(targets.values()), 4)
    if abs(target_sum - 1.0) > 1e-6:
        raise ValueError(f"targets must sum to 1.0, got {target_sum}")
    tickers = sorted(set(holdings) | set(targets))
    trades: list[Trade] = []
    for ticker in tickers:
        current = holdings.get(ticker, 0.0)
        wanted = round(total * targets.get(ticker, 0.0), 2)
        delta = round(wanted - current, 2)
        if abs(delta) < 0.01:
            continue
        trades.append(Trade(ticker=ticker, action="buy" if delta > 0 else "sell", amount=abs(delta)))
    return RebalancePlan(total_value=total, trades=trades)
