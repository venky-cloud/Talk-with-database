from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from ..core.safety import validate_query

router = APIRouter()

class ValidateRequest(BaseModel):
    candidates: List[str]
    db_type: str = "mysql"

@router.post("/")
def validate(req: ValidateRequest):
    results = [validate_query(q, req.db_type) for q in req.candidates]
    return {"results": results}
