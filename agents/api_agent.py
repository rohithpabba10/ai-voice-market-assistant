from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
import os

import yfinance as yf
from dotenv import load_dotenv

load_dotenv()


def _history_period_from_time_query(time_query: str | None) -> str:
    if not time_query:
        return "1mo"
    query = time_query.lower()
    if "day" in query:
        return "1d"
    if "week" in query:
        return "5d"
    if "year" in query:
        return "1y"
    return "1mo"


def _get_ticker_metrics(ticker: str, period: str) -> Dict[str, Any]:
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info or {}

    history = yf_ticker.history(period=period)
    one_day = yf_ticker.history(period="1d")

    if one_day.empty:
        return {"error": f"No price data found for {ticker}"}

    # 🔹 Current price
    current_price = float(one_day["Close"].iloc[-1])
    open_price = float(one_day["Open"].iloc[-1]) if "Open" in one_day else current_price
    change_percent = ((current_price - open_price) / open_price * 100) if open_price else 0.0

    # 🔹 Historical price
    historical_price = None
    if not history.empty:
        historical_price = float(history["Close"].iloc[0])

    # 🔹 Volatility
    one_year = yf_ticker.history(period="1y")
    volatility = None
    if not one_year.empty:
        volatility = float(one_year["Close"].pct_change().std() * (252 ** 0.5))

    # 🔥 NEW: Chart Data
    chart_data = None
    if not history.empty:
        chart_data = history.reset_index()[["Date", "Close"]].to_dict(orient="records")

    return {
        "ticker": ticker,
        "current_price": current_price,
        "historical_price": historical_price,
        "change_percent": f"{change_percent:.2f}%",
        "timestamp": datetime.now().strftime("%Y-%m-%d"),
        "pe_ratio": float(info.get("trailingPE")) if info.get("trailingPE") else None,
        "beta": float(info.get("beta")) if info.get("beta") else None,
        "volatility": volatility,
        "company_name": info.get("longName") or ticker,

        # 🔥 ADD THIS
        "chart_data": chart_data
    }


def api_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    companies: List[str] = state.get("companies", [])
    intents: List[str] = state.get("intents", [])
    portfolio_data: Dict[str, Any] = state.get("portfolio_data", {})
    time_query: str | None = state.get("time_query")

    if "portfolio" in intents and portfolio_data.get("holdings"):
        portfolio_tickers = list(portfolio_data["holdings"].keys())
        companies = list(dict.fromkeys(companies + portfolio_tickers))

    if not companies:
        return {"market_data": {}}

    period = _history_period_from_time_query(time_query)
    market_data: Dict[str, Any] = {}

    for ticker in companies:
        try:
            market_data[ticker] = _get_ticker_metrics(ticker, period)
        except Exception as exc:
            market_data[ticker] = {"ticker": ticker, "error": str(exc)}

    return {"market_data": market_data}