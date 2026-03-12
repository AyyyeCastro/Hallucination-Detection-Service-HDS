from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analyze import router as analyze_router

app = FastAPI(
    title="HDS",
    description="API for analyzing LLM outputs for accuracy and hallucination",
    version="0.0.1"
)

origins=[
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router, prefix="/analyze", tags=["analysis"])

app.get("/")
def health_check():
    return{
        "Status...": "HDS API running."
    }
    
