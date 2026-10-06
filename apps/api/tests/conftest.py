"""Shared fixtures for apps/api/tests (backend reset per test, design 15.2)."""

from __future__ import annotations

import pytest

from sunovate_api.testing import reset_backend_state


@pytest.fixture(autouse=True)
def _reset_backend_state() -> None:
    """No-op on simulated; TRUNCATE + seed before every test on postgres."""
    reset_backend_state()
