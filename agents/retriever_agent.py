from __future__ import annotations

from typing import Any, Dict, List


def retriever_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    market_data = state.get("market_data", {})
    news_data = state.get("news_data", {})
    documents: List[Dict[str, Any]] = []

    for ticker, payload in market_data.items():
        documents.append({"type": "market", "ticker": ticker, "data": payload})

    for ticker, articles in news_data.items():
        documents.append({"type": "news", "ticker": ticker, "data": articles})

    return {"retrieved_docs": documents}
