from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ProfileCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str
    email: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    resume_text: str
    summary: str | None = None

class ProfileSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    created_at: datetime

class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str | None = None
    github_url: str | None = None
    linkedin_url: str | None = None
    summary: str | None = None
    created_at: datetime
    updated_at: datetime
