from dataclasses import dataclass

from app.extraction.skill_extractor import SkillExtractionError, SkillExtractor
from app.models.profile import Profile


class ProfileServiceError(ValueError):
    """Raised when a profile cannot be converted into a skill profile."""


@dataclass(frozen=True)
class ProfileSkillProfile:
    profile_id: int | None
    normalized_skills: tuple[str, ...] = ()
    raw_matched_phrases: tuple[str, ...] = ()
    source_text: str = ""

    @property
    def skill_lookup(self) -> frozenset[str]:
        return frozenset(skill.casefold() for skill in self.normalized_skills)


class ProfileService:
    """Build a reusable skill profile from resume text."""

    def __init__(self, extractor: SkillExtractor | None = None):
        self.extractor = extractor or SkillExtractor()

    def build_skill_profile(self, profile: Profile) -> ProfileSkillProfile:
        return self.build_skill_profile_from_text(
            resume_text=profile.resume_text,
            summary=profile.summary,
            profile_id=profile.id,
        )

    def build_skill_profile_from_text(
        self, *,
        resume_text: str,
        summary: str | None = None,
        profile_id: int | None = None,
    ) -> ProfileSkillProfile:
        source_text = self._build_source_text(
            resume_text=resume_text,
            summary=summary,
        )

        if not source_text:
            raise ProfileServiceError("Profile text is empty.")

        try:
            extraction = self.extractor.extract(source_text)
        except SkillExtractionError as exc:
            raise ProfileServiceError(
                "Failed to extract skills from profile text."
            ) from exc

        return ProfileSkillProfile(
            profile_id=profile_id,
            normalized_skills=tuple(extraction.normalized_skills),
            raw_matched_phrases=tuple(extraction.raw_matched_phrases),
            source_text=source_text,
        )

    def _build_source_text(
        self, *,
        resume_text: str,
        summary: str | None = None,
    ) -> str:
        parts: list[str] = []

        if resume_text and resume_text.strip():
            parts.append(resume_text.strip())

        if summary and summary.strip():
            parts.append(summary.strip())

        return "\n\n".join(parts)