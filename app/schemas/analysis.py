from pydantic import BaseModel, Field

class MatchResult(BaseModel):
    internship_id: int
    internship_title: str
    company_name: str
    fit_score: float
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)

class MatchResultsResponse(BaseModel):
    """
    To do
    """
    results: list[MatchResult] = Field(default_factory=list)