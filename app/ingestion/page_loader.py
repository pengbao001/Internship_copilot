from dataclasses import dataclass
from io import BytesIO
from typing import Literal
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.core.exceptions import (
    IngestionError,
    SourceFetchError,
    SourceParseError,
    UnsupportedSourceError,
)

SourceKind = Literal["pasted_text", "html", "pdf"]


@dataclass(slots=True)
class LoadedDocument:
    source_kind: SourceKind
    source: str
    raw_text: str
    title: str | None = None
    final_url: str | None = None
    content_type: str | None = None


class PageLoader:
    """Load internship description text from pasted text or a remote URL."""

    def __init__(
        self, *,
        timeout: float = 15.0,
        user_agent: str = "AI-Internship-Copilot/0.1",
    ):
        self.timeout = timeout
        self.user_agent = user_agent

    def load(
        self, *,
        text: str | None = None,
        url: str | None = None,
    ) -> LoadedDocument:
        has_text = text is not None and bool(text.strip())
        has_url = url is not None and bool(url.strip())

        if has_text == has_url:
            raise IngestionError("Provide exactly one of 'text' or 'url'.")

        if has_text:
            return self.load_from_text(text=text)  # type: ignore[arg-type]

        return self.load_from_url(url=url)  # type: ignore[arg-type]

    def load_from_text(
        self, *,
        text: str,
        title: str | None = None,
    ) -> LoadedDocument:
        if not text or not text.strip():
            raise IngestionError("Pasted text is empty.")

        return LoadedDocument(
            source_kind="pasted_text",
            source="pasted_text",
            raw_text=text,
            title=title,
        )

    def load_from_url(self, *, url: str) -> LoadedDocument:
        normalized_url = self._normalize_url(url)

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/pdf;q=0.9,*/*;q=0.8",
        }

        try:
            with httpx.Client(
                headers=headers,
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = client.get(normalized_url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceFetchError(f"Failed to fetch URL: {normalized_url}") from exc

        content_type = self._extract_content_type(response)

        if self._is_pdf_response(response=response, content_type=content_type):
            return self._load_pdf_response(
                response=response,
                requested_url=normalized_url,
                content_type=content_type,
            )

        return self._load_html_response(
            response=response,
            requested_url=normalized_url,
            content_type=content_type,
        )

    def _normalize_url(self, url: str) -> str:
        candidate = url.strip()
        if not candidate:
            raise IngestionError("URL is empty.")

        parsed = urlparse(candidate)

        if not parsed.scheme:
            candidate = f"https://{candidate}"
            parsed = urlparse(candidate)

        if parsed.scheme not in {"http", "https"}:
            raise UnsupportedSourceError(
                "Only http:// and https:// URLs are supported."
            )

        return candidate

    def _extract_content_type(self, response: httpx.Response) -> str | None:
        value = response.headers.get("content-type")
        if not value:
            return None

        return value.split(";")[0].strip().lower()

    def _is_pdf_response(
        self, *,
        response: httpx.Response,
        content_type: str | None,
    ) -> bool:
        if content_type == "application/pdf":
            return True

        if response.content.startswith(b"%PDF-"):
            return True

        disposition = response.headers.get("content-disposition", "").lower()
        if ".pdf" in disposition:
            return True

        final_path = urlparse(str(response.url)).path.lower()
        return final_path.endswith(".pdf")

    def _load_html_response(
        self, *,
        response: httpx.Response,
        requested_url: str,
        content_type: str | None,
    ) -> LoadedDocument:
        soup = BeautifulSoup(response.text, "html.parser")

        for tag_name in ("script", "style", "noscript", "template"):
            for tag in soup.find_all(tag_name):
                tag.decompose()

        title = self._extract_html_title(soup)
        content_root = soup.find("main") or soup.find("article") or soup.body or soup
        raw_text = content_root.get_text("\n", strip=True)

        if not raw_text.strip():
            raise SourceParseError("Fetched HTML page did not contain readable text.")

        return LoadedDocument(
            source_kind="html",
            source=requested_url,
            raw_text=raw_text,
            title=title,
            final_url=str(response.url),
            content_type=content_type,
        )

    def _extract_html_title(self, soup: BeautifulSoup) -> str | None:
        h1 = soup.find("h1")
        if h1 is not None:
            title = h1.get_text(" ", strip=True)
            if title:
                return title

        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            if title:
                return title

        return None

    def _load_pdf_response(
        self, *,
        response: httpx.Response,
        requested_url: str,
        content_type: str | None,
    ) -> LoadedDocument:
        try:
            reader = PdfReader(BytesIO(response.content))
            extracted_pages: list[str] = []

            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text)

            raw_text = "\n".join(extracted_pages).strip()

            title: str | None = None
            if reader.metadata and reader.metadata.title:
                candidate = str(reader.metadata.title).strip()
                title = candidate or None

        except Exception as exc:
            raise SourceParseError("Failed to parse PDF content.") from exc

        if not raw_text:
            raise SourceParseError(
                "PDF text extraction returned no text. The file may be scanned or image-only."
            )

        return LoadedDocument(
            source_kind="pdf",
            source=requested_url,
            raw_text=raw_text,
            title=title,
            final_url=str(response.url),
            content_type=content_type or "application/pdf",
        )