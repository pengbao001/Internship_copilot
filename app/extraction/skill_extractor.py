import re
from dataclasses import dataclass, field
from typing import Literal

from app.extraction.skill_catalog import DEFAULT_SKILL_CATALOG, SkillCatalog

PatternKind = Literal["literal", "regex"]


class SkillExtractionError(ValueError):
    """Raised when skill extraction cannot run."""


@dataclass(frozen=True)
class CompiledSkillPattern:
    canonical_name: str
    source_text: str
    pattern_kind: PatternKind
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class SkillMatch:
    canonical_name: str
    matched_text: str
    start: int
    end: int
    pattern_kind: PatternKind
    source_text: str


@dataclass
class SkillExtractionResult:
    normalized_skills: list[str] = field(default_factory=list)
    raw_matched_phrases: list[str] = field(default_factory=list)
    matches: list[SkillMatch] = field(default_factory=list)

    @property
    def phrases_by_skill(self) -> dict[str, list[str]]:
        grouped = {}

        for match in self.matches:
            phrases = grouped.setdefault(match.canonical_name, [])
            if match.matched_text not in phrases:
                phrases.append(match.matched_text)

        return grouped


class SkillExtractor:
    """Deterministic skill extractor based on a controlled skill catalog."""

    def __init__(self, catalog: SkillCatalog = DEFAULT_SKILL_CATALOG):
        self.catalog = catalog
        self._compiled_patterns = self._compile_catalog()

    def extract(self, text: str) -> SkillExtractionResult:
        if not text or not text.strip():
            raise SkillExtractionError("Cannot extract skills from empty text.")

        collected_matches = self._collect_matches(text)
        matches = self._deduplicate_matches(collected_matches)

        return SkillExtractionResult(
            normalized_skills=self._build_normalized_skills(matches),
            raw_matched_phrases=self._build_raw_matched_phrases(matches),
            matches=matches,
        )

    def _compile_catalog(self) -> list[CompiledSkillPattern]:
        compiled_patterns = []

        try:
            for skill in self.catalog:
                for alias in skill.all_literal_aliases:
                    compiled_patterns.append(
                        CompiledSkillPattern(
                            canonical_name=skill.canonical_name,
                            source_text=alias,
                            pattern_kind="literal",
                            pattern=self._compile_literal_alias(alias),
                        )
                    )

                for regex_pattern in skill.regex_patterns:
                    compiled_patterns.append(
                        CompiledSkillPattern(
                            canonical_name=skill.canonical_name,
                            source_text=regex_pattern,
                            pattern_kind="regex",
                            pattern=re.compile(regex_pattern, re.IGNORECASE),
                        )
                    )
        except re.error as exc:
            raise SkillExtractionError(
                "Skill catalog contains an invalid regex pattern."
            ) from exc

        return compiled_patterns

    def _compile_literal_alias(self, alias: str) -> re.Pattern[str]:
        escaped_alias = re.escape(alias)
        pattern_text = rf"(?<!\w){escaped_alias}(?!\w)"
        return re.compile(pattern_text, re.IGNORECASE)

    def _collect_matches(self, text: str) -> list[SkillMatch]:
        matches = []

        for compiled_pattern in self._compiled_patterns:
            for found_match in compiled_pattern.pattern.finditer(text):
                matched_text = found_match.group(0).strip()
                if not matched_text:
                    continue

                matches.append(
                    SkillMatch(
                        canonical_name=compiled_pattern.canonical_name,
                        matched_text=matched_text,
                        start=found_match.start(),
                        end=found_match.end(),
                        pattern_kind=compiled_pattern.pattern_kind,
                        source_text=compiled_pattern.source_text,
                    )
                )

        return matches

    def _deduplicate_matches(self, matches: list[SkillMatch]) -> list[SkillMatch]:
        ordered_matches = sorted(
            matches,
            key=lambda match: (
                match.start,
                -(match.end - match.start),
                match.canonical_name.casefold(),
            ),
        )

        unique_matches = []
        seen_keys = set()

        for match in ordered_matches:
            key = (match.canonical_name.casefold(), match.start, match.end)
            if key in seen_keys:
                continue

            seen_keys.add(key)
            unique_matches.append(match)

        return unique_matches

    def _build_normalized_skills(self, matches: list[SkillMatch]) -> list[str]:
        normalized_skills = []
        seen_skills = set()

        for match in matches:
            key = match.canonical_name.casefold()
            if key in seen_skills:
                continue

            seen_skills.add(key)
            normalized_skills.append(match.canonical_name)

        return normalized_skills

    def _build_raw_matched_phrases(self, matches: list[SkillMatch]) -> list[str]:
        raw_phrases = []
        seen_phrases = set()

        for match in matches:
            phrase = match.matched_text
            if phrase in seen_phrases:
                continue

            seen_phrases.add(phrase)
            raw_phrases.append(phrase)

        return raw_phrases