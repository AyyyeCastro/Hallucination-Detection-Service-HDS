from fastapi import APIRouter
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_helper import analyze_document

router = APIRouter()


@router.post("/", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeRequest):
    return analyze_document(request.text)