"""Test helpers shared by `apps/api/tests` and the root `tests/` suites."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi.testclient import TestClient

from .context import build_context
from .core.config import Settings
from .main import create_app
from .store.dataset import REFERENCE_DATE

TEST_SECRET = "test-only-secret-not-for-production"  # noqa: S105 - test fixture value


def make_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "dev_auth_secret": TEST_SECRET,
        "log_level": "WARNING",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def make_client(today: date = REFERENCE_DATE, **overrides: Any) -> TestClient:
    settings = make_settings(**overrides)
    app = create_app(settings, build_context(settings, clock=lambda: today))
    return TestClient(app)


def login(client: TestClient, local_part: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/dev/login", json={"email": f"{local_part}@sunovate.local"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['data']['accessToken']}"}
