from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
import os
from ..core.execution import execute_query

router = APIRouter()

class ExecuteRequest(BaseModel):
    query: str
    db_type: str = "mysql"
    db_uri: str | None = None

@router.post("/")
def exec_query(req: ExecuteRequest):
    result = execute_query(req.query, req.db_type, req.db_uri)
    return result
