"""In-memory vault of RAHASIA documents for the view-only viewer (ADR-020, PROPOSED).

Holds SIMULATED_DATA only. Content is sealed per page with envelope encryption, readers are
granted explicitly per document (never by team membership alone), and clearance must cover the
document classification. A sliding-window limit stops bulk page scraping.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid5
from zoneinfo import ZoneInfo

from .crypto import KeyProvider, SealedContent, open_sealed, seal

_NAMESPACE = UUID("6f1d3c52-5d0a-4a2f-9f53-2b7a1c0e8d44")
_JAKARTA = ZoneInfo("Asia/Jakarta")


@dataclass(frozen=True)
class SecureDocument:
    id: UUID
    title: str
    classification_code: str
    owner_team_code: str
    reader_emails: frozenset[str]
    pages: tuple[SealedContent, ...]

    @property
    def page_count(self) -> int:
        return len(self.pages)


@dataclass(frozen=True)
class PageAccess:
    allowed: bool
    retry_after_seconds: int = 0


@dataclass
class PageRateLimiter:
    """At most `limit` page renders per principal within `window_seconds`."""

    limit: int = 40
    window_seconds: int = 60
    clock: Callable[[], float] = time.monotonic
    _hits: dict[UUID, deque[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def check(self, principal_id: UUID) -> PageAccess:
        now = self.clock()
        with self._lock:
            hits = self._hits.setdefault(principal_id, deque())
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            if len(hits) >= self.limit:
                return PageAccess(False, max(1, int(self.window_seconds - (now - hits[0]))))
            hits.append(now)
            return PageAccess(True)


def _associated_data(document_id: UUID, page_index: int) -> bytes:
    return f"{document_id}:{page_index}".encode()


class SecureVault:
    def __init__(self, provider: KeyProvider, *, limiter: PageRateLimiter | None = None) -> None:
        self._provider = provider
        self._documents: dict[UUID, SecureDocument] = {}
        self.limiter = limiter or PageRateLimiter()

    @property
    def key_id(self) -> str:
        return self._provider.key_id

    def add(
        self,
        *,
        slug: str,
        title: str,
        classification_code: str,
        owner_team_code: str,
        reader_emails: frozenset[str],
        pages: list[str],
    ) -> SecureDocument:
        document_id = uuid5(_NAMESPACE, slug)
        sealed = tuple(
            seal(
                text.encode(), self._provider, associated_data=_associated_data(document_id, index)
            )
            for index, text in enumerate(pages)
        )
        document = SecureDocument(
            id=document_id,
            title=title,
            classification_code=classification_code,
            owner_team_code=owner_team_code,
            reader_emails=frozenset(email.lower() for email in reader_emails),
            pages=sealed,
        )
        self._documents[document_id] = document
        return document

    def documents(self) -> list[SecureDocument]:
        return sorted(self._documents.values(), key=lambda doc: doc.title)

    def get(self, document_id: UUID) -> SecureDocument | None:
        return self._documents.get(document_id)

    def page_text(self, document: SecureDocument, page_number: int) -> str:
        sealed = document.pages[page_number - 1]
        return open_sealed(
            sealed, self._provider, associated_data=_associated_data(document.id, page_number - 1)
        ).decode()


def jakarta_now() -> datetime:
    return datetime.now(_JAKARTA)


def seed_simulated_vault(vault: SecureVault) -> None:
    """SIMULATED_DATA only: invented content, no real SUN information."""
    vault.add(
        slug="simulasi-rahasia-pedoman-penilaian",
        title="SIMULASI - Pedoman Penilaian Internal (Rahasia)",
        classification_code="RESTRICTED",
        owner_team_code="PPSUN",
        reader_emails=frozenset({"sim.coordinator@sunovate.local", "sim.lead.psun@sunovate.local"}),
        pages=[
            "Dokumen ini adalah contoh fiktif untuk menguji penampil dokumen rahasia.\n"
            "Isi tidak mewakili kebijakan, angka, atau proses Direktorat Surat Utang Negara.\n"
            "Penanda uji: KODE-UJI-RAHASIA-7781.",
            "Halaman kedua berisi uraian contoh tahapan pemeriksaan internal.\n"
            "Setiap halaman hanya dapat dilihat sebagai gambar dengan tanda air pembaca.",
        ],
    )
