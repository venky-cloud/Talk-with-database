import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import nlu, schema, generate, validate, rank, execute, mongodb, history, api_routes
from .routers import sql_generate, mongo_generate
from .routers import chatbot

app = FastAPI(title="Talk-with-Database API", version="0.1.0")

# CORS - Allow all origins (development mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include all routers
app.include_router(nlu.router, prefix="/nlu", tags=["nlu"])
app.include_router(schema.router, prefix="/schema", tags=["schema"])
app.include_router(generate.router, prefix="/generate", tags=["generate"])
app.include_router(validate.router, prefix="/validate", tags=["validate"])
app.include_router(rank.router, prefix="/rank", tags=["rank"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])
app.include_router(mongodb.router, prefix="/mongodb", tags=["mongodb"])
app.include_router(history.router, prefix="/history", tags=["history"])
app.include_router(api_routes.router, prefix="/api", tags=["api"])
app.include_router(sql_generate.router, prefix="/generate", tags=["generate-multiple"])  # /generate/sql/generate-multiple
app.include_router(mongo_generate.router, prefix="/generate", tags=["generate-multiple"])  # /generate/mongodb/generate-multiple
app.include_router(chatbot.router, prefix="/ai", tags=["chatbot"])

@app.get("/")
def root():
    return {"message": "FastAPI service is running"}
