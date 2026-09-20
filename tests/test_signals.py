"""Unit-тесты сигналов и ребалансировки: без сети, детерминированы."""

import pytest

from app.services.market import dividend_yield, history, universe
from app.services.signals import rebalance, signal_for, sma


def test_sma_math() -> None:
    assert sma([1.0, 2.0, 3.0, 4.0, 5.0], 5) == 3.0
    assert sma([1.0, 2.0, 3.0, 4.0, 5.0], 2) == 4.5
    with pytest.raises(ValueError):
        sma([1.0], 5)
    with pytest.raises(ValueError):
        sma([1.0, 2.0], 0)


def test_signals_direction() -> None:
    bullish = signal_for("AAA")
    assert (bullish.sma_short, bullish.sma_long, bullish.signal) == (23.0, 17.6, "bullish")
    assert bullish.yield_pct == 1.5
    bearish = signal_for("BBB")
    assert (bearish.sma_short, bearish.sma_long, bearish.signal) == (37.0, 42.4, "bearish")
    with pytest.raises(ValueError):
        signal_for("GHOST")


def test_rebalance_plan() -> None:
    plan = rebalance({"AAA": 600.0, "BBB": 400.0}, {"AAA": 0.5, "BBB": 0.5})
    assert plan.total_value == 1000.0
    assert [(trade.ticker, trade.action, trade.amount) for trade in plan.trades] == [
        ("AAA", "sell", 100.0),
        ("BBB", "buy", 100.0),
    ]


def test_rebalance_balanced_no_trades() -> None:
    plan = rebalance({"AAA": 500.0}, {"AAA": 1.0})
    assert plan.trades == []


def test_rebalance_rejects_bad_input() -> None:
    with pytest.raises(ValueError):
        rebalance({}, {"AAA": 1.0})
    with pytest.raises(ValueError):
        rebalance({"AAA": 100.0}, {"AAA": 0.5, "BBB": 0.4})


def test_universe() -> None:
    assert universe() == ["AAA", "BBB", "CCC"]
    assert dividend_yield("bbb") == 4.0
    assert len(history("AAA")) == 20
