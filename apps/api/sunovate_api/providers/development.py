"""Development-only provider implementations. No network calls, no external services."""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from uuid import UUID

from ..store.records import User
from .interfaces import (
    AIProvider,
    DocumentLocation,
    GenerationRequest,
    GenerationResult,
    ProviderDisabledError,
)

_SENTENCE = re.compile(r"(?<=[.!?])\s+")
_WORD = re.compile(r"[a-z0-9]+")


class DevelopmentExtractiveAIProvider:
    """Deterministic extractive composer: copies the most relevant sentence of each passage.

    It never adds facts that are not present in the passages.
    """

    name = "development_extractive"

    def __init__(self, term_normalizer: Callable[[str], str]) -> None:
        self._normalize = term_normalizer

    def _best_sentence(self, text: str, terms: frozenset[str]) -> str:
        sentences = [s.strip() for s in _SENTENCE.split(text) if s.strip()]

        def score(sentence: str) -> int:
            words = {self._normalize(w) for w in _WORD.findall(sentence.lower())}
            return len(words & terms)

        return max(sentences, key=score) if sentences else text.strip()

    def generate(self, request: GenerationRequest) -> GenerationResult:
        lines = [
            f"{n}. {self._best_sentence(p.text, request.query_terms)} [{p.index}]"
            for n, p in enumerate(request.passages, start=1)
        ]
        body = "Berdasarkan sumber yang dapat Anda akses:\n\n" + "\n".join(lines)
        body += (
            "\n\nJawaban disusun secara ekstraktif oleh penyedia pengembangan dan bukan "
            "keputusan atau sikap resmi."
        )
        return GenerationResult(text=body, provider=self.name)


class DisabledAIProvider:
    name = "disabled"

    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise ProviderDisabledError("AI provider is disabled")


class DisabledEmbeddingProvider:
    name = "disabled"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        raise ProviderDisabledError("Embedding provider is disabled until a model is approved")


_LOCAL_SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")


def is_safe_local_location(location: str) -> bool:
    """`local://a/b/c.ext` with plain segments only (AUD-20).

    Rejects traversal (`..`, `.`), empty segments, absolute or drive paths, backslashes,
    percent-encoding, and control characters, so a future provider that reads from disk can join
    the path under its storage root without escaping it.
    """
    if not location.startswith("local://"):
        return False
    path = location.removeprefix("local://")
    if not path or len(path) > 900:
        return False
    return all(
        segment not in {".", ".."} and _LOCAL_SEGMENT.fullmatch(segment) is not None
        for segment in path.split("/")
    )


class LocalDocumentProvider:
    """Validates `local://` references only. Does not read, upload, or copy files."""

    name = "local"

    def describe(self, location: str) -> DocumentLocation:
        if not is_safe_local_location(location):
            return DocumentLocation(
                "local", location, False, "Hanya referensi local:// dengan path sederhana didukung"
            )
        return DocumentLocation(
            "local", location, False, "Referensi simulasi; file tidak tersedia di repository"
        )


class DevelopmentIdentityProvider:
    name = "development"

    def __init__(self, lookup: Callable[[str], User | None]) -> None:
        self._lookup = lookup

    def resolve_login(self, email: str) -> UUID | None:
        user = self._lookup(email)
        if user is None or user.status != "ACTIVE" or user.data_origin != "SIMULATED_DATA":
            return None
        return user.id


class DisabledNotificationProvider:
    name = "disabled"

    def send(self, recipient_user_id: UUID, subject: str, body: str) -> bool:
        return False


class DevelopmentHermesClient:
    """Hermes runtime for development: delegates composition to the configured AIProvider."""

    name = "development"

    def __init__(self, ai: AIProvider) -> None:
        self._ai = ai

    def answer(self, request: GenerationRequest) -> GenerationResult:
        return self._ai.generate(request)
