"""Remaining audit findings closed on 28 October 2026 (AUD-03 partial, AUD-17, AUD-21)."""

from __future__ import annotations

import pytest

from sunovate_api.testing import login, make_client, make_settings

API = "/api/v1"


def test_user_directory_shows_clearance_only_to_user_administrators() -> None:
    client = make_client()
    lead_rows = client.get(f"{API}/users?pageSize=100", headers=login(client, "sim.lead.psun"))
    assert lead_rows.status_code == 200
    assert all(row["clearanceCode"] is None for row in lead_rows.json()["data"])
    admin_rows = client.get(f"{API}/users?pageSize=100", headers=login(client, "sim.admin"))
    assert all(row["clearanceCode"] for row in admin_rows.json()["data"])


def test_reading_the_audit_trail_is_itself_recorded() -> None:
    client = make_client()
    auditor = login(client, "sim.auditor")
    client.get(f"{API}/audit-logs?action=WORK_EXPORT", headers=auditor)
    logs = client.get(f"{API}/audit-logs?action=AUDIT_LOG_READ", headers=auditor).json()["data"]
    assert logs, "the first read must appear in the trail"
    assert set(logs[0]["detail"]) == {"filtered", "returned"}
    assert "WORK_EXPORT" not in str(logs[0]["detail"])


@pytest.mark.parametrize("secret", ["pendek", "x" * 31])
def test_short_dev_auth_secrets_are_rejected(secret: str) -> None:
    with pytest.raises(ValueError, match="DEV_AUTH_SECRET"):
        make_settings(dev_auth_secret=secret)


def test_empty_or_long_dev_auth_secrets_are_accepted() -> None:
    assert make_settings(dev_auth_secret="").dev_auth_secret == ""
    assert len(make_settings(dev_auth_secret="y" * 32).dev_auth_secret) == 32
