from pydantic import BaseModel
from typing import List

class AnalyzeRequest(BaseModel):
    text: str

class ClaimResult(BaseModel):
    claim: str
    score: float
    verification: str
    evidence: List[str]

class AnalyzeResponse(BaseModel):
    claims: List[ClaimResult]
    hallucination_score: float