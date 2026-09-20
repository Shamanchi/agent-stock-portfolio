"""Эндпоинты сигналов и ребалансировки."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.market import universe
from app.services.signals import RebalancePlan, TickerSignal, rebalance, signal_for

router = APIRouter()


class SignalsRequest(BaseModel):
    tickers: list[str] = Field(min_length=1, max_length=50)


class RebalanceRequest(BaseModel):
    holdings: dict[str, float] = Field(min_length=1, max_length=50)
    targets: dict[str, float] = Field(min_length=1, max_length=50)


@router.get("/universe")
async def list_universe() -> dict:
    return {"tickers": universe()}


@router.post("/signals", response_model=list[TickerSignal])
async def signals(
    request: SignalsRequest,
    settings: Settings = Depends(get_settings),
) -> list[TickerSignal]:
    try:
        return [
            signal_for(ticker, settings.sma_short, settings.sma_long) for ticker in request.tickers
        ]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/rebalance", response_model=RebalancePlan)
async def rebalance_endpoint(request: RebalanceRequest) -> RebalancePlan:
    try:
        return rebalance(
            {key.upper(): value for key, value in request.holdings.items()},
            {key.upper(): value for key, value in request.targets.items()},
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
