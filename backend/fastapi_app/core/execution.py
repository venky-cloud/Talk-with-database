from __future__ import annotations
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Result
from pymongo import MongoClient
from .config import settings


def _log_to_mongo(doc: Dict[str, Any]):
    try:
        if settings.MONGO_URI:
            client = MongoClient(settings.MONGO_URI)
            db = client.get_default_database() or client["twdb"]
            db["query_logs"].insert_one(doc)
    except Exception:
        pass


def execute_query(query: str, db_type: str = "mysql", db_uri: str | None = None) -> Dict[str, Any]:
    if db_type != "mysql":
        return {"error": f"Unsupported db_type for execution: {db_type}"}
    uri = db_uri or settings.DB_URI
    if not uri:
        return {"error": "DB_URI not configured"}
    engine = create_engine(uri)
    # enforce limit cap for SELECT without limit
    q = query
    if q.strip().lower().startswith("select") and " limit " not in q.lower():
        q = q.rstrip(";") + f" LIMIT {settings.SELECT_LIMIT_CAP}"
    try:
        with engine.connect() as conn:
            res: Result = conn.execute(text(q))
            if res.returns_rows:
                rows = [dict(r._mapping) for r in res.fetchall()]
                out = {"rows": rows, "row_count": len(rows)}
            else:
                out = {"row_count": res.rowcount}
        _log_to_mongo({"query": q, "db_type": db_type, "success": True})
        return out
    except Exception as e:
        _log_to_mongo({"query": q, "db_type": db_type, "success": False, "error": str(e)})
        return {"error": str(e)}
