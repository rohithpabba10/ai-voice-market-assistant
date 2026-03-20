from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import json

from agents.api_agent import api_agent
from agents.analysis_agent import generate_analysis   # ✅ FIXED
from agents.language_agent import language_agent
from agents.news_agent import news_agent
from agents.retriever_agent import retriever_agent
from agents.voice_agent import text_to_speech as tts_agent   # ✅ FIXED


@dataclass
class SimpleWorkflow:
    def invoke(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = dict(state)
        state.setdefault("companies", [])
        state.setdefault("intents", [])
        state.setdefault("time_query", None)

        transcript = (state.get("transcript") or "").strip()
        state["transcript"] = transcript

        self._load_portfolio(state)
        self._classify_intent(state)

        # 🔹 Step 1: Get stock data
        state.update(api_agent(state))

        # 🔹 Step 2: Get news if needed
        if self._needs_news(transcript):
            state.update(news_agent(state))
        else:
            state["news_data"] = {}

        # 🔹 Step 3: Retrieve combined docs
        state.update(retriever_agent(state))

        # 🔥 Step 4: Generate AI analysis (FREE OpenRouter)
        analysis_text = generate_analysis(transcript)

        state["analysis"] = {
            "recommendations": [
                {
                    "ticker": state.get("companies", [""])[0] if state.get("companies") else "",
                    "action": "hold",
                    "reason": analysis_text
                }
            ],
            "comparisons": {},
            "portfolio_metrics": {}
        }

        # 🔹 Step 5: Generate human-readable output
        state.update(language_agent(state))

        # 🔹 Step 6: Convert to voice
        narrative = state.get("narrative", "")
        state["audio_file"] = tts_agent(narrative)

        return state

    def _load_portfolio(self, state: Dict[str, Any]) -> None:
        try:
            with open("data/portfolio.json", "r", encoding="utf-8") as file:
                state["portfolio_data"] = json.load(file)
        except:
            state["portfolio_data"] = {}

    def _classify_intent(self, state: Dict[str, Any]) -> None:
        transcript = state.get("transcript", "").lower()
        intents: List[str] = []

        if any(word in transcript for word in ["price", "stock", "quote", "trading"]):
            intents.append("price")
        if any(word in transcript for word in ["compare", "versus", "vs"]):
            intents.append("compare")
        if any(word in transcript for word in ["portfolio", "holdings"]):
            intents.append("portfolio")
        if any(word in transcript for word in ["recommend", "buy", "sell"]):
            intents.append("recommend")
        if not intents:
            intents.append("price")

        state["intents"] = list(dict.fromkeys(intents))
        state["companies"] = self._extract_companies(transcript)
        state["time_query"] = self._extract_time_query(transcript)

    def _extract_companies(self, transcript: str) -> List[str]:
        with open("config.json", "r", encoding="utf-8") as file:
            ticker_map = json.load(file).get("ticker_map", {})

        found: List[str] = []
        words = transcript.replace("?", " ").replace(",", " ").split()

        for word in words:
            cleaned = word.strip().lower()
            if cleaned in ticker_map:
                found.append(ticker_map[cleaned])
            elif cleaned.isupper() and len(cleaned) <= 5:
                found.append(cleaned)

        for token in transcript.split():
            token = token.strip().upper()
            if 1 <= len(token) <= 5 and token.isalpha() and token not in found:
                if token in ticker_map.values():
                    found.append(token)

        return list(dict.fromkeys(found))

    def _extract_time_query(self, transcript: str) -> str | None:
        for unit in ["day", "week", "month", "year"]:
            if unit in transcript:
                return f"last {unit}"
        return None

    def _needs_news(self, transcript: str) -> bool:
        return any(word in transcript.lower() for word in ["why", "rising", "falling", "news", "up", "down"])


def workflow() -> SimpleWorkflow:
    return SimpleWorkflow()