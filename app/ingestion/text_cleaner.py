import html
import re
import unicodedata


class TextCleaner:
    """Normalize extracted text before skill extraction or storage."""

    _zero_width_pattern = re.compile(r"[\u200b\u200c\u200d\ufeff]")
    _multi_space_pattern = re.compile(r"[ \t\f\v]+")
    _multi_blank_line_pattern = re.compile(r"\n{3,}")
    _pdf_hyphen_break_pattern = re.compile(r"(\w)-\n(\w)")
    _bullet_pattern = re.compile(r"^\s*[•●▪◦‣∙]\s*", re.MULTILINE)

    def clean(self, text: str, *, source_kind: str = "pasted_text") -> str:
        if not text or not text.strip():
            raise ValueError("Cannot clean empty text.")

        cleaned = html.unescape(text)
        cleaned = unicodedata.normalize("NFKC", cleaned)
        cleaned = self._normalize_line_endings(cleaned)
        cleaned = cleaned.replace("\xa0", " ")
        cleaned = self._zero_width_pattern.sub("", cleaned)

        if source_kind == "pdf":
            cleaned = self._repair_pdf_hyphenation(cleaned)

        cleaned = self._normalize_bullets(cleaned)
        cleaned = self._normalize_lines(cleaned)
        cleaned = self._multi_blank_line_pattern.sub("\n\n", cleaned)

        return cleaned.strip()

    def _normalize_line_endings(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n")

    def _repair_pdf_hyphenation(self, text: str) -> str:
        return self._pdf_hyphen_break_pattern.sub(r"\1\2", text)

    def _normalize_bullets(self, text: str) -> str:
        return self._bullet_pattern.sub("- ", text)

    def _normalize_lines(self, text: str) -> str:
        normalized_lines: list[str] = []

        for raw_line in text.split("\n"):
            line = self._multi_space_pattern.sub(" ", raw_line).strip()
            normalized_lines.append(line)

        return "\n".join(normalized_lines)