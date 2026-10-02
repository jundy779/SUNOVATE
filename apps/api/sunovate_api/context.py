"""Application context: explicit dependency wiring for the modular monolith."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from .authz.service import AuthorizationService
from .core.config import Settings
from .core.security import DevTokenSigner
from .hermes.gateway import HermesGateway
from .providers.registry import Providers, build_providers
from .store.simulated import SimulatedStore


@dataclass
class AppContext:
    settings: Settings
    store: SimulatedStore
    authz: AuthorizationService
    signer: DevTokenSigner
    providers: Providers
    hermes: HermesGateway
    clock: Callable[[], date]


def build_context(
    settings: Settings,
    *,
    store: SimulatedStore | None = None,
    clock: Callable[[], date] = date.today,
) -> AppContext:
    store = store or SimulatedStore()
    authz = AuthorizationService(store)
    providers = build_providers(settings, store)
    hermes = HermesGateway(
        store=store,
        authz=authz,
        client=providers.hermes,
        max_classification=settings.hermes_max_classification,
        enabled=settings.hermes_mode != "disabled" and settings.ai_provider != "disabled",
    )
    return AppContext(
        settings=settings,
        store=store,
        authz=authz,
        signer=DevTokenSigner(settings.dev_auth_secret, settings.dev_auth_token_ttl_minutes),
        providers=providers,
        hermes=hermes,
        clock=clock,
    )
