from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    database: Optional[str] = "mongodb"
    count: int = 5
    schema: Optional[Dict[str, Any]] = None

class MongoVariant(BaseModel):
    title: str
    mongo: Union[List[Dict[str, Any]], Dict[str, Any], str]
    notes: Optional[str] = None

class GenerateResponse(BaseModel):
    variants: List[MongoVariant]

@router.post("/mongodb/generate-multiple", response_model=GenerateResponse)
async def generate_mongo_variants(payload: GenerateRequest) -> GenerateResponse:
    prompt = payload.prompt.strip().lower()
    n = max(1, min(payload.count, 10))

    # basic heuristic
    coll = "orders" if "order" in prompt else "customers"

    pipelines: List[MongoVariant] = []
    templates: List[MongoVariant] = [
        MongoVariant(
            title="Find recent",
            mongo={"collection": coll, "query": {"created_at": {"$gte": {"$date": "2025-11-01T00:00:00Z"}}}, "projection": {}, "limit": 100},
            notes="Simple find with recent date filter"
        ),
        MongoVariant(
            title="Top by amount",
            mongo=[
                {"$match": {"amount": {"$gt": 0}}},
                {"$group": {"_id": "$customer_id", "total": {"$sum": "$amount"}}},
                {"$sort": {"total": -1}},
                {"$limit": 10}
            ],
            notes="Aggregate by customer"
        ),
        MongoVariant(
            title="Lookup customers",
            mongo=[
                {"$match": {"created_at": {"$gte": {"$date": "2025-11-01T00:00:00Z"}}}},
                {"$group": {"_id": "$customer_id", "total_amount": {"$sum": "$amount"}}},
                {"$lookup": {"from": "customers", "localField": "_id", "foreignField": "id", "as": "customer"}},
                {"$unwind": {"path": "$customer", "preserveNullAndEmptyArrays": True}},
                {"$project": {"customer_id": "$_id", "name": "$customer.name", "total_amount": 1, "_id": 0}},
                {"$sort": {"total_amount": -1}},
                {"$limit": 5}
            ],
            notes="Join-like lookup"
        ),
        MongoVariant(
            title="Parameterized window",
            mongo="db.%s.aggregate([{ $setWindowFields: { partitionBy: '$customer_id', sortBy: { created_at: 1 }, output: { rn: { $documentNumber: {} } } } }])" % coll,
            notes="Requires MongoDB version with $setWindowFields"
        ),
        MongoVariant(
            title="Projection example",
            mongo={"collection": coll, "query": {}, "projection": {"_id": 0, "customer_id": 1, "amount": 1, "created_at": 1}, "limit": 100},
            notes="Field projection"
        ),
    ]

    for v in templates[:n]:
        pipelines.append(v)

    return GenerateResponse(variants=pipelines)
