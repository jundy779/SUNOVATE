"""Builds provider instances from settings and reports their honest status."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..core.config import Settings
from ..hermes.text import normalize_term
from ..store.records import User
from .development import (
    DevelopmentExtractiveAIProvider,
    DevelopmentHermesClient,
    DevelopmentIdentityProvider,
    DisabledAIProvider,
    DisabledEmbeddingProvider,
    DisabledNotificationProvider,
    LocalDocumentProvider,
)
from .interfaces import (
    AIProvider,
    DocumentProvider,
    EmbeddingProvider,
    HermesClient,
    IdentityProvider,
    NotificationProvider,
    ProviderStatus,
)


@dataclass
class Providers:
    ai: AIProvider
    embedding: EmbeddingProvider
    document: DocumentProvider
    identity: IdentityProvider
    notification: NotificationProvider
    hermes: HermesClient

    def statuses(self) -> list[ProviderStatus]:
        def status(kind: str, name: str, note: str) -> ProviderStatus:
            mode = "DISABLED" if name == "disabled" else "DEVELOPMENT"
            return ProviderStatus(kind, name, mode, False, note)

        return [
            status("AIProvider", self.ai.name, "Tanpa model eksternal; OQ-11"),
            status("EmbeddingProvider", self.embedding.name, "Model embedding belum disetujui"),
            status("DocumentProvider", self.document.name, "SharePoint belum tersedia; OQ-06"),
            status("IdentityProvider", self.identity.name, "SSO belum ditetapkan; OQ-07"),
            status("NotificationProvider", self.notification.name, "Tidak ada kanal produksi"),
            status("HermesClient", self.hermes.name, "Runtime pengembangan tanpa akses DB"),
            ProviderStatus(
                "MarketDataProvider",
                "not_implemented",
                "DISABLED",
                False,
                "Belum ada sumber data pasar resmi",
            ),
        ]


def build_providers(settings: Settings, lookup: Callable[[str], User | None]) -> Providers:
    """`lookup` resolves a SIMULATED user by email; providers never receive a data store."""
    ai: AIProvider = (
        DevelopmentExtractiveAIProvider(normalize_term)
        if settings.ai_provider == "development_extractive"
        else DisabledAIProvider()
    )
    return Providers(
        ai=ai,
        embedding=DisabledEmbeddingProvider(),
        document=LocalDocumentProvider(),
        identity=DevelopmentIdentityProvider(lookup),
        notification=DisabledNotificationProvider(),
        hermes=DevelopmentHermesClient(ai),
    )
