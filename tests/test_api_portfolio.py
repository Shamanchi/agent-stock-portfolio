"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_universe(client: TestClient) -> None:
    resp = client.get("/api/v1/universe")
    assert resp.status_code == 200
    assert resp.json() == {"tickers": ["AAA", "BBB", "CCC"]}


def test_signals(client: TestClient) -> None:
    resp = client.post("/api/v1/signals", json={"tickers": ["AAA", "BBB"]})
    assert resp.status_code == 200
    by_ticker = {item["ticker"]: item for item in resp.json()}
    assert by_ticker["AAA"]["signal"] == "bullish"
    assert by_ticker["BBB"]["signal"] == "bearish"


def test_signals_rejects_unknown(client: TestClient) -> None:
    resp = client.post("/api/v1/signals", json={"tickers": ["GHOST"]})
    assert resp.status_code == 422


def test_rebalance(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/rebalance",
        json={"holdings": {"AAA": 600, "BBB": 400}, "targets": {"AAA": 0.5, "BBB": 0.5}},
    )
    assert resp.status_code == 200
    assert resp.json()["total_value"] == 1000.0
    assert len(resp.json()["trades"]) == 2


@pytest.mark.integration()
def test_rebalance_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: форма плана, без сети."""
    resp = client.post(
        "/api/v1/rebalance",
        json={"holdings": {"AAA": 500}, "targets": {"AAA": 1.0}},
    )
    assert resp.status_code == 200
    assert resp.json()["trades"] == []
