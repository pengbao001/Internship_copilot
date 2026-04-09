from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Final


class SkillCatalogError(ValueError):
    """Raised when the skill catalog configuration is invalid."""


@dataclass(frozen=True)
class SkillDefinition:
    canonical_name: str
    literal_aliases: tuple[str, ...] = field(default_factory=tuple)
    regex_patterns: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not self.canonical_name.strip():
            raise SkillCatalogError("canonical_name must not be empty.")

    @property
    def all_literal_aliases(self) -> tuple[str, ...]:
        ordered = {}

        for alias in (self.canonical_name, *self.literal_aliases):
            cleaned_alias = alias.strip()
            if not cleaned_alias:
                continue

            ordered.setdefault(cleaned_alias.casefold(), cleaned_alias)

        return tuple(ordered.values())


@dataclass(frozen=True)
class SkillCatalog:
    skills: tuple[SkillDefinition, ...]

    def __post_init__(self):
        if not self.skills:
            raise SkillCatalogError("Skill catalog must contain at least one skill.")

        canonical_names = [skill.canonical_name.casefold() for skill in self.skills]
        if len(canonical_names) != len(set(canonical_names)):
            raise SkillCatalogError("Duplicate canonical skill names are not allowed.")

        alias_owner = {}
        for skill in self.skills:
            for alias in skill.all_literal_aliases:
                alias_key = alias.casefold()
                previous_owner = alias_owner.get(alias_key)

                if previous_owner is not None and previous_owner != skill.canonical_name:
                    raise SkillCatalogError(
                        f"Alias collision: {alias!r} is assigned to both "
                        f"{previous_owner!r} and {skill.canonical_name!r}."
                    )

                alias_owner[alias_key] = skill.canonical_name

    def __iter__(self) -> Iterator[SkillDefinition]:
        return iter(self.skills)


DEFAULT_SKILL_CATALOG: Final[SkillCatalog] = SkillCatalog(
    skills=(
        SkillDefinition("Python", literal_aliases=("python3",)),
        SkillDefinition("SQL"),
        SkillDefinition("Git"),
        SkillDefinition("Linux"),
        SkillDefinition("Docker"),
        SkillDefinition("FastAPI"),
        SkillDefinition("NumPy"),
        SkillDefinition("Pandas"),
        SkillDefinition(
            "Scikit-learn",
            literal_aliases=("sklearn", "scikit learn"),
        ),
        SkillDefinition("PyTorch"),
        SkillDefinition("TensorFlow"),
        SkillDefinition(
            "NLP",
            literal_aliases=("natural language processing",),
        ),
        SkillDefinition(
            "Machine Learning",
            regex_patterns=(
                r"(?<!\w)machine(?:[\s-]+)learning(?!\w)",
            ),
        ),
        SkillDefinition(
            "Deep Learning",
            regex_patterns=(
                r"(?<!\w)deep(?:[\s-]+)learning(?!\w)",
            ),
        ),
        SkillDefinition(
            "Computer Vision",
            regex_patterns=(
                r"(?<!\w)computer(?:[\s-]+)vision(?!\w)",
            ),
        ),
        SkillDefinition(
            "LLMs",
            literal_aliases=("llm", "llms"),
            regex_patterns=(
                r"(?<!\w)large(?:[\s-]+)language(?:[\s-]+)models?(?!\w)",
            ),
        ),
        SkillDefinition(
            "Transformers",
            literal_aliases=(
                "transformer",
                "transformers",
                "transformer architecture",
                "transformer architectures",
            ),
        ),
        SkillDefinition(
            "RAG",
            literal_aliases=("rag",),
            regex_patterns=(
                r"(?<!\w)retrieval(?:[\s-]+)augmented(?:[\s-]+)generation(?!\w)",
            ),
        ),
        SkillDefinition(
            "Prompt Engineering",
            literal_aliases=("prompt design",),
            regex_patterns=(
                r"(?<!\w)prompt(?:[\s-]+)engineering(?!\w)",
            ),
        ),
        SkillDefinition(
            "Hugging Face",
            literal_aliases=("huggingface",),
        ),
        SkillDefinition(
            "LangChain",
            literal_aliases=("lang chain",),
        ),
        SkillDefinition(
            "AWS",
            literal_aliases=("amazon web services",),
        ),
        SkillDefinition(
            "PostgreSQL",
            literal_aliases=("postgres",),
        ),
    )
)