# AI Calling Agent

Production-grade AI calling agent using Groq API, Jambonz, and Flask.

## Features
- Real-time voice conversation API
- Groq API integration (mixtral-8x7b-32768 model)
- Jambonz phone system integration
- Flask REST API with `/api/call` endpoint
- Cloud deployed on Railway (free tier)
- Mock response fallback for testing

## Tech Stack
- **Backend**: Flask, Python 3.13
- **LLM**: Groq API (free tier)
- **Phone**: Jambonz (open-source)
- **Deployment**: Railway
- **Database**: SQLite

## Live URL
https://echo-web-production-375e.up.railway.app

## API Endpoint
POST /api/call
Request:
{
“message”: “What is AI?”
}

Response:
{
“status”: “success”,
“input”: “What is AI?”,
“response”: “AI is artificial intelligence...”
}

## Setup
```bash
pip install -r requirements.txt
export GROQ_API_KEY=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
python server.py
```

## Architecture
User → Jambonz → Flask Server → Groq API → Response

---