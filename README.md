# Rohith Market Voice Assistant

A customized voice-powered finance assistant built with Python and Streamlit. The app accepts voice input, identifies the user's market-related intent, fetches stock and news data, analyzes a sample portfolio, and replies with a short spoken summary.

## Highlights

- Voice input with microphone recording
- Text-to-speech output support
- Stock price lookup and simple company comparison
- Portfolio analysis using sample holdings
- News lookup for “why is a stock rising/falling” type queries
- Beginner-friendly project structure and setup guide
- Personalized branding for **Pabba Rohith**

## Tech Stack

- Python
- Streamlit
- yFinance
- Alpha Vantage
- NewsAPI
- AssemblyAI
- AWS Polly
- Requests
- Pandas / NumPy

## Project Structure

```text
rohith-market-voice-assistant/
├── app.py
├── config.json
├── requirements.txt
├── .env.example
├── .gitignore
├── data/
│   └── portfolio.json
├── agents/
│   ├── analysis_agent.py
│   ├── api_agent.py
│   ├── language_agent.py
│   ├── news_agent.py
│   ├── retriever_agent.py
│   └── voice_agent.py
└── orchestrator/
    └── workflow.py
```

## How to Run Locally

### 1. Open terminal inside the project folder

```bash
git clone <your-repo-link>
cd rohith-market-voice-assistant
```

### 2. Create a virtual environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Copy `.env.example` to `.env` and add your real API keys.

### 5. Run the app

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Example Voice Commands

- “What is Tesla stock price?”
- “Compare Apple and Microsoft.”
- “Why is Nvidia rising?”
- “Analyze my portfolio.”
- “Should I sell any stock in my portfolio?”

## Environment Variables

Create a `.env` file with values like these:

```env
ASSEMBLYAI_API_KEY=your_assemblyai_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_newsapi_key
AWS_REGION=us-east-1
VOICE_ID=Joanna
```

## Notes

- This version is cleaned up and personalized for portfolio / GitHub use.
- It is based on the public project idea you shared, with structure and branding simplified for easier learning and pushing to your own GitHub.
- For a polished portfolio repo, add screenshots after running the app.

## Author

**Pabba Rohith**

