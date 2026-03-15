from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analyze import router as analyze_router
import os

app = FastAPI(
    title="HDS",
    description="API for analyzing LLM outputs for accuracy and hallucination",
    version="2.6"
)

origins = [
    "http://localhost:3000",
    "https://hds.andrewcastro.dev",
    "https://andrewcastro.dev"
]

extra_origin = os.getenv("FRONTEND_ORIGIN")
if extra_origin and extra_origin not in origins:
    origins.append(extra_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/analyze", tags=["analysis"])

@app.get("/")
def health_check():
    return {"status": "HDS API running."}