"""
MongoDB-specific NLU: Intent Classification & Entity Recognition
Extract collections, fields, and operations from natural language
"""

import re
from typing import Dict, List, Any, Optional

# MongoDB operation keywords
MONGODB_OPERATIONS = {
    "find": [
        r'\b(find|search|get|show|list|display|retrieve|fetch|select)\b',
        r'\b(all|every)\b.*\b(documents?|records?|items?)\b',
    ],
    "insert": [
        r'\b(insert|add|create|save|put|new)\b',
        r'\b(document|record|item|entry)\b',
    ],
    "update": [
        r'\b(update|modify|change|edit|set|alter)\b',
    ],
    "delete": [
        r'\b(delete|remove|drop|destroy|erase)\b',
    ],
    "aggregate": [
        r'\b(aggregate|group|sum|count|average|stats)\b',
        r'\b(pipeline|stage)\b',
    ],
    "count": [
        r'\b(count|total|number\s+of)\b',
    ],
}

def classify_mongodb_operation(text: str) -> Dict[str, Any]:
    """
    Classify MongoDB operation from natural language.
    Similar to SQL intent classification but for MongoDB.
    """
    text_lower = text.lower()
    scores = {}
    
    for operation, patterns in MONGODB_OPERATIONS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score += 1
        if score > 0:
            scores[operation] = score
    
    if not scores:
        return {
            "operation": "find",  # Default to find
            "confidence": 0.3,
            "method": "default"
        }
    
    # Get operation with highest score
    best_operation = max(scores, key=scores.get)
    confidence = scores[best_operation] / len(MONGODB_OPERATIONS[best_operation])
    
    return {
        "operation": best_operation,
        "confidence": min(confidence, 1.0),
        "method": "keyword",
        "all_scores": scores
    }

def extract_mongodb_entities(text: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, List[str]]:
    """
    Extract MongoDB-specific entities from text:
    - collections (similar to SQL tables)
    - fields (similar to SQL columns)
    - values
    - conditions
    """
    entities = {
        "collections": [],
        "fields": [],
        "values": [],
        "conditions": [],
        "operators": []
    }
    
    text_lower = text.lower()
    
    # Extract collections from schema
    if schema and "collections" in schema:
        for db_name, collections in schema["collections"].items():
            for collection in collections:
                if collection.lower() in text_lower:
                    entities["collections"].append(collection)
    
    # Pattern-based collection detection
    collection_patterns = [
        r'\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\bin\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+collection',
        r'\bcollection\s+([a-zA-Z_][a-zA-Z0-9_]*)',
    ]
    
    for pattern in collection_patterns:
        matches = re.findall(pattern, text_lower)
        entities["collections"].extend(matches)
    
    # Extract fields (document properties)
    field_patterns = [
        r'\b(where|with|having)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(equals?|is|=|:)',
        r'\bfield\s+([a-zA-Z_][a-zA-Z0-9_]*)',
    ]
    
    for pattern in field_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    entities["fields"].append(match[-1])
                else:
                    entities["fields"].append(match)
    
    # Extract conditions
    condition_keywords = [
        "greater than", "less than", "equal to", "not equal",
        "contains", "matches", "starts with", "ends with"
    ]
    
    for keyword in condition_keywords:
        if keyword in text_lower:
            entities["conditions"].append(keyword)
    
    # Extract MongoDB operators mentioned
    mongodb_operators = [
        "$eq", "$ne", "$gt", "$gte", "$lt", "$lte",
        "$in", "$nin", "$and", "$or", "$not",
        "$exists", "$regex", "$text", "$where"
    ]
    
    for operator in mongodb_operators:
        if operator in text_lower:
            entities["operators"].append(operator)
    
    # Extract quoted values
    quoted_values = re.findall(r'["\']([^"\']+)["\']', text)
    entities["values"].extend(quoted_values)
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities

def build_mongodb_query_from_nlu(
    text: str,
    operation: str,
    entities: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Build MongoDB query from NLU analysis.
    Enhanced to support aggregation pipelines.
    """
    query = {}
    text_lower = text.lower()
    
    # Extract collection
    collection = entities["collections"][0] if entities["collections"] else "collection"
    
    # Check if this is an aggregation query
    is_aggregation = operation == "aggregate" or any(word in text_lower for word in 
        ["aggregate", "group by", "sum", "average", "count by", "total", "max", "min"])
    
    if is_aggregation:
        # Build aggregation pipeline
        pipeline = []
        
        # $match stage (filtering)
        match_stage = {}
        
        # Extract status/state conditions
        if "status" in text_lower:
            if "in [" in text_lower or "in (" in text_lower:
                # Extract array values
                status_match = re.search(r'status\s+in\s+[\[\(]([^\]\)]+)[\]\)]', text_lower)
                if status_match:
                    statuses = [s.strip(' "\',') for s in status_match.group(1).split(',')]
                    match_stage["status"] = {"$in": statuses}
            elif "=" in text_lower or "is" in text_lower:
                status_match = re.search(r'status\s+(?:=|is)\s+["\']?(\w+)["\']?', text_lower)
                if status_match:
                    match_stage["status"] = status_match.group(1)
        
        # Date range conditions
        if "last" in text_lower and "days" in text_lower:
            days_match = re.search(r'last\s+(\d+)\s+days', text_lower)
            if days_match:
                days = int(days_match.group(1))
                from datetime import datetime, timedelta
                date_threshold = datetime.now() - timedelta(days=days)
                match_stage["order_date"] = {"$gte": date_threshold.isoformat()}
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # $group stage
        group_stage = {"_id": None}
        
        # Find group by field
        group_by_match = re.search(r'(?:by|per)\s+(\w+)', text_lower)
        if group_by_match:
            group_field = group_by_match.group(1)
            group_stage["_id"] = f"${group_field}"
        
        # Add aggregation functions
        if "sum" in text_lower or "total" in text_lower or "revenue" in text_lower:
            # Find the field to sum
            sum_field = "total_amount"
            if "revenue" in text_lower:
                sum_field = "total_amount"
            group_stage["total_revenue"] = {"$sum": f"${sum_field}"}
        
        if "count" in text_lower or "number of" in text_lower:
            group_stage["count"] = {"$sum": 1}
        
        if "average" in text_lower or "avg" in text_lower:
            avg_match = re.search(r'average\s+(\w+)', text_lower)
            if avg_match:
                group_stage["average"] = {"$avg": f"${avg_match.group(1)}"}
        
        pipeline.append({"$group": group_stage})
        
        # $sort stage
        if "sort" in text_lower:
            sort_stage = {}
            if "desc" in text_lower or "descending" in text_lower or "highest" in text_lower:
                # Sort by revenue/total desc
                if "revenue" in text_lower or "total" in text_lower:
                    sort_stage = {"total_revenue": -1}
                else:
                    sort_stage = {"count": -1}
            else:
                sort_stage = {"_id": 1}
            
            pipeline.append({"$sort": sort_stage})
        
        # $limit stage
        limit_match = re.search(r'limit\s+(\d+)|top\s+(\d+)', text_lower)
        if limit_match:
            limit_val = int(limit_match.group(1) or limit_match.group(2))
            pipeline.append({"$limit": limit_val})
        
        return {
            "collection": collection,
            "query": {},
            "operation": "aggregate",
            "pipeline": pipeline
        }
    
    else:
        # Regular find query
        # Build filter based on entities
        if entities["fields"] and entities["values"]:
            for i, field in enumerate(entities["fields"]):
                if i < len(entities["values"]):
                    query[field] = entities["values"][i]
        
        # Handle conditions
        if "greater than" in entities["conditions"] and entities["fields"]:
            field = entities["fields"][0]
            if entities["values"]:
                query[field] = {"$gt": entities["values"][0]}
        
        if "less than" in entities["conditions"] and entities["fields"]:
            field = entities["fields"][0]
            if entities["values"]:
                query[field] = {"$lt": entities["values"][0]}
        
        if "not equal" in entities["conditions"] and entities["fields"]:
            field = entities["fields"][0]
            if entities["values"]:
                query[field] = {"$ne": entities["values"][0]}
        
        return {
            "collection": collection,
            "query": query,
            "operation": operation
        }

def generate_mongodb_query_variants(
    text: str,
    schema: Optional[Dict[str, Any]] = None,
    n_candidates: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate multiple MongoDB query candidates.
    Similar to SQL generation but for MongoDB.
    """
    # Classify operation
    op_result = classify_mongodb_operation(text)
    operation = op_result["operation"]
    
    # Extract entities
    entities = extract_mongodb_entities(text, schema)
    
    # Generate base query
    base_query = build_mongodb_query_from_nlu(text, operation, entities)
    
    variants = [base_query]
    
    # Generate variants with different query structures
    if entities["fields"] and entities["values"]:
        # Variant 1: Exact match
        variant1 = base_query.copy()
        variants.append(variant1)
        
        # Variant 2: Case-insensitive match
        variant2 = base_query.copy()
        if entities["fields"]:
            field = entities["fields"][0]
            if entities["values"]:
                variant2["query"] = {
                    field: {"$regex": entities["values"][0], "$options": "i"}
                }
                variants.append(variant2)
        
        # Variant 3: Multiple fields (if available)
        if len(entities["fields"]) > 1:
            variant3 = base_query.copy()
            variant3["query"] = {}
            for i, field in enumerate(entities["fields"][:2]):
                if i < len(entities["values"]):
                    variant3["query"][field] = entities["values"][i]
            variants.append(variant3)
        
        # Variant 4: With projection (limit fields)
        if len(entities["fields"]) > 0:
            variant4 = base_query.copy()
            variant4["projection"] = {field: 1 for field in entities["fields"][:3]}
            variant4["projection"]["_id"] = 0
            variants.append(variant4)
    
    # Limit to n_candidates
    return variants[:n_candidates]

def mongodb_query_to_string(query_dict: Dict[str, Any]) -> str:
    """
    Convert MongoDB query dict to readable string format.
    Enhanced to support aggregation pipelines.
    """
    import json
    
    collection = query_dict.get("collection", "collection")
    operation = query_dict.get("operation", "find")
    query = query_dict.get("query", {})
    projection = query_dict.get("projection")
    pipeline = query_dict.get("pipeline")
    
    # Handle aggregation pipeline
    if operation == "aggregate" and pipeline:
        query_str = f"db.{collection}.aggregate([\n"
        for i, stage in enumerate(pipeline):
            query_str += "  " + json.dumps(stage, indent=2).replace("\n", "\n  ")
            if i < len(pipeline) - 1:
                query_str += ",\n"
            else:
                query_str += "\n"
        query_str += "])"
        return query_str
    
    # Handle regular find
    query_str = f"db.{collection}.{operation}("
    
    if query:
        query_str += json.dumps(query, indent=2)
    
    if projection:
        query_str += ", " + json.dumps(projection, indent=2)
    
    query_str += ")"
    
    return query_str
