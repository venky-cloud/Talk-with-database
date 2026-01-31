from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from ..core.ranking import rank_candidates

router = APIRouter()

class RankRequest(BaseModel):
    text: str
    candidates: List[str]
    db_schema: Dict[str, Any] | None = None
    db_type: str = "mysql"

@router.post("/")
def rank(req: RankRequest):
    ranked = rank_candidates(req.text, req.candidates, req.db_schema or {}, req.db_type)
    return {"ranked": ranked}
