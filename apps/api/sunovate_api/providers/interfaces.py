"""Provider interfaces. External systems are reached only through these contracts.

Production implementations do not exist yet; see docs/03-architecture/provider-abstraction.md.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


class ProviderDisabledError(RuntimeError):
    """Raised when a disabled provider is invoked."""


@dataclass(frozen=True)
class ContextPassage:
    """An already-authorized passage handed to the AI layer. Treated as untrusted data."""

    index: int
    title: str
    section_label: str
    text: str


@dataclass(frozen=True)
class GenerationRequest:
    question: str
    passages: Sequence[ContextPassage]
    query_terms: frozenset[str]


@dataclass(frozen=True)
class GenerationResult:
    text: str
    provider: str


@dataclass(frozen=True)
class DocumentLocation:
    provider: str
    location: str
    available: bool
    note: str


@dataclass(frozen=True)
class ProviderStatus:
    kind: str
    implementation: str
    mode: str  # DEVELOPMENT | DISABLED
    production_ready: bool
    note: str


class AIProvider(Protocol):
    name: str

    def generate(self, request: GenerationRequest) -> GenerationResult: ...


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class DocumentProvider(Protocol):
    name: str

    def describe(self, location: str) -> DocumentLocation: ...


class IdentityProvider(Protocol):
    name: str

    def resolve_login(self, email: str) -> UUID | None: ...


class NotificationProvider(Protocol):
    name: str

    def send(self, recipient_user_id: UUID, subject: str, body: str) -> bool: ...


class HermesClient(Protocol):
    """Hermes runtime. Receives only authorized passages; has no database access."""

    name: str

    def answer(self, request: GenerationRequest) -> GenerationResult: ...
