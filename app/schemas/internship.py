from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from typing import Literal

class ExtractedSkillsPreview(BaseModel):
    normalized_skills : list[str]
    raw_matched_phrases : list[str]

class InternshipIngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_name : str
    title : str | None = None
    location : str | None = None
    text : str | None = None
    url : str | None = None

    @model_validator(mode="after")
    def validate_source(self) -> "InternshipIngestRequest":
        has_text = bool(self.text and self.text.strip())
        has_url = bool(self.url and self.url.strip())

        if has_text == has_url:
            raise ValueError("Please provide one of 'text' or 'url'.")
        return self


class InternshipCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    company_name: str
    location: str
    source_url: str | None
    raw_description: str
    cleaned_description: str | None = None
    is_active: bool = True

class InternshipSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str
    location: str | None = None
    source_url: str | None = None
    is_active: bool
    created_at: datetime

class InternshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company_name: str
    location: str | None = None
    source_url: str | None = None
    raw_description: str
    cleaned_description: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class InternshipIngestResponse(BaseModel):
    internship : InternshipRead
    source_kind : Literal["pasted_text", "html", "pdf"]
    source_text : str | None = None
    extracted_skills : ExtractedSkillsPreview