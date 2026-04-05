from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.internship_repository import InternshipRepository
from app.repositories.profile_repository import ProfileRepository

DbSession = Annotated[Session, Depends(get_db_session)]

@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int

def get_pagination(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)

PaginationDep = Annotated[Pagination, Depends(get_pagination)]

def get_internship_repository(session: DbSession) -> InternshipRepository:
    return InternshipRepository(session=session)

def get_profile_repository(session: DbSession) -> ProfileRepository:
    return ProfileRepository(session=session)

InternshipRepositoryDep = Annotated[
    InternshipRepository,
    Depends(get_internship_repository),
]

ProfileRepositoryDep = Annotated[
    ProfileRepository,
    Depends(get_profile_repository),
]