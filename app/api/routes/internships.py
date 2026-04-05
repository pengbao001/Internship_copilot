from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.deps import InternshipRepositoryDep, PaginationDep
from app.schemas.internship import InternshipCreate, InternshipRead, InternshipSummary

router = APIRouter(
    prefix="/internships",
    tags=["internships"],
)

@router.post("/", response_model=InternshipRead, status_code=status.HTTP_201_CREATED)
def create_internship(
        payload: InternshipCreate,
        repo: InternshipRepositoryDep
) -> Any:
    return repo.create(**payload.model_dump())

@router.get("/", response_model=list[InternshipSummary])
def list_internships(
        repo: InternshipRepositoryDep,
        pagination: PaginationDep,
) -> Any:
    return repo.list(
        limit=pagination.limit,
        offset=pagination.offset,
    )

@router.get("/{internship_id}", response_model=InternshipRead)
def get_internship(
        internship_id: int,
        repo: InternshipRepositoryDep,
) -> Any:
    internship = repo.get_by_id(internship_id)
    if internship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found",
        )
    return internship