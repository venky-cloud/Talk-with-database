from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Literal
import os
from sqlalchemy import create_engine, text
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from ..core.mongodb_safety import (
    detect_mongodb_injection,
    validate_mongodb_query,
    sanitize_mongodb_query
)
from ..core.mongodb_nlu import (
    classify_mongodb_operation,
    extract_mongodb_entities,
    generate_mongodb_query_variants,
    mongodb_query_to_string
)

router = APIRouter()

class DatabaseRequest(BaseModel):
    db_type: str
    db_uri: Optional[str] = None

class MongoQueryRequest(BaseModel):
    db_name: str
    collection_name: str
    query: Any = {}
    operation: Literal["find","insert","update","delete","count"] = "find"
    document: Optional[Any] = None

    # Allow extra fields without failing validation
    model_config = {"extra": "ignore"}

class MongoNLURequest(BaseModel):
    text: str
    db_schema: Optional[Dict[str, Any]] = None

class MongoGenerateRequest(BaseModel):
    text: str
    db_schema: Optional[Dict[str, Any]] = None
    n_candidates: int = 5

class MongoValidateRequest(BaseModel):
    query: Dict[str, Any]
    operation: str = "find"

@router.post("/inspect")
def inspect_schema(req: DatabaseRequest):
    db_type = req.db_type or os.getenv("DB_TYPE", "mysql")
    db_uri = req.db_uri or (os.getenv("DB_URI") if db_type == "mysql" else os.getenv("MONGO_URI"))

    if db_type == "mysql":
        if not db_uri:
            raise HTTPException(status_code=400, detail="DB_URI not set")
        try:
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MySQL connection error: {str(e)}")

    elif db_type == "mongodb":
        if not db_uri:
            raise HTTPException(status_code=400, detail="MONGO_URI not set")

        try:
            client = MongoClient(db_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            client.admin.command('ping')

            # Get database names
            db_names = client.list_database_names()

            # Get collections for each database
            collections: Dict[str, List[str]] = {}
            for db_name in db_names:
                if db_name not in ['admin', 'local', 'config']:  # Skip system databases
                    db = client[db_name]
                    collections[db_name] = db.list_collection_names()

            return {
                "databases": db_names,
                "collections": collections
            }
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            raise HTTPException(status_code=500, detail=f"MongoDB connection error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MongoDB error: {str(e)}")
        finally:
            if 'client' in locals():
                client.close()

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported db_type: {db_type}")

@router.post("/mongodb-query")
def execute_mongodb_query(req: MongoQueryRequest):
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise HTTPException(status_code=400, detail="MONGO_URI not set")

    try:
        client = MongoClient(mongo_uri)
        db = client[req.db_name]
        collection = db[req.collection_name]

        if req.operation == "find":
            results = list(collection.find(req.query))
            return {
                "operation": "find",
                "count": len(results),
                "documents": results[:100]  # Limit results for safety
            }

        elif req.operation == "insert":
            if not req.document:
                raise HTTPException(status_code=400, detail="Document required for insert operation")
            result = collection.insert_one(req.document)
            return {
                "operation": "insert",
                "inserted_id": str(result.inserted_id),
                "acknowledged": result.acknowledged
            }

        elif req.operation == "update":
            if not req.document:
                raise HTTPException(status_code=400, detail="Document required for update operation")
            result = collection.update_many(req.query, {"$set": req.document})
            return {
                "operation": "update",
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "acknowledged": result.acknowledged
            }

        elif req.operation == "delete":
            result = collection.delete_many(req.query)
            return {
                "operation": "delete",
                "deleted_count": result.deleted_count,
                "acknowledged": result.acknowledged
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {req.operation}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB query error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

@router.post("/nlu")
def mongodb_nlu_parse(req: MongoNLURequest):
    """
    Parse natural language for MongoDB operations.
    Extract operation, collections, fields, and conditions.
    """
    # Classify operation
    operation_result = classify_mongodb_operation(req.text)
    
    # Extract entities
    entities = extract_mongodb_entities(req.text, req.db_schema)
    
    return {
        "operation": operation_result["operation"],
        "confidence": operation_result["confidence"],
        "method": operation_result["method"],
        "entities": entities,
        "all_scores": operation_result.get("all_scores", {})
    }

@router.post("/generate")
def mongodb_generate_queries(req: MongoGenerateRequest):
    """
    Generate MongoDB query candidates from natural language using Mixtral LLM.
    Now uses the same LLM provider as SQL generation.
    """
    from ..core.generator import get_generator
    
    # Try to use Mixtral LLM for MongoDB generation
    try:
        # Get the configured provider (mixtral)
        provider = os.getenv("GENERATOR_PROVIDER", "mongodb_nlu")
        
        if provider == "mixtral":
            # Use Mixtral LLM for generation
            gen = get_generator(provider)
            
            # Build prompt for MongoDB
            schema_ctx = req.db_schema or {}
            
            # Extract collections from schema
            collections_info = ""
            if schema_ctx and "collections" in schema_ctx:
                collections_info = "\nAvailable collections:\n"
                for db_name, collections in schema_ctx["collections"].items():
                    collections_info += f"  Database: {db_name}\n"
                    for col in collections:
                        collections_info += f"    - {col}\n"
            
            prompt = f"""Convert this natural language request into MongoDB query syntax.

{collections_info}

Request: {req.text}

Generate MongoDB queries using the following formats:
- For simple find: db.collection.find({{field: value}})
- For aggregation: db.collection.aggregate([{{$match: ...}}, {{$group: ...}}, {{$sort: ...}}])
- For insert: db.collection.insertOne({{...}})
- For update: db.collection.updateMany({{filter}}, {{$set: {{...}}}})

Generate {req.n_candidates or 3} different valid MongoDB query variations.
Return only the MongoDB queries, one per line, no explanations."""

            # Generate with Mixtral
            result = gen.generate(
                prompt=prompt,
                n_candidates=req.n_candidates or 3,
                temperature=req.temperature or 0.3,
                top_p=req.top_p or 0.95,
                max_tokens=req.max_tokens or 300
            )
            
            # Extract candidates
            candidates = result.get("candidates", [])
            
            if candidates:
                # Clean up queries
                cleaned_queries = []
                for query in candidates:
                    # Remove markdown code blocks if present
                    query = query.strip()
                    if query.startswith("```"):
                        lines = query.split("\n")
                        query = "\n".join(lines[1:-1]) if len(lines) > 2 else query
                    cleaned_queries.append(query.strip())
                
                return {
                    "candidates": cleaned_queries,
                    "count": len(cleaned_queries),
                    "provider": "mixtral"
                }
    
    except Exception as e:
        print(f"Mixtral generation failed: {e}, falling back to rule-based")
    
    # Fallback to rule-based NLU if Mixtral fails or not configured
    variants = generate_mongodb_query_variants(
        req.text,
        req.db_schema,
        req.n_candidates
    )
    
    # Convert to string format
    query_strings = [mongodb_query_to_string(v) for v in variants]
    
    return {
        "candidates": query_strings,
        "candidates_dict": variants,
        "count": len(variants),
        "provider": "mongodb_nlu_fallback"
    }

@router.post("/validate")
def mongodb_validate_query(req: MongoValidateRequest):
    """
    Validate MongoDB query for injection attacks and dangerous operations.
    """
    # Detect injection
    injection_result = detect_mongodb_injection(req.query)
    
    # Validate query
    validation_result = validate_mongodb_query(req.query, req.operation)
    
    return {
        "injection_detected": injection_result["detected"],
        "injection_threats": injection_result["threats"],
        "injection_severity": injection_result["severity"],
        "validation": validation_result,
        "safe": not validation_result["blocked"]
    }

@router.post("/execute")
def mongodb_execute_query(req: MongoQueryRequest):
    """
    Execute MongoDB query with safety validation.
    Similar to SQL execute but for MongoDB.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise HTTPException(status_code=400, detail="MONGO_URI not set")
    
    # Basic request validation
    if not req.db_name or not req.collection_name:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation error",
                "details": ["db_name and collection_name are required"]
            }
        )
    
    # Ensure query is a dictionary
    if not isinstance(req.query, dict):
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation error",
                "details": ["query must be a valid JSON object"]
            }
        )
    
    # For insert/update operations, validate document
    if req.operation in ["insert", "update"] and not req.document:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Validation error",
                "details": ["document is required for insert/update operations"]
            }
        )
    
    # Validate query first
    try:
        validation_result = validate_mongodb_query(req.query, req.operation)
        if validation_result.get("blocked", False):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Query blocked by safety validation",
                    "reasons": validation_result.get("reasons", ["Unknown validation error"])
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Query validation failed",
                "details": [str(e)]
            }
        )
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[req.db_name]
        collection = db[req.collection_name]
        
        results = {
            "operation": req.operation,
            "collection": req.collection_name,
            "database": req.db_name,
            "success": False
        }
        
        if req.operation == "find":
            docs = list(collection.find(req.query).limit(100))
            # Convert ObjectId to string
            for doc in docs:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            results["success"] = True
            results["count"] = len(docs)
            results["documents"] = docs
            
        elif req.operation == "insert":
            if not req.document:
                raise HTTPException(status_code=400, detail="Document required for insert")
            result = collection.insert_one(req.document)
            results["success"] = True
            results["inserted_id"] = str(result.inserted_id)
            
        elif req.operation == "update":
            if not req.document:
                raise HTTPException(status_code=400, detail="Document required for update")
            result = collection.update_many(req.query, {"$set": req.document})
            results["success"] = True
            results["matched_count"] = result.matched_count
            results["modified_count"] = result.modified_count
            
        elif req.operation == "delete":
            result = collection.delete_many(req.query)
            results["success"] = True
            results["deleted_count"] = result.deleted_count
            
        elif req.operation == "count":
            count = collection.count_documents(req.query)
            results["success"] = True
            results["count"] = count
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {req.operation}")
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB execution error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()
