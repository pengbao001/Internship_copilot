from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import ProfileRepositoryDep, PaginationDep
from app.schemas.profile import ProfileRead, ProfileSummary, ProfileCreate

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
)

@router.post("/", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
def create_profile(
        payload: ProfileCreate,
        repo: ProfileRepositoryDep
) -> Any:
    return repo.create(**payload.model_dump())

@router.get("/", response_model=list[ProfileSummary])
def list_profiles(
        repo: ProfileRepositoryDep,
        pagination: PaginationDep,
) -> Any:
    return repo.list(
        limit=pagination.limit,
        offset=pagination.offset,
    )

@router.get("/{profile_id}", response_model=ProfileRead)
def get_profile(
        profile_id: int,
        repo: ProfileRepositoryDep,
) -> Any:
    profile = repo.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile