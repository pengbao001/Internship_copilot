from pydantic import BaseModel, Field

from typing import Literal

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

class InternshipMatchRead(BaseModel):
    internship_id: int | None = None
    title: str
    company_name: str
    section_strategy: Literal["sectioned", "fallback_all_required"]
    fit_score: float
    required_match_ratio: float
    preferred_match_ratio: float
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    matched_required_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_required_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    raw_required_phrases: list[str] = Field(default_factory=list)
    raw_preferred_phrases: list[str] = Field(default_factory=list)


class ProfileMatchesResponse(BaseModel):
    profile_id: int
    profile_name: str
    profile_skills: list[str] = Field(default_factory=list)
    total_results: int
    results: list[InternshipMatchRead] = Field(default_factory=list)