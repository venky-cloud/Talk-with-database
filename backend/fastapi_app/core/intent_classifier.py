"""
Intent Classification Module
Uses transformer models for classifying user intent from natural language queries.
"""
from __future__ import annotations
from typing import Dict, List, Optional
import re

# Intent types
INTENT_SELECT = "SELECT"
INTENT_INSERT = "INSERT"
INTENT_UPDATE = "UPDATE"
INTENT_DELETE = "DELETE"
INTENT_API_FETCH = "API_FETCH"
INTENT_MONGODB = "MONGODB"
INTENT_SCHEMA = "SCHEMA"
INTENT_UNKNOWN = "UNKNOWN"

# Keyword-based intent detection (lightweight fallback)
INTENT_KEYWORDS = {
    INTENT_SELECT: [
        r'\b(show|get|find|list|display|select|fetch|retrieve|view|search|query)\b',
        r'\b(what|which|how many|count)\b',
        r'\b(all|top|first|last)\b',
    ],
    INTENT_INSERT: [
        r'\b(add|insert|create|new|register)\b',
        r'\b(save|store|put)\b',
    ],
    INTENT_UPDATE: [
        r'\b(update|modify|change|edit|set|alter)\b',
        r'\b(rename|replace)\b',
    ],
    INTENT_DELETE: [
        r'\b(delete|remove|drop|clear|erase)\b',
    ],
    INTENT_API_FETCH: [
        r'\b(api|rest|endpoint|http|request)\b',
        r'\b(call|invoke|trigger)\b',
    ],
    INTENT_MONGODB: [
        r'\b(mongo|mongodb|document|collection|nosql)\b',
    ],
    INTENT_SCHEMA: [
        r'\b(schema|structure|tables|columns|relations|describe)\b',
        r'\b(show tables|show columns|describe table)\b',
    ],
}


def classify_intent_keyword(text: str) -> tuple[str, float]:
    """
    Classify intent using keyword matching (fast fallback).
    Returns (intent, confidence)
    """
    text_lower = text.lower()
    scores = {}
    
    for intent, patterns in INTENT_KEYWORDS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                score += 1
        scores[intent] = score
    
    # Get intent with highest score
    if max(scores.values()) == 0:
        return INTENT_UNKNOWN, 0.0
    
    best_intent = max(scores, key=scores.get)
    confidence = min(scores[best_intent] / 3.0, 1.0)  # Normalize
    
    return best_intent, confidence


# Advanced transformer-based classification (loaded lazily)
_intent_model = None


def load_intent_model():
    """Load intent classification model (RoBERTa-based)"""
    global _intent_model
    if _intent_model is not None:
        return _intent_model
    
    try:
        from transformers import pipeline
        # Use zero-shot classification with RoBERTa
        _intent_model = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",  # Good for intent classification
            device=-1  # CPU
        )
        return _intent_model
    except Exception as e:
        print(f"Warning: Could not load intent model: {e}")
        return None


def classify_intent_transformer(text: str) -> tuple[str, float]:
    """
    Classify intent using transformer model (RoBERTa/BART).
    Returns (intent, confidence)
    """
    model = load_intent_model()
    if model is None:
        return classify_intent_keyword(text)
    
    try:
        candidate_labels = [
            "retrieve data",  # SELECT
            "insert data",    # INSERT
            "update data",    # UPDATE
            "delete data",    # DELETE
            "api request",    # API
            "mongodb query",  # MONGODB
            "schema info",    # SCHEMA
        ]
        
        result = model(text, candidate_labels)
        top_label = result['labels'][0]
        confidence = result['scores'][0]
        
        # Map labels to intents
        label_to_intent = {
            "retrieve data": INTENT_SELECT,
            "insert data": INTENT_INSERT,
            "update data": INTENT_UPDATE,
            "delete data": INTENT_DELETE,
            "api request": INTENT_API_FETCH,
            "mongodb query": INTENT_MONGODB,
            "schema info": INTENT_SCHEMA,
        }
        
        intent = label_to_intent.get(top_label, INTENT_UNKNOWN)
        return intent, float(confidence)
    
    except Exception as e:
        print(f"Transformer classification failed: {e}")
        return classify_intent_keyword(text)


def classify_intent(text: str, use_transformer: bool = True) -> Dict[str, any]:
    """
    Main intent classification function.
    
    Args:
        text: User's natural language query
        use_transformer: Use transformer model if True, else keyword-based
    
    Returns:
        {
            "intent": str,
            "confidence": float,
            "method": str ("transformer" or "keyword")
        }
    """
    if use_transformer:
        intent, confidence = classify_intent_transformer(text)
        method = "transformer"
    else:
        intent, confidence = classify_intent_keyword(text)
        method = "keyword"
    
    return {
        "intent": intent,
        "confidence": confidence,
        "method": method,
    }


# Named Entity Recognition (NER) for SQL entities
def extract_sql_entities(text: str, schema: Optional[Dict] = None) -> Dict[str, List[str]]:
    """
    Extract SQL-related entities from text (tables, columns, conditions).
    Uses pattern matching and schema matching.
    """
    entities = {
        "tables": [],
        "columns": [],
        "values": [],
        "conditions": [],
    }
    
    text_lower = text.lower()
    
    # Extract from schema if provided
    if schema:
        tables = schema.get("tables", [])
        for table in tables:
            if table.lower() in text_lower:
                entities["tables"].append(table)
        
        columns_dict = schema.get("columns", {})
        for table, cols in columns_dict.items():
            if table in entities["tables"]:
                for col in cols:
                    col_name = col.get("name", "")
                    if col_name.lower() in text_lower:
                        entities["columns"].append(f"{table}.{col_name}")
    
    # Extract quoted strings as values
    import re
    quoted_values = re.findall(r"['\"]([^'\"]+)['\"]", text)
    entities["values"].extend(quoted_values)
    
    # Extract conditions (simple patterns)
    condition_patterns = [
        r'where\s+(\w+)',
        r'(\w+)\s*=\s*',
        r'(\w+)\s*>\s*',
        r'(\w+)\s*<\s*',
    ]
    for pattern in condition_patterns:
        matches = re.findall(pattern, text_lower)
        entities["conditions"].extend(matches)
    
    # Remove duplicates
    for key in entities:
        entities[key] = list(set(entities[key]))
    
    return entities
