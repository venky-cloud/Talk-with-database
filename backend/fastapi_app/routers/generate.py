from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import re
from ..core.generator import get_generator

router = APIRouter()

class GenerateRequest(BaseModel):
    text: str
    db_schema: Dict[str, Any] | None = None
    db_type: str = "mysql"
    n_candidates: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None

class GenerateResponse(BaseModel):
    candidates: List[str]
    provider: str
    generation_params: Dict[str, Any]

@router.post("/")
def generate(req: GenerateRequest):
    provider = os.getenv("GENERATOR_PROVIDER", "mixtral")
    
    # Safe parsers for env values
    def safe_int(val: str, default: int) -> int:
        try:
            return int(val)
        except Exception:
            m = re.search(r"\d+", str(val) or "")
            return int(m.group(0)) if m else default

    def safe_float(val: str, default: float) -> float:
        try:
            return float(val)
        except Exception:
            m = re.search(r"\d+(?:\.\d+)?", str(val) or "")
            return float(m.group(0)) if m else default

    # Beam search / generation parameters (robust to malformed envs)
    n = req.n_candidates or safe_int(os.getenv("GENERATOR_N_CANDIDATES", "5"), 5)
    temperature = req.temperature or safe_float(os.getenv("GENERATOR_TEMPERATURE", "0.2"), 0.2)
    top_p = req.top_p or safe_float(os.getenv("GENERATOR_TOP_P", "0.95"), 0.95)
    max_tokens = req.max_tokens or safe_int(os.getenv("GENERATOR_MAX_TOKENS", "200"), 200)
    
    gen = get_generator(provider)
    schema_ctx = req.db_schema or {}
    prompt = build_prompt(req.text, schema_ctx, req.db_type)
    
    # Pass generation parameters
    candidates = gen.generate(
        prompt,
        n=n,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    
    generation_params = {
        "n_candidates": n,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    
    return GenerateResponse(
        candidates=candidates,
        provider=provider,
        generation_params=generation_params
    )


def build_prompt(user_text: str, schema: Dict[str, Any], db_type: str) -> str:
    schema_desc = []
    if db_type == "mysql":
        tables = schema.get("tables", [])
        columns = schema.get("columns", {})
        for t in tables[:10]:
            cols = ", ".join([c.get("name") if isinstance(c, dict) else str(c) for c in columns.get(t, [])])
            schema_desc.append(f"Table {t}({cols})")
    elif db_type == "mongodb":
        collections = schema.get("collections", [])
        for c in collections[:10]:
            schema_desc.append(f"Collection {c}")
    schema_str = "\n".join(schema_desc)
    
    system = (
        "You are an expert SQL query generator. Follow these rules strictly:\n"
        "1. Output ONLY the SQL query with NO explanations, markdown, or comments\n"
        "2. Use plain MySQL syntax - DO NOT escape underscores or add backslashes\n"
        "3. Table and column names should be plain text without any escaping (e.g., customer_id NOT customer\\_id)\n"
        "4. Always include a LIMIT clause (default 10 unless specified)\n"
        "5. Use proper JOINs when querying multiple tables\n"
        "6. Follow the provided schema strictly - only use tables and columns that exist\n"
        "7. Generate syntactically correct MySQL queries that will run without errors"
    )
    
    example = (
        "\nExample:\n"
        "User: Show last 5 orders with customer names\n"
        "Query: SELECT o.id, c.name, o.amount, o.created_at FROM orders o JOIN customers c ON o.customer_id = c.id ORDER BY o.created_at DESC LIMIT 5"
    )
    
    return f"[SYSTEM]\n{system}\n{example}\n[DB_TYPE]\n{db_type}\n[SCHEMA]\n{schema_str}\n[USER REQUEST]\n{user_text}\n[SQL QUERY]\n"
