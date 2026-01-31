from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..core.intent_classifier import classify_intent, extract_sql_entities

router = APIRouter()

class NLURequest(BaseModel):
    text: str
    db_schema: Optional[Dict[str, Any]] = None
    use_transformer: bool = True

class NLUResponse(BaseModel):
    intent: str
    confidence: float
    method: str
    entities: Dict[str, List[str]]
    dependencies: List[Dict[str, Any]]

# spaCy for dependency parsing (loaded lazily)
_spacy_nlp = None

def load_spacy():
    """Load spaCy model for dependency parsing"""
    global _spacy_nlp
    if _spacy_nlp is not None:
        return _spacy_nlp
    
    try:
        import spacy
        _spacy_nlp = spacy.load("en_core_web_sm")
        return _spacy_nlp
    except Exception as e:
        print(f"Warning: Could not load spaCy: {e}")
        try:
            # Try to download if not installed
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            return _spacy_nlp
        except:
            return None

def extract_dependencies(text: str) -> List[Dict[str, Any]]:
    """Extract syntactic dependencies using spaCy"""
    nlp = load_spacy()
    if nlp is None:
        # Fallback to rule-based
        dependencies: List[Dict[str, Any]] = []
        keywords = ["from", "into", "where", "join", "on", "group by", "order by", "having", "limit"]
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                dependencies.append({"type": "clause", "keyword": keyword})
        return dependencies
    
    try:
        doc = nlp(text)
        dependencies = []
        
        for token in doc:
            if token.dep_ in ["ROOT", "nsubj", "dobj", "pobj", "prep", "compound"]:
                dependencies.append({
                    "text": token.text,
                    "lemma": token.lemma_,
                    "pos": token.pos_,
                    "dep": token.dep_,
                    "head": token.head.text,
                })
        
        return dependencies
    except Exception as e:
        print(f"Dependency parsing failed: {e}")
        return []

@router.post("/parse", response_model=NLUResponse)
def parse(req: NLURequest):
    """
    Advanced NLU parsing with intent classification, NER, and dependency parsing.
    """
    # 1. Intent Classification
    intent_result = classify_intent(req.text, use_transformer=req.use_transformer)
    
    # 2. Named Entity Recognition (SQL entities)
    entities = extract_sql_entities(req.text, req.db_schema)
    
    # 3. Dependency Parsing
    dependencies = extract_dependencies(req.text)
    
    return NLUResponse(
        intent=intent_result["intent"],
        confidence=intent_result["confidence"],
        method=intent_result["method"],
        entities=entities,
        dependencies=dependencies
    )
