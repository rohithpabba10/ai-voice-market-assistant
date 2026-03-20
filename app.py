from __future__ import annotations

import asyncio
import base64
from datetime import datetime
import os

import streamlit as st
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

import plotly.express as px
import pandas as pd

from orchestrator.workflow import workflow

load_dotenv()

st.set_page_config(page_title="Rohith Market Voice Assistant", page_icon="🎙️", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #07111f 0%, #10233f 45%, #1d3557 100%);
        color: #f5f7fb;
    }
    .block-container {
        max-width: 860px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .hero {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 1.4rem;
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(8px);
        margin-bottom: 1rem;
    }
    .subtext {
        color: #d5deeb;
        font-size: 0.98rem;
    }
    .chip {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.05);
        margin-right: 0.45rem;
        margin-top: 0.45rem;
        font-size: 0.88rem;
    }
    .chat-card {
        padding: 0.9rem 1rem;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(255,255,255,0.10);
    }
    .user-card {
        background: rgba(91, 141, 239, 0.16);
    }
    .bot-card {
        background: rgba(255,255,255,0.08);
    }
    .timestamp {
        color: #bbcae0;
        font-size: 0.78rem;
        margin-top: 0.35rem;
    }
    .footer-note {
        margin-top: 2rem;
        text-align: center;
        color: #c8d2e0;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _autoplay_audio(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "rb") as file:
        audio_bytes = file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    st.markdown(
        f"""
        <audio autoplay controls style="width:100%; margin-top: 0.75rem;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )


async def main() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>🎙️ Rohith Market Voice Assistant</h1>
            <p class="subtext">
                Ask for stock prices, portfolio analysis, comparisons, and recent market reasons using your voice.
            </p>
            <div>
                <span class="chip">Voice Input</span>
                <span class="chip">Stock Briefs</span>
                <span class="chip">Portfolio Summary</span>
                <span class="chip">News-Aware Responses</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

    graph = workflow()

    audio = mic_recorder(start_prompt="🎤 Start Recording", stop_prompt="⏹ Stop Recording", key="recorder")

    transcript_text = st.text_input("Or type your query", placeholder="Example: Compare Apple and Microsoft")

    submitted = st.button("Run Text Query")

    state = {
        "transcript": "",
        "companies": [],
        "intents": [],
        "market_data": {},
        "news_data": {},
        "retrieved_docs": [],
        "portfolio_data": {},
        "analysis": {},
        "narrative": "",
        "audio_input": "",
        "audio_output": "",
        "time_query": None,
        "error": None,
        "node": "",
    }

    should_run = False

    if audio and not st.session_state.is_processing:
        os.makedirs("data", exist_ok=True)
        audio_input = "data/input.wav"
        with open(audio_input, "wb") as file:
            file.write(audio["bytes"])
        state["audio_input"] = audio_input
        state["transcript"] = "Analyze my portfolio"
        should_run = True

    if submitted and transcript_text.strip() and not st.session_state.is_processing:
        state["transcript"] = transcript_text.strip()
        should_run = True

    if should_run:
        st.session_state.is_processing = True
        try:
            with st.spinner("Generating market brief..."):
                result = graph.invoke(state)
                state.update(result)

            # 🔥 STOCK CHART DISPLAY
            market_data = state.get("market_data", {})

            for ticker, data in market_data.items():
                chart_data = data.get("chart_data")

                if chart_data:
                    df = pd.DataFrame(chart_data)

                    fig = px.line(
                        df,
                        x="Date",
                        y="Close",
                        title=f"📈 {ticker} Stock Price Trend"
                    )

                    fig.update_layout(
                        template="plotly_dark",
                        xaxis_title="Date",
                        yaxis_title="Price ($)"
                    )

                    st.plotly_chart(fig, use_container_width=True)

            # 🔹 Conversation history
            if state["transcript"]:
                st.session_state.conversation.append(
                    {
                        "role": "user",
                        "content": state["transcript"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    }
                )
            if state["narrative"]:
                st.session_state.conversation.append(
                    {
                        "role": "bot",
                        "content": state["narrative"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                    }
                )

            # 🔹 Audio output
            if state.get("audio_file"):
                _autoplay_audio(state["audio_file"])

        except Exception as exc:
            st.error(f"Error: {exc}")
        finally:
            st.session_state.is_processing = False

    if st.session_state.conversation:
        st.subheader("Conversation")
        for msg in reversed(st.session_state.conversation):
            card_type = "user-card" if msg["role"] == "user" else "bot-card"
            speaker = "You" if msg["role"] == "user" else "Assistant"
            st.markdown(
                f"""
                <div class="chat-card {card_type}">
                    <strong>{speaker}</strong><br>
                    {msg['content']}
                    <div class="timestamp">{msg['timestamp']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div class='footer-note'>Prepared by <strong>Pabba Rohith</strong>.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())