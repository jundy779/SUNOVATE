"""Application wiring: one AppRuntime per app, one AppContext per request."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import date

from .authz.service import AuthorizationService
from .core.config import Settings
from .core.security import DevTokenSigner
from .hermes.gateway import HermesGateway
from .providers.development import DevelopmentIdentityProvider
from .providers.registry import Providers, build_providers
from .store.records import User
from .store.repository import DataBackend, Repository
from .store.simulated import SimulatedBackend, SimulatedStore


@dataclass
class AppContext:
    settings: Settings
    store: Repository
    authz: AuthorizationService
    signer: DevTokenSigner
    providers: Providers
    hermes: HermesGateway
    clock: Callable[[], date]


@dataclass
class AppRuntime:
    """Per-process state stored in `app.state.runtime`."""

    settings: Settings
    backend: DataBackend
    signer: DevTokenSigner  # created once: the ephemeral dev secret must not change per request
    providers: Providers  # identity is rebound to the request repository in request_context()
    clock: Callable[[], date]

    def request_context(self, repo: Repository) -> AppContext:
        authz = AuthorizationService(repo)
        providers = replace(
            self.providers, identity=DevelopmentIdentityProvider(repo.user_by_email)
        )
        hermes = HermesGateway(
            store=repo,
            authz=authz,
            client=providers.hermes,
            max_classification=self.settings.hermes_max_classification,
            enabled=(
                self.settings.hermes_mode != "disabled" and self.settings.ai_provider != "disabled"
            ),
        )
        return AppContext(
            settings=self.settings,
            store=repo,
            authz=authz,
            signer=self.signer,
            providers=providers,
            hermes=hermes,
            clock=self.clock,
        )


def _no_user(_email: str) -> User | None:
    return None


def build_runtime(
    settings: Settings,
    *,
    backend: DataBackend | None = None,
    clock: Callable[[], date] = date.today,
) -> AppRuntime:
    """The only place where the data backend is chosen."""
    if backend is None:
        if settings.data_backend == "postgres":
            # Lazy import: the simulated mode never loads the PostgreSQL driver.
            from .store.postgres import PostgresBackend

            backend = PostgresBackend(settings.database_url)
        else:
            backend = SimulatedBackend(SimulatedStore())
    return AppRuntime(
        settings=settings,
        backend=backend,
        signer=DevTokenSigner(settings.dev_auth_secret, settings.dev_auth_token_ttl_minutes),
        providers=build_providers(settings, _no_user),
        clock=clock,
    )
