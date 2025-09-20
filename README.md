# English Conversation Practice Web App

A two-part application that turns the previous command line English practice tool into a browser-based experience. The frontend is a React single-page application that records microphone input and displays helpful resources. A FastAPI backend proxies audio clips to the ChatGPT voice conversation API so the learner can speak naturally and hear AI feedback.

## Project structure

- `backend/` – FastAPI service that exposes REST endpoints for scenarios and voice chat.
- `frontend/` – React/Vite project that renders the UI and records audio via the MediaRecorder API.

## Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key with access to the ChatGPT voice conversation features.

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
uvicorn app.main:app --reload
```

You can optionally configure CORS origins by setting `FRONTEND_ORIGINS` with a comma separated list of allowed origins (defaults to `*`).

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file inside `frontend/` if you need to override the backend URL:

```
VITE_API_BASE=http://localhost:8000
```

The dev server will run on http://localhost:5173 and proxy API requests directly to the backend.

## Voice conversation flow

1. The user chooses a scenario and begins recording.
2. The frontend sends the captured audio blob to the backend.
3. The backend transcribes the learner's speech and forwards the audio to the ChatGPT voice conversation API.
4. The assistant's text and audio reply are sent back to the browser along with updated conversation history.

Both text and audio are stored in the session history so learners can replay answers or read transcripts while reviewing tips and phrasebook entries for the selected scenario.

