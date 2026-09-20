"""Mock-истории цен и дивиденды: офлайн-фикстуры без сети."""

from __future__ import annotations

# 20 точек истории на тикер: AAA растёт, BBB падает, CCC боковик.
HISTORIES: dict[str, list[float]] = {
    "AAA": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 14.0, 15.0, 16.0, 17.0,
            18.0, 19.0, 20.0, 21.0, 22.0, 21.0, 22.0, 23.0, 24.0, 25.0],
    "BBB": [50.0, 49.0, 48.0, 47.0, 46.0, 45.0, 46.0, 45.0, 44.0, 43.0,
            42.0, 41.0, 40.0, 39.0, 38.0, 39.0, 38.0, 37.0, 36.0, 35.0],
    "CCC": [20.0, 21.0, 20.0, 21.0, 20.0, 21.0, 20.0, 21.0, 20.0, 21.0,
            20.0, 21.0, 20.0, 21.0, 20.0, 21.0, 20.0, 21.0, 20.0, 21.0],
}

YIELDS: dict[str, float] = {"AAA": 1.5, "BBB": 4.0, "CCC": 2.5}


def universe() -> list[str]:
    return sorted(HISTORIES)


def history(ticker: str) -> list[float]:
    key = ticker.strip().upper()
    if key not in HISTORIES:
        raise ValueError(f"unknown ticker: {ticker!r}")
    return list(HISTORIES[key])


def dividend_yield(ticker: str) -> float:
    return YIELDS.get(ticker.strip().upper(), 0.0)
