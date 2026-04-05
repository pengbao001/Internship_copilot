from datetime import datetime

from pydantic import BaseModel, ConfigDict

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