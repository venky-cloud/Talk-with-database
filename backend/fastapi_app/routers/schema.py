from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
import os
from sqlalchemy import create_engine, text
from pymongo import MongoClient

router = APIRouter()

class SchemaRequest(BaseModel):
    db_type: str | None = None
    db_uri: str | None = None

@router.post("/inspect")
def inspect_schema(req: SchemaRequest):
    db_type = req.db_type or os.getenv("DB_TYPE", "mysql")
    db_uri = req.db_uri or os.getenv("DB_URI")
    if db_type == "mysql":
        if not db_uri:
            return {"error": "DB_URI not set"}
        engine = create_engine(db_uri)
        with engine.connect() as conn:
            current_db = conn.execute(text("SELECT DATABASE()"))
            dbname = list(current_db)[0][0]
            
            # Get all tables
            tables = conn.execute(text(
                """
                SELECT TABLE_NAME FROM information_schema.tables
                WHERE table_schema = :db
                ORDER BY TABLE_NAME
                """
            ), {"db": dbname}).fetchall()
            table_names = [t[0] for t in tables]
            
            # Get columns with additional details
            columns: Dict[str, List[Dict[str, Any]]] = {}
            primary_keys: Dict[str, List[str]] = {}
            indexes: Dict[str, List[Dict[str, Any]]] = {}
            
            for t in table_names:
                # Get columns
                cols = conn.execute(text(
                    """
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
                    FROM information_schema.columns
                    WHERE table_schema = :db AND table_name = :t
                    ORDER BY ORDINAL_POSITION
                    """
                ), {"db": dbname, "t": t}).fetchall()
                columns[t] = [
                    {
                        "name": c[0], 
                        "type": c[1], 
                        "nullable": c[2],
                        "key": c[3],
                        "default": c[4],
                        "extra": c[5]
                    } for c in cols
                ]
                
                # Get primary keys
                pk_cols = [c[0] for c in cols if c[3] == "PRI"]
                if pk_cols:
                    primary_keys[t] = pk_cols
                
                # Get indexes
                idx_result = conn.execute(text(
                    """
                    SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE
                    FROM information_schema.statistics
                    WHERE table_schema = :db AND table_name = :t
                    ORDER BY INDEX_NAME, SEQ_IN_INDEX
                    """
                ), {"db": dbname, "t": t}).fetchall()
                
                idx_dict = {}
                for idx_name, col_name, non_unique in idx_result:
                    if idx_name not in idx_dict:
                        idx_dict[idx_name] = {
                            "name": idx_name,
                            "columns": [],
                            "unique": non_unique == 0
                        }
                    idx_dict[idx_name]["columns"].append(col_name)
                indexes[t] = list(idx_dict.values())
            
            # Get foreign key relationships
            fk_result = conn.execute(text(
                """
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME,
                    CONSTRAINT_NAME
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE table_schema = :db 
                    AND REFERENCED_TABLE_NAME IS NOT NULL
                ORDER BY TABLE_NAME, CONSTRAINT_NAME
                """
            ), {"db": dbname}).fetchall()
            
            foreign_keys = []
            for fk in fk_result:
                foreign_keys.append({
                    "from_table": fk[0],
                    "from_column": fk[1],
                    "to_table": fk[2],
                    "to_column": fk[3],
                    "constraint_name": fk[4]
                })
        
        return {
            "db": dbname, 
            "tables": table_names, 
            "columns": columns,
            "primary_keys": primary_keys,
            "indexes": indexes,
            "foreign_keys": foreign_keys
        }
    elif db_type == "mongodb":
        mongo_uri = db_uri or os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri)
        dbname = client.get_default_database().name if client.get_default_database() else "default"
        db = client[dbname]
        collections = db.list_collection_names()
        return {"db": dbname, "collections": collections}
    else:
        return {"error": f"Unsupported db_type: {db_type}"}
