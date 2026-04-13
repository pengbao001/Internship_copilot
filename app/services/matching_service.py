import re
from dataclasses import dataclass
from typing import Literal, Sequence

from app.extraction.skill_extractor import (
    SkillExtractionError,
    SkillExtractionResult,
    SkillExtractor,
)
from app.models.internship import Internship
from app.models.profile import Profile
from app.services.profile_service import ProfileService, ProfileSkillProfile

SectionStrategy = Literal["sectioned", "fallback_all_required"]


class MatchingServiceError(ValueError):
    """Raised when an internship cannot be parsed or matched."""


@dataclass(frozen=True)
class SectionBuckets:
    required_text: str = ""
    preferred_text: str = ""
    unclassified_text: str = ""
    used_section_rules: bool = False


@dataclass(frozen=True)
class InternshipSkillProfile:
    internship_id: int | None
    title: str
    company_name: str
    required_skills: tuple[str, ...] = ()
    preferred_skills: tuple[str, ...] = ()
    raw_required_phrases: tuple[str, ...] = ()
    raw_preferred_phrases: tuple[str, ...] = ()
    section_strategy: SectionStrategy = "fallback_all_required"


@dataclass(frozen=True)
class InternshipMatchResult:
    internship_id: int | None
    title: str
    company_name: str
    section_strategy: SectionStrategy
    fit_score: float
    required_match_ratio: float
    preferred_match_ratio: float
    required_skills: tuple[str, ...] = ()
    preferred_skills: tuple[str, ...] = ()
    raw_required_phrases: tuple[str, ...] = ()
    raw_preferred_phrases: tuple[str, ...] = ()
    matched_required_skills: tuple[str, ...] = ()
    matched_preferred_skills: tuple[str, ...] = ()
    missing_required_skills: tuple[str, ...] = ()
    missing_preferred_skills: tuple[str, ...] = ()
    missing_skills: tuple[str, ...] = ()


class MatchingService:
    """Compare a profile against internships with an explainable scoring formula."""

    _REQUIRED_HEADING_PATTERNS = (
        re.compile(
            r"^\s*(requirements?|required qualifications?|minimum qualifications?|"
            r"basic qualifications?|must[- ]have(?: skills?)?)\s*:?\s*$",
            re.IGNORECASE,
        ),
    )

    _PREFERRED_HEADING_PATTERNS = (
        re.compile(
            r"^\s*(preferred qualifications?|nice[- ]to[- ]have|"
            r"bonus(?: points?)?|pluses?)\s*:?\s*$",
            re.IGNORECASE,
        ),
    )

    _NEUTRAL_HEADING_PATTERNS = (
        re.compile(
            r"^\s*(responsibilities?|what you(?:'|’)ll do|about (?:the )?role|"
            r"about us|benefits?|perks|compensation|salary|how to apply|"
            r"application process)\s*:?\s*$",
            re.IGNORECASE,
        ),
    )

    _REQUIRED_INLINE_PATTERNS = (
        re.compile(
            r"\b(required|must have|minimum qualifications?|basic qualifications?)\b",
            re.IGNORECASE,
        ),
    )

    _PREFERRED_INLINE_PATTERNS = (
        re.compile(
            r"\b(preferred|nice[- ]to[- ]have|bonus(?: points?)?|plus)\b",
            re.IGNORECASE,
        ),
    )

    def __init__(
        self,
        extractor: SkillExtractor | None = None,
        profile_service: ProfileService | None = None,
    ):
        shared_extractor = extractor or SkillExtractor()
        self.extractor = shared_extractor
        self.profile_service = profile_service or ProfileService(
            extractor=shared_extractor
        )

    def rank_internships(
        self, *,
        profile: Profile,
        internships: Sequence[Internship],
    ) -> list[InternshipMatchResult]:
        profile_skill_profile = self.profile_service.build_skill_profile(profile)
        return self.rank_internships_for_skill_profile(
            profile_skill_profile=profile_skill_profile,
            internships=internships,
        )

    def rank_internships_for_skill_profile(
        self, *,
        profile_skill_profile: ProfileSkillProfile,
        internships: Sequence[Internship],
    ) -> list[InternshipMatchResult]:
        results = [
            self.match_profile_to_internship(
                profile_skill_profile=profile_skill_profile,
                internship=internship,
            )
            for internship in internships
        ]

        return sorted(
            results,
            key=lambda result: (
                -result.fit_score,
                -len(result.matched_required_skills),
                -len(result.matched_preferred_skills),
                result.company_name.casefold(),
                result.title.casefold(),
            ),
        )

    def match_profile_to_internship(
        self, *,
        profile_skill_profile: ProfileSkillProfile,
        internship: Internship,
    ) -> InternshipMatchResult:
        internship_skill_profile = self.build_internship_skill_profile(internship)
        profile_lookup = profile_skill_profile.skill_lookup

        matched_required_skills = tuple(
            skill
            for skill in internship_skill_profile.required_skills
            if skill.casefold() in profile_lookup
        )
        missing_required_skills = tuple(
            skill
            for skill in internship_skill_profile.required_skills
            if skill.casefold() not in profile_lookup
        )

        matched_preferred_skills = tuple(
            skill
            for skill in internship_skill_profile.preferred_skills
            if skill.casefold() in profile_lookup
        )
        missing_preferred_skills = tuple(
            skill
            for skill in internship_skill_profile.preferred_skills
            if skill.casefold() not in profile_lookup
        )

        required_match_ratio = self._coverage_ratio(
            matched_count=len(matched_required_skills),
            total_count=len(internship_skill_profile.required_skills),
        )
        preferred_match_ratio = self._coverage_ratio(
            matched_count=len(matched_preferred_skills),
            total_count=len(internship_skill_profile.preferred_skills),
        )

        fit_score = self._calculate_fit_score(
            required_match_ratio=required_match_ratio,
            preferred_match_ratio=preferred_match_ratio,
            has_required=bool(internship_skill_profile.required_skills),
            has_preferred=bool(internship_skill_profile.preferred_skills),
        )

        missing_skills = self._merge_skill_sequences(
            missing_required_skills,
            missing_preferred_skills,
        )

        return InternshipMatchResult(
            internship_id=internship_skill_profile.internship_id,
            title=internship_skill_profile.title,
            company_name=internship_skill_profile.company_name,
            section_strategy=internship_skill_profile.section_strategy,
            fit_score=fit_score,
            required_match_ratio=required_match_ratio,
            preferred_match_ratio=preferred_match_ratio,
            required_skills=internship_skill_profile.required_skills,
            preferred_skills=internship_skill_profile.preferred_skills,
            raw_required_phrases=internship_skill_profile.raw_required_phrases,
            raw_preferred_phrases=internship_skill_profile.raw_preferred_phrases,
            matched_required_skills=matched_required_skills,
            matched_preferred_skills=matched_preferred_skills,
            missing_required_skills=missing_required_skills,
            missing_preferred_skills=missing_preferred_skills,
            missing_skills=missing_skills,
        )

    def build_internship_skill_profile(
        self,
        internship: Internship,
    ) -> InternshipSkillProfile:
        source_text = self._build_internship_source_text(internship)
        sections = self._split_into_sections(source_text)

        if sections.used_section_rules:
            required_result = self._extract_or_empty(sections.required_text)
            preferred_result = self._extract_or_empty(sections.preferred_text)
            unclassified_result = self._extract_or_empty(sections.unclassified_text)

            required_skills = self._merge_skill_sequences(
                required_result.normalized_skills,
                unclassified_result.normalized_skills,
            )

            required_phrase_map = self._merge_phrase_maps(
                required_result,
                unclassified_result,
            )

            required_lookup = {skill.casefold() for skill in required_skills}
            preferred_skills = tuple(
                skill
                for skill in preferred_result.normalized_skills
                if skill.casefold() not in required_lookup
            )

            required_phrases = self._flatten_phrases_for_skills(
                skills=required_skills,
                phrase_map=required_phrase_map,
            )
            preferred_phrases = self._flatten_phrases_for_skills(
                skills=preferred_skills,
                phrase_map=self._merge_phrase_maps(preferred_result),
            )

            if required_skills or preferred_skills:
                return InternshipSkillProfile(
                    internship_id=internship.id,
                    title=internship.title,
                    company_name=internship.company_name,
                    required_skills=required_skills,
                    preferred_skills=preferred_skills,
                    raw_required_phrases=required_phrases,
                    raw_preferred_phrases=preferred_phrases,
                    section_strategy="sectioned",
                )

        full_result = self._extract_or_empty(source_text)

        return InternshipSkillProfile(
            internship_id=internship.id,
            title=internship.title,
            company_name=internship.company_name,
            required_skills=tuple(full_result.normalized_skills),
            preferred_skills=(),
            raw_required_phrases=tuple(full_result.raw_matched_phrases),
            raw_preferred_phrases=(),
            section_strategy="fallback_all_required",
        )

    def _build_internship_source_text(self, internship: Internship) -> str:
        if internship.cleaned_description and internship.cleaned_description.strip():
            return internship.cleaned_description.strip()

        if internship.raw_description and internship.raw_description.strip():
            return internship.raw_description.strip()

        raise MatchingServiceError("Internship description is empty.")

    def _split_into_sections(self, text: str) -> SectionBuckets:
        required_lines: list[str] = []
        preferred_lines: list[str] = []
        unclassified_lines: list[str] = []

        current_section: Literal["required", "preferred"] | None = None
        used_section_rules = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            heading_section = self._classify_heading(line)
            if heading_section is not None:
                current_section = heading_section
                used_section_rules = True
                continue

            if self._is_neutral_heading(line):
                current_section = None
                continue

            inline_section = self._classify_inline_line(line)
            if inline_section is not None:
                used_section_rules = True
                if inline_section == "required":
                    required_lines.append(line)
                else:
                    preferred_lines.append(line)
                continue

            if current_section == "required":
                required_lines.append(line)
                used_section_rules = True
            elif current_section == "preferred":
                preferred_lines.append(line)
                used_section_rules = True
            else:
                unclassified_lines.append(line)

        return SectionBuckets(
            required_text="\n".join(required_lines),
            preferred_text="\n".join(preferred_lines),
            unclassified_text="\n".join(unclassified_lines),
            used_section_rules=used_section_rules,
        )

    def _classify_heading(self, line: str) -> Literal["required", "preferred"] | None:
        for pattern in self._REQUIRED_HEADING_PATTERNS:
            if pattern.fullmatch(line):
                return "required"

        for pattern in self._PREFERRED_HEADING_PATTERNS:
            if pattern.fullmatch(line):
                return "preferred"

        return None

    def _is_neutral_heading(self, line: str) -> bool:
        return any(pattern.fullmatch(line) for pattern in self._NEUTRAL_HEADING_PATTERNS)

    def _classify_inline_line(self, line: str) -> Literal["required", "preferred"] | None:
        if any(pattern.search(line) for pattern in self._PREFERRED_INLINE_PATTERNS):
            return "preferred"

        if any(pattern.search(line) for pattern in self._REQUIRED_INLINE_PATTERNS):
            return "required"

        return None

    def _extract_or_empty(self, text: str) -> SkillExtractionResult:
        if not text or not text.strip():
            return SkillExtractionResult()

        try:
            return self.extractor.extract(text)
        except SkillExtractionError as exc:
            raise MatchingServiceError(
                "Failed to extract skills from internship text."
            ) from exc

    def _merge_skill_sequences(self, *groups: Sequence[str]) -> tuple[str, ...]:
        ordered_skills: list[str] = []
        seen_skills: set[str] = set()

        for group in groups:
            for skill in group:
                skill_key = skill.casefold()
                if skill_key in seen_skills:
                    continue

                seen_skills.add(skill_key)
                ordered_skills.append(skill)

        return tuple(ordered_skills)

    def _merge_phrase_maps(
        self,
        *results: SkillExtractionResult,
    ) -> dict[str, list[str]]:
        phrase_map: dict[str, list[str]] = {}

        for result in results:
            for skill, phrases in result.phrases_by_skill.items():
                target_phrases = phrase_map.setdefault(skill, [])
                for phrase in phrases:
                    if phrase not in target_phrases:
                        target_phrases.append(phrase)

        return phrase_map

    def _flatten_phrases_for_skills(
        self, *,
        skills: Sequence[str],
        phrase_map: dict[str, list[str]],
    ) -> tuple[str, ...]:
        ordered_phrases: list[str] = []

        for skill in skills:
            for phrase in phrase_map.get(skill, []):
                if phrase not in ordered_phrases:
                    ordered_phrases.append(phrase)

        return tuple(ordered_phrases)

    def _coverage_ratio(self, *, matched_count: int, total_count: int) -> float:
        if total_count == 0:
            return 0.0

        return round(matched_count / total_count, 3)

    def _calculate_fit_score(
        self, *,
        required_match_ratio: float,
        preferred_match_ratio: float,
        has_required: bool,
        has_preferred: bool,
    ) -> float:
        weight_total = 0.0
        weighted_score = 0.0

        if has_required:
            weighted_score += required_match_ratio * 0.7
            weight_total += 0.7

        if has_preferred:
            weighted_score += preferred_match_ratio * 0.3
            weight_total += 0.3

        if weight_total == 0.0:
            return 0.0

        return round((weighted_score / weight_total) * 100, 1)