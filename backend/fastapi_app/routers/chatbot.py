import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests

router = APIRouter()

MIXTRAL_API_KEY = os.getenv("MIXTRAL_API_KEY") or os.getenv("MISTRAL_API_KEY") or os.getenv("OPENROUTER_API_KEY")
MIXTRAL_PROVIDER = os.getenv("MIXTRAL_PROVIDER", "openrouter")  # 'mistral' or 'openrouter'
MIXTRAL_MODEL = os.getenv("MIXTRAL_MODEL", "mistralai/mixtral-8x7b-instruct")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    reply: str
    used_model: Optional[str] = None
    provider: Optional[str] = None
    mode: str  # 'llm' or 'fallback'

RESTRICTION = "I can only answer questions related to the project documentation."

# Minimal project context loader
_cached_context: Optional[str] = None

def load_project_context() -> str:
    global _cached_context
    if _cached_context:
        return _cached_context
    parts: List[str] = []
    try:
        if os.path.exists(README_PATH):
            with open(README_PATH, "r", encoding="utf-8") as f:
                parts.append(f.read())
    except Exception:
        pass
    # Add known backend endpoints overview
    parts.append("Endpoints: /schema, /generate, /validate, /rank, /execute, /mongodb, /history, /api, /generate/sql/generate-multiple, /generate/mongodb/generate-multiple")
    _cached_context = "\n\n".join(parts)
    return _cached_context

# Simple scope guard: if nothing overlaps with known keywords, reject
KEYWORDS = [
    "sql", "mysql", "mongodb", "schema", "workbench", "query", "api", "history",
    "login", "dashboard", "vite", "react", "fastapi", "tailwind", "tables", "orders", "customers"
]


def is_in_scope(text: str) -> bool:
    # Relaxed: treat most questions as in-scope unless clearly unrelated keywords are found
    t = (text or "").lower()
    if any(k in t for k in KEYWORDS):
        return True
    # Allow general how-to questions
    if any(p in t for p in ["how to", "run", "start", "setup", "install", "query", "login", "dashboard"]):
        return True
    return True


def call_mixtral(prompt: str, context: str) -> str:
    if MIXTRAL_PROVIDER == "mistral":
        # Mistral API
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MIXTRAL_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": MIXTRAL_MODEL,
            "messages": [
                {"role": "system", "content": "You are an advanced AI assistant built for this project. Answer ONLY using the provided project context. If out of scope, say: 'I can only answer questions related to the project documentation.'"},
                {"role": "user", "content": f"Project context:\n\n{context}\n\nUser question: {prompt}"}
            ],
            "temperature": 0.2,
        }
        r = requests.post(url, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    else:
        # OpenRouter style
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {MIXTRAL_API_KEY}", "Content-Type": "application/json"}
        body = {
            "model": MIXTRAL_MODEL,
            "messages": [
                {"role": "system", "content": "You are an advanced AI assistant built for this project. Answer ONLY using the provided project context. If out of scope, say: 'I can only answer questions related to the project documentation.'"},
                {"role": "user", "content": f"Project context:\n\n{context}\n\nUser question: {prompt}"}
            ],
            "temperature": 0.2,
        }
        r = requests.post(url, json=body, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


@router.post("/chatbot/ask", response_model=ChatResponse)
def ask_chatbot(req: ChatRequest) -> ChatResponse:
    question = (req.message or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Empty message")

    # Relaxed: continue even if not matching strict keywords

    context = load_project_context()

    if MIXTRAL_API_KEY:
        try:
            answer = call_mixtral(question, context)
            # Enforce policy on response content just in case
            if "I can only answer" in answer:
                return ChatResponse(reply=RESTRICTION, used_model=MIXTRAL_MODEL, provider=MIXTRAL_PROVIDER, mode="llm")
            return ChatResponse(reply=answer, used_model=MIXTRAL_MODEL, provider=MIXTRAL_PROVIDER, mode="llm")
        except Exception as e:
            # Fallback if API fails
            pass

    # Fallback: simple canned answers for common queries
    q = question.lower()
    canned = None
    if any(k in q for k in ["run project", "start project", "how to run", "setup"]):
        canned = (
            "Frontend: npm install && npm run dev (project/).\n"
            "Backend: create venv, pip install -r backend/requirements.txt, then uvicorn fastapi_app.main:app --reload --port 8000.\n"
            "MySQL: ensure running on port 3307 (db talkwithdata). MongoDB: localhost:27017."
        )
    elif any(k in q for k in ["run query", "execute query", "sql query", "mongodb query"]):
        canned = (
            "SQL: use SQL Query or SQL Workbench, generate or type your query, then Run.\n"
            "MongoDB: use MongoDB Query/Workbench; generate variants, Insert, then Execute."
        )
    elif any(k in q for k in ["login", "auth", "sign in"]):
        canned = "Open /login, demo@example.com / demo123; app redirects to /home after sign-in."
    elif any(k in q for k in ["how to use", "how do i use", "guide", "help"]):
        canned = (
            "1) Sign in at /login (demo@example.com / demo123).\n"
            "2) Go to SQL Query or MongoDB Query: enter your prompt, Generate Variants, Insert, then Run.\n"
            "3) Use Workbenches for manual queries and tabs.\n"
            "4) See results in Dashboard/History; use Schema Workbench for table details."
        )

    if canned:
        return ChatResponse(reply=canned, used_model=None, provider=None, mode="fallback")

    # As last resort, generic friendly reply without raw markdown
    return ChatResponse(
        reply="Ask about running the project, generating SQL/Mongo queries, using workbenches, or viewing dashboard/history.",
        used_model=None,
        provider=None,
        mode="fallback",
    )
