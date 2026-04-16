from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.internship import Internship

class InternshipRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *,
               title: str,
               company_name: str,
               location: str | None = None,
               source_url: str | None = None,
               raw_description: str,
               cleaned_description: str,
               is_active: bool = True,
    ) -> Internship:
        internship = Internship(
            title=title,
            company_name=company_name,
            location=location,
            source_url=source_url,
            raw_description=raw_description,
            cleaned_description=cleaned_description,
            is_active=is_active,
        )

        try:
            self.session.add(internship)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

        self.session.refresh(internship)
        return internship

    def get_by_id(self, internship_id: int) -> Internship | None:
        intern = select(Internship).where(Internship.id == internship_id)
        return self.session.scalar(intern)

    def list(self, *,
             limit: int = 20,
             offset: int = 0,
             only_active: bool | None = None,
    ) -> list[Internship]:
        interns = select(Internship).order_by(Internship.created_at.desc())

        if only_active is not None:
            interns = interns.where(Internship.is_active == only_active)

        interns = interns.limit(limit).offset(offset)
        return list(self.session.scalars(interns).all())

    def list_all(self, *,
                 only_active: bool | None = None) -> list[Internship]:

        interns = select(Internship).order_by(Internship.created_at.desc())

        if only_active is not None:
            interns = interns.where(Internship.is_active == only_active)
        return list(self.session.scalars(interns).all())
