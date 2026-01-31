from __future__ import annotations
from typing import List, Dict, Any
from sqlglot import parse_one, exp

try:
    from sentence_transformers import SentenceTransformer, util
    _embed = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    _embed = None


def rank_candidates(text: str, candidates: List[str], schema: Dict[str, Any], db_type: str) -> List[Dict[str, Any]]:
    ranked = []
    for q in candidates:
        syntax_ok = False
        try:
            parse_one(q, read=db_type)
            syntax_ok = True
        except Exception:
            syntax_ok = False
        # simple schema match: count occurrences of table names
        schema_score = 0.0
        tables = schema.get("tables", [])
        if tables:
            matches = sum(1 for t in tables if t.lower() in q.lower())
            schema_score = matches / max(1, len(tables))
        sim_score = 0.0
        if _embed:
            try:
                sim = util.cos_sim(_embed.encode([text], convert_to_tensor=True), _embed.encode([q], convert_to_tensor=True))
                sim_score = float(sim[0][0])
            except Exception:
                sim_score = 0.0
        score = (1.0 if syntax_ok else 0.0) + schema_score + sim_score
        ranked.append({"query": q, "score": score, "syntax_ok": syntax_ok, "schema_score": schema_score, "sim": sim_score})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
