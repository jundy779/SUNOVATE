"""Cross-cutting security tests: authentication, scope, classification, leakage."""

from __future__ import annotations

import pytest

from sunovate_api.authz.catalog import ROLE_PERMISSIONS
from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

API = "/api/v1"

PROTECTED_GET = [
    "/auth/me", "/users", "/teams", "/roles", "/permissions", "/classifications", "/knowledge",
    f"/knowledge/{sid('knowledge:K1')}", "/documents", f"/documents/{sid('doc:K1')}",
    f"/documents/{sid('doc:K1')}/versions", "/search?q=metadata", "/dashboard/summary",
    "/work-outputs", f"/work-outputs/{sid('wo:WO1')}", "/tasks", "/milestones",
    "/pending-matters", "/follow-ups", "/audit-logs", "/approvals", "/providers",
    "/data-quality-issues",
]
PROTECTED_POST = ["/knowledge", "/hermes/query", f"/approvals/{sid('approval:K7')}/decision"]

USERS = ["sim.admin", "sim.coordinator", "sim.lead.psun", "sim.owner.ppsun",
         "sim.reviewer.akpsun", "sim.staff.pppsun", "sim.auditor", "sim.readonly.dhtv"]


@pytest.mark.parametrize("path", PROTECTED_GET)
def test_get_requires_authentication(path: str) -> None:
    assert make_client().get(API + path).status_code == 401


@pytest.mark.parametrize("path", PROTECTED_POST)
def test_post_requires_authentication(path: str) -> None:
    assert make_client().post(API + path, json={}).status_code == 401


def test_confidential_records_never_returned_to_any_seeded_user() -> None:
    client = make_client()
    k6 = str(sid("knowledge:K6"))
    for user in USERS:
        headers = login(client, user)
        listed = client.get(f"{API}/knowledge?pageSize=100", headers=headers)
        if listed.status_code == 200:
            assert k6 not in {e["id"] for e in listed.json()["data"]}, user
            assert client.get(f"{API}/knowledge/{k6}", headers=headers).status_code == 404


def test_listing_respects_team_scope_and_sharing() -> None:
    client = make_client()
    listed = client.get(f"{API}/knowledge?pageSize=100",
                        headers=login(client, "sim.staff.pppsun")).json()["data"]
    for entry in listed:
        own_team = entry["ownerTeamCode"] == "PPPSUN"
        shared = entry["sharingScope"] == "DIRECTORATE" and entry["lifecycleStatus"] == "PUBLISHED"
        assert own_team or shared, entry["title"]
        assert entry["classificationCode"] in {"PUBLIC", "INTERNAL"}


def test_cross_team_detail_returns_404_not_403() -> None:
    client = make_client()
    response = client.get(f"{API}/knowledge/{sid('knowledge:K2')}",
                          headers=login(client, "sim.staff.pppsun"))
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_permission_matrix_matches_role_catalog() -> None:
    client = make_client()
    roles = client.get(f"{API}/roles", headers=login(client, "sim.admin")).json()["data"]
    assert {r["code"]: frozenset(r["permissions"]) for r in roles} == ROLE_PERMISSIONS


def test_no_role_combines_hermes_and_audit_by_default() -> None:
    # Auditors read audit logs but do not query Hermes; admins do not query Hermes.
    assert "hermes:query" not in ROLE_PERMISSIONS["auditor"]
    assert "hermes:query" not in ROLE_PERMISSIONS["system_admin"]


def test_error_responses_do_not_leak_internals() -> None:
    client = make_client()
    response = client.get(f"{API}/knowledge/not-a-uuid", headers=login(client, "sim.admin"))
    assert response.status_code == 422
    assert "Traceback" not in response.text


def test_every_response_is_labelled_simulated() -> None:
    client = make_client()
    headers = login(client, "sim.coordinator")
    for path in ["/knowledge", "/tasks", "/dashboard/summary", "/teams"]:
        assert client.get(API + path, headers=headers).json()["meta"]["dataLabel"] == (
            "SIMULATED_DATA"
        )
