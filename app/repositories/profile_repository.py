from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.profile import Profile

class ProfileRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *,
               full_name: str,
               email: str | None = None,
               github_url: str | None = None,
               linkedin_url: str | None = None,
               resume_text: str,
               summary : str | None = None
    ) -> Profile:

        profile = Profile(
            full_name=full_name,
            email=email,
            github_url=github_url,
            linkedin_url=linkedin_url,
            resume_text=resume_text,
            summary=summary,
        )

        try:
            self.session.add(profile)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise

        self.session.refresh(profile)
        return profile

    def get_by_id(self, profile_id: int) -> Profile | None:
        profile = select(Profile).where(Profile.id == profile_id)
        return self.session.scalar(profile)

    def list(self, *,
             limit : int = 20,
             offset : int = 0
    ) -> list[Profile]:

        profiles = (
            select(Profile)
            .order_by(Profile.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(self.session.scalars(profiles).all())