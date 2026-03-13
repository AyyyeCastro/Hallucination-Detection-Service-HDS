from pydantic import BaseModel, Field
from typing import List, Optional


class AnalyzeRequest(BaseModel):
    text: str


class ClaimResult(BaseModel):
    claim: str
    context_based_claim: str
    search_query: Optional[str] = None
    score: float
    semantic_score: float
    verification: str
    evidence: List[str] = Field(default_factory=list)
    page_title: Optional[str] = None
    matched_numbers: List[str] = Field(default_factory=list)
    mismatched_numbers: List[str] = Field(default_factory=list)

class SummaryResult(BaseModel):
    claims_analyzed: int
    overall_score: float
    overall_verification: str


class AnalyzeResponse(BaseModel):
    claims: List[ClaimResult]
    summary: SummaryResult