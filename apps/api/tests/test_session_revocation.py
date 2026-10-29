"""Logout revokes the session token on the server (AUD-05). SIMULATED_DATA only."""

from __future__ import annotations

import base64
import json
from datetime import UTC, datetime, timedelta

from sunovate_api.core.security import DevTokenSigner
from sunovate_api.testing import TEST_SECRET, login, make_client

API = "/api/v1"


def test_logout_makes_the_same_token_unusable() -> None:
    client = make_client()
    headers = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/auth/me", headers=headers).status_code == 200

    logout = client.post(f"{API}/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert logout.json()["data"] == {"loggedOut": True}

    after = client.get(f"{API}/auth/me", headers=headers)
    assert after.status_code == 401
    assert after.json()["message"] == "Sesi telah diakhiri, silakan masuk kembali"
    assert client.post(f"{API}/auth/logout", headers=headers).status_code == 401


def test_logout_ends_only_that_session() -> None:
    client = make_client()
    first = login(client, "sim.staff.pppsun")
    second = login(client, "sim.staff.pppsun")
    assert first != second, "every login issues a token with its own id"
    client.post(f"{API}/auth/logout", headers=first)
    assert client.get(f"{API}/auth/me", headers=second).status_code == 200


def test_logout_is_audited_without_the_token() -> None:
    client = make_client()
    headers = login(client, "sim.staff.pppsun")
    token = headers["Authorization"][7:]
    client.post(f"{API}/auth/logout", headers=headers)
    logs = client.get(f"{API}/audit-logs?action=LOGOUT", headers=login(client, "sim.admin"))
    entries = logs.json()["data"]
    assert entries and entries[0]["entityType"] == "user"
    assert token not in logs.text


def test_tokens_without_an_id_are_refused() -> None:
    client = make_client()
    signer = DevTokenSigner(TEST_SECRET, 60)
    now = datetime.now(UTC)
    body = {"sub": "00000000-0000-0000-0000-000000000000", "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp())}
    payload = base64.urlsafe_b64encode(json.dumps(body).encode()).rstrip(b"=").decode()
    legacy = f"{payload}.{signer._sign(payload)}"
    response = client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {legacy}"})
    assert response.status_code == 401


def test_expired_revocations_are_purged_at_the_next_logout() -> None:
    client = make_client()
    backend = client.app.state.runtime.backend  # simulated or PostgreSQL, per TEST_BACKEND
    old = datetime.now(UTC) - timedelta(days=1)
    with backend.session() as repo:
        user = repo.user_by_email("sim.staff.pppsun@sunovate.local")
        with repo.transaction():
            repo.revoke_token("a" * 32, user.id, old)
        assert repo.is_token_revoked("a" * 32)
    client.post(f"{API}/auth/logout", headers=login(client, "sim.staff.pppsun"))
    with backend.session() as repo:
        assert not repo.is_token_revoked("a" * 32)
