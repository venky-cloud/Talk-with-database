from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import re
from ..core.generator import get_generator

router = APIRouter()

class ApiGenerateRequest(BaseModel):
    text: str
    api_schema: Optional[Dict[str, Any]] = None
    mode: str = "auto"
    n_candidates: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None

class ApiGenerateResponse(BaseModel):
    candidates: List[str]
    provider: str
    mode: str

def _fallback_generate_rest(text: str, schema: Optional[Dict[str, Any]]) -> List[str]:
    t = text.lower()
    method = "GET"
    if any(k in t for k in ["create", "add", "insert", "post"]):
        method = "POST"
    elif any(k in t for k in ["update", "modify", "patch"]):
        method = "PATCH"
    elif any(k in t for k in ["put", "replace"]):
        method = "PUT"
    elif any(k in t for k in ["delete", "remove"]):
        method = "DELETE"
    resource = "items"
    nouns = ["users", "orders", "products", "customers", "invoices", "items"]
    for n in nouns:
        if n in t:
            resource = n
            break
    params = {}
    if "last" in t or "recent" in t:
        params["sort"] = "desc"
    if "top" in t:
        params["limit"] = 10
    if "limit" in t:
        params["limit"] = 10
    body = {}
    if method in ["POST", "PUT", "PATCH"]:
        body = {"example": True}
    candidate = {
        "method": method,
        "path": f"/{resource}",
        "params": params,
        "headers": {"Content-Type": "application/json"},
        "body": body
    }
    return [json_dump(candidate)]

def _fallback_generate_graphql(text: str, schema: Optional[Dict[str, Any]]) -> List[str]:
    t = text.lower()
    op = "query"
    field = "items"
    nouns = ["users", "orders", "products", "customers", "invoices", "items"]
    for n in nouns:
        if n in t:
            field = n
            break
    q = f"{op} {{ {field}(limit: 10) {{ id }} }}"
    return [q]

def json_dump(obj: Dict[str, Any]) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False)

def build_rest_prompt(text: str, schema: Optional[Dict[str, Any]]) -> str:
    resources = []
    if schema and isinstance(schema.get("resources"), list):
        for r in schema.get("resources", [])[:10]:
            resources.append(str(r))
    schema_str = "\n".join(resources)
    rules = (
        "You are an API request generator. Output only JSON per candidate. "
        "Use this structure: {\"method\": \"GET|POST|PUT|PATCH|DELETE\", \"path\": \"/resource\", \"params\": {..}, \"headers\": {..}, \"body\": {..}} "
        "Do not include explanations or code fences."
    )
    return f"[RULES]\n{rules}\n[RESOURCES]\n{schema_str}\n[USER]\n{text}\n[OUTPUT]\n"

def build_graphql_prompt(text: str, schema: Optional[Dict[str, Any]]) -> str:
    types = []
    if schema and isinstance(schema.get("types"), list):
        for t in schema.get("types", [])[:10]:
            types.append(str(t))
    schema_str = "\n".join(types)
    rules = (
        "You are a GraphQL generator. Output only a single query or mutation string. "
        "Prefer simple queries with a small selection set like id,name. No explanations."
    )
    return f"[RULES]\n{rules}\n[SCHEMA]\n{schema_str}\n[USER]\n{text}\n[GRAPHQL]\n"

@router.post("/generate")
def generate(req: ApiGenerateRequest):
    provider = os.getenv("GENERATOR_PROVIDER", "mixtral")
    # Safe parsers
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

    n = req.n_candidates or safe_int(os.getenv("GENERATOR_N_CANDIDATES", "3"), 3)
    temperature = req.temperature or safe_float(os.getenv("GENERATOR_TEMPERATURE", "0.2"), 0.2)
    top_p = req.top_p or safe_float(os.getenv("GENERATOR_TOP_P", "0.95"), 0.95)
    max_tokens = req.max_tokens or safe_int(os.getenv("GENERATOR_MAX_TOKENS", "200"), 200)

    mode = req.mode.lower()
    gen = None
    try:
        gen = get_generator(provider)
    except Exception:
        gen = None
    out_mode = "rest" if mode in ["rest", "auto"] else "graphql"
    if gen:
        try:
            if mode in ["rest", "auto"]:
                prompt = build_rest_prompt(req.text, req.api_schema)
                cands = gen.generate(prompt, n=n, temperature=temperature, top_p=top_p, max_tokens=max_tokens)
                return ApiGenerateResponse(candidates=cands, provider=provider, mode="rest")
            else:
                prompt = build_graphql_prompt(req.text, req.api_schema)
                cands = gen.generate(prompt, n=n, temperature=temperature, top_p=top_p, max_tokens=max_tokens)
                return ApiGenerateResponse(candidates=cands, provider=provider, mode="graphql")
        except Exception:
            pass
    if out_mode == "rest":
        return ApiGenerateResponse(candidates=_fallback_generate_rest(req.text, req.api_schema), provider="fallback", mode="rest")
    return ApiGenerateResponse(candidates=_fallback_generate_graphql(req.text, req.api_schema), provider="fallback", mode="graphql")