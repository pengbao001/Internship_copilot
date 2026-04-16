from dataclasses import dataclass

from app.core.exceptions import (
    IngestionError,
    SourceFetchError,
    SourceParseError,
    UnsupportedSourceError,
)

from app.extraction.skill_extractor import (
    SkillExtractionError,
    SkillExtractor,
)

from app.ingestion.page_loader import PageLoader, SourceKind
from app.ingestion.text_cleaner import TextCleaner
from app.models.internship import Internship
from app.repositories.internship_repository import InternshipRepository

class InternshipIngestionServiceError(ValueError):
    """Raised when internship ingestion cannot be completed."""

@dataclass(frozen=True)
class InternshipIngestionResult:
    internship: Internship
    source_kind: SourceKind
    source_title: str | None = None
    normalized_skills: tuple[str, ...] = ()
    raw_matched_phrases: tuple[str, ...] = ()

class InternshipIngestionService:

    def __init__(self, *,
                 repository: InternshipRepository,
                 page_loader: PageLoader | None = None,
                 text_cleaner: TextCleaner | None = None,
                 extractor: SkillExtractor | None = None):
        self.repository = repository
        self.page_loader = page_loader or PageLoader()
        self.text_cleaner = text_cleaner or TextCleaner()
        self.extractor = extractor or SkillExtractor()

    def _choose_title(self, *,
                      explicit_title : str | None,
                      extracted_title: str | None) -> str:
        if explicit_title and explicit_title.strip():
            return explicit_title.strip()
        if extracted_title and extracted_title.strip():
            return extracted_title.strip()
        return "Untitled internship."

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None

    def ingest(self, *,
               company_name: str,
               title : str | None = None,
               location : str | None = None,
               text : str | None = None,
               url : str | None = None,) -> InternshipIngestionResult:
        normalized_company_name = company_name.strip()
        if not normalized_company_name:
            raise InternshipIngestionServiceError("company_name must not be empty.")

        try:
            document = self.page_loader.load(text=text, url=url)
            cleaned_description = self.text_cleaner.clean(
                document.raw_text,
                source_kind=document.source_kind,
            )
            extraction = self.extractor.extract(cleaned_description)
        except (
            IngestionError,
            SourceFetchError,
            SourceParseError,
            UnsupportedSourceError,
            SkillExtractionError,
            ValueError,
        ) as exc:
            raise InternshipIngestionServiceError(str(exc)) from exc

        final_title = self._choose_title(
            explicit_title=title,
            extracted_title=document.title,
        )

        internship = self.repository.create(
            title=final_title,
            company_name=normalized_company_name,
            location=self._normalize_optional_text(location),
            source_url=document.final_url or self._normalize_optional_text(url),
            raw_description=document.raw_text,
            cleaned_description=cleaned_description,
            is_active=True,
        )

        return InternshipIngestionResult(
            internship=internship,
            source_kind=document.source_kind,
            source_title=document.title,
            normalized_skills=tuple(extraction.normalized_skills),
            raw_matched_phrases=tuple(extraction.raw_matched_phrases),
        )