from __future__ import annotations

from typing import Any, Dict, List
import os

from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()


def news_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    companies: List[str] = state.get("companies", [])
    transcript = state.get("transcript", "")
    api_key = os.getenv("b618b80f1d7e48739d8ccf9dad7d83ab")

    if not api_key or not companies:
        return {"news_data": {}}

    client = NewsApiClient(api_key=api_key)
    news_data: Dict[str, Any] = {}

    for company in companies:
        try:
            response = client.get_everything(q=company, language="en", sort_by="publishedAt", page_size=5)
            articles = response.get("articles", [])
            news_data[company] = [
                {
                    "title": article.get("title"),
                    "source": (article.get("source") or {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "summary": article.get("description"),
                }
                for article in articles
            ]
        except Exception as exc:
            news_data[company] = [{"error": str(exc), "query": transcript}]

    return {"news_data": news_data}
