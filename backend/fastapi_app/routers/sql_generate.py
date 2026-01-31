from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    database: Optional[str] = "mysql"
    count: int = 5
    schema: Optional[Dict[str, Any]] = None

class SQLVariant(BaseModel):
    title: str
    sql: str
    notes: Optional[str] = None

class GenerateResponse(BaseModel):
    variants: List[SQLVariant]

@router.post("/sql/generate-multiple", response_model=GenerateResponse)
async def generate_sql_variants(payload: GenerateRequest) -> GenerateResponse:
    prompt = payload.prompt.strip()
    n = max(1, min(payload.count, 10))

    # Very simple rule-based templates; can be replaced with LLM later.
    templates = [
        ("Direct SELECT", "SELECT * FROM {table} LIMIT 100;", "Basic select."),
        ("Filtered", "SELECT * FROM {table} WHERE {filter} LIMIT 100;", "Add simple filter."),
        ("Aggregation", "SELECT {group_col}, COUNT(*) AS cnt FROM {table} GROUP BY {group_col} ORDER BY cnt DESC LIMIT 100;", "Group by example."),
        ("Join Customers/Orders", "SELECT c.id, c.name, SUM(o.amount) total_amount FROM customers c JOIN orders o ON o.customer_id = c.id GROUP BY c.id, c.name ORDER BY total_amount DESC LIMIT 100;", "Common e-commerce join."),
        ("Date Range Param", "SELECT * FROM {table} WHERE created_at BETWEEN :start AND :end;", "Use parameters for safer queries."),
        ("CTE", "WITH t AS (SELECT * FROM {table}) SELECT * FROM t LIMIT 100;", "CTE skeleton."),
        ("Window Function", "SELECT *, ROW_NUMBER() OVER (ORDER BY created_at DESC) rn FROM {table} LIMIT 100;", "Window example."),
    ]

    # naive parsed tokens from prompt
    table = "orders" if "order" in prompt.lower() else "customers"
    group_col = "customer_id" if table == "orders" else "email"
    filter_expr = "amount > 0" if table == "orders" else "email LIKE '%@%'"

    variants: List[SQLVariant] = []
    for i, (title, sql, notes) in enumerate(templates[:n]):
        sql_f = sql.format(table=table, group_col=group_col, filter=filter_expr)
        variants.append(SQLVariant(title=title, sql=sql_f, notes=notes))

    return GenerateResponse(variants=variants)
