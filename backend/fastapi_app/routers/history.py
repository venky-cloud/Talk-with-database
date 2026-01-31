from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

router = APIRouter()

# Simple file-based storage for history (can be replaced with database later)
HISTORY_FILE = "query_history.json"

class QueryHistoryItem(BaseModel):
    id: str
    query_text: str
    generated_sql: str
    query_type: str  # "mysql" or "mongodb"
    status: str  # "success" or "error"
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: str

class SaveQueryRequest(BaseModel):
    query_text: str
    generated_sql: str
    query_type: str = "mysql"
    status: str = "success"
    result_count: Optional[int] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[float] = None

def load_history() -> List[Dict[str, Any]]:
    """Load query history from file"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_history(history: List[Dict[str, Any]]):
    """Save query history to file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save history: {str(e)}")

@router.get("/list")
def get_history(limit: int = 50, offset: int = 0):
    """Get query history with pagination"""
    try:
        history = load_history()
        # Sort by created_at descending (most recent first)
        history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        total = len(history)
        paginated = history[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": paginated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
def save_query(req: SaveQueryRequest):
    """Save a query to history"""
    try:
        history = load_history()
        
        # Generate unique ID
        import uuid
        new_id = str(uuid.uuid4())
        
        # Create new history item
        new_item = {
            "id": new_id,
            "query_text": req.query_text,
            "generated_sql": req.generated_sql,
            "query_type": req.query_type,
            "status": req.status,
            "result_count": req.result_count,
            "error_message": req.error_message,
            "execution_time_ms": req.execution_time_ms,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Add to history
        history.append(new_item)
        
        # Keep only last 1000 items to prevent file from growing too large
        if len(history) > 1000:
            history = history[-1000:]
        
        save_history(history)
        
        return {
            "success": True,
            "id": new_id,
            "message": "Query saved to history"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{query_id}")
def delete_query(query_id: str):
    """Delete a query from history"""
    try:
        history = load_history()
        
        # Filter out the query with matching id
        new_history = [item for item in history if item.get('id') != query_id]
        
        if len(new_history) == len(history):
            raise HTTPException(status_code=404, detail="Query not found")
        
        save_history(new_history)
        
        return {
            "success": True,
            "message": "Query deleted from history"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
def clear_history():
    """Clear all query history"""
    try:
        save_history([])
        return {
            "success": True,
            "message": "History cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
def get_stats():
    """Get query history statistics"""
    try:
        history = load_history()
        
        total_queries = len(history)
        success_count = len([h for h in history if h.get('status') == 'success'])
        error_count = len([h for h in history if h.get('status') == 'error'])
        
        # Get query types breakdown
        mysql_count = len([h for h in history if h.get('query_type') == 'mysql'])
        mongodb_count = len([h for h in history if h.get('query_type') == 'mongodb'])
        
        # Calculate average execution time
        execution_times = [h.get('execution_time_ms', 0) for h in history if h.get('execution_time_ms')]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_queries": total_queries,
            "success_count": success_count,
            "error_count": error_count,
            "mysql_count": mysql_count,
            "mongodb_count": mongodb_count,
            "avg_execution_time_ms": round(avg_execution_time, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
