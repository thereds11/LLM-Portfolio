# Project 1: Local LLM Chat (FastAPI + SPA)

This project provides a small backend (FastAPI) that calls local LLMs via Ollama, and a tiny single-page app (SPA) in `frontend/` that talks to the backend.

## What changed

- Replaced Streamlit UI with a static SPA in `frontend/` (`index.html`, `main.js`, `styles.css`).
- `app.py` is now a FastAPI server exposing a `/chat` endpoint.
- `requirement.txt` updated with `fastapi` + `uvicorn`.

## Quick start (Windows PowerShell)

1) Install Ollama and pull models you want, e.g.:
```powershell
ollama pull llama3; ollama pull phi3; ollama pull mistral
```

2) Create & activate venv, install deps:
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirement.txt
```

3) Run the backend:
```powershell
python app.py
```

4) Open the SPA: open `frontend/index.html` in your browser (double-click or right-click -> Open). The SPA talks to the backend at `http://localhost:8000`.

Notes:
- Ensure Ollama is running and models are available. The SPA connects to `/ws/chat` for streaming responses.
- The frontend is now a React + Vite app using Chakra UI located in `frontend/`. To run it in dev mode you'll need Node.js and npm.

Frontend dev:
```powershell
cd frontend
npm install
npm run dev
```

Or build for production and serve the `dist/` from the backend static files if desired.

Contributions and improvements are welcome.
