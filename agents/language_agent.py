from __future__ import annotations

from typing import Any, Dict, List
import json


def _load_company_names() -> Dict[str, str]:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    ticker_map = config.get("ticker_map", {})
    return {ticker: name.title() for name, ticker in ticker_map.items()}


def language_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    market_data = state.get("market_data", {})
    analysis = state.get("analysis", {})
    retrieved_docs = state.get("retrieved_docs", [])
    intents: List[str] = state.get("intents", [])
    transcript = state.get("transcript", "")

    company_names = _load_company_names()
    parts: List[str] = []

    if "price" in intents:
        for ticker, payload in market_data.items():
            if payload.get("error"):
                parts.append(f"I could not fetch live data for {ticker}.")
                continue
            name = company_names.get(ticker, payload.get("company_name", ticker))
            current_price = payload.get("current_price")
            change_percent = payload.get("change_percent")
            if current_price is not None:
                parts.append(f"{name} is trading near ${current_price:.2f} with an intraday move of {change_percent}.")

    if "compare" in intents:
        comparisons = analysis.get("comparisons", {})
        sentences = []
        for ticker, payload in comparisons.items():
            name = company_names.get(ticker, ticker)
            price = payload.get("current_price")
            pe_ratio = payload.get("pe_ratio")
            beta = payload.get("beta")
            piece = f"{name}: price=${price:.2f}" if isinstance(price, (int, float)) else f"{name}: price unavailable"
            if pe_ratio is not None:
                piece += f", PE={pe_ratio:.2f}"
            if beta is not None:
                piece += f", beta={beta:.2f}"
            sentences.append(piece)
        if sentences:
            parts.append("Comparison summary — " + "; ".join(sentences) + ".")

    if "portfolio" in intents:
        portfolio_metrics = analysis.get("portfolio_metrics", {})
        total_value = portfolio_metrics.get("total_value")
        holdings = portfolio_metrics.get("holdings", {})
        if isinstance(total_value, (int, float)):
            summary = [f"Your sample portfolio is worth about ${total_value:.2f}."]
            for ticker, details in holdings.items():
                name = company_names.get(ticker, ticker)
                summary.append(f"{name} contributes ${details['value']:.2f} at {details['allocation']} allocation")
            parts.append(" ".join(summary) + ".")

    if "recommend" in intents:
        recommendations = analysis.get("recommendations", [])
        if recommendations:
            rec = recommendations[0]
            ticker = rec.get("ticker") or "your current watchlist"
            name = company_names.get(ticker, ticker)
            parts.append(f"Recommendation: {rec.get('action', 'hold').title()} — {name}. Reason: {rec.get('reason', 'No reason available')}.")

    if any(word in transcript.lower() for word in ["why", "rising", "falling", "news", "up", "down"]):
        for item in retrieved_docs:
            if item.get("type") == "news" and item.get("data"):
                first = item["data"][0]
                if isinstance(first, dict) and first.get("title"):
                    parts.append(f"Recent headline for {item.get('ticker')}: {first['title']}.")
                    break

    if not parts:
        parts.append("I understood the request, but I do not have enough data to produce a strong market brief.")

    return {"narrative": " ".join(parts)}
