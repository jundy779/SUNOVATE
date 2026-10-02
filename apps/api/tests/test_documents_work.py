import hashlib
from datetime import date

import pytest

from sunovate_api.domain import deadline_state
from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

API = "/api/v1"


def test_document_versions_reject_duplicate_checksum() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    doc = sid("doc:K2")
    existing = client.get(f"{API}/documents/{doc}/versions", headers=owner).json()["data"]
    duplicate = client.post(f"{API}/documents/{doc}/versions", headers=owner, json={
        "versionLabel": "v1.1", "checksumSha256": existing[0]["checksumSha256"],
        "providerLocation": "local://simulated/k2-v1-1.pdf",
    })
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "DUPLICATE_CHECKSUM"

    fresh = client.post(f"{API}/documents/{doc}/versions", headers=owner, json={
        "versionLabel": "v1.1", "checksumSha256": hashlib.sha256(b"SIMULATED v1.1").hexdigest(),
        "providerLocation": "local://simulated/k2-v1-1.pdf",
    })
    assert fresh.status_code == 201
    assert fresh.json()["data"]["extractionStatus"] == "PENDING"


def test_document_version_requires_permission_and_local_reference() -> None:
    client = make_client()
    doc = sid("doc:K1")
    body = {"versionLabel": "v2", "checksumSha256": "a" * 64,
            "providerLocation": "https://sharepoint.example/x.pdf"}
    assert client.post(f"{API}/documents/{doc}/versions", json=body,
                       headers=login(client, "sim.readonly.dhtv")).status_code == 403
    lead = login(client, "sim.lead.psun")
    assert client.post(f"{API}/documents/{doc}/versions", json=body,
                       headers=lead).status_code == 422


def test_document_detail_follows_knowledge_visibility() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/documents/{sid('doc:K1')}", headers=staff).status_code == 200
    assert client.get(f"{API}/documents/{sid('doc:K2')}", headers=staff).status_code == 404
    assert client.get(f"{API}/documents/{sid('doc:K6')}", headers=staff).status_code == 404


@pytest.mark.parametrize(
    ("due", "status", "expected"),
    [
        (date(2026, 9, 30), "IN_PROGRESS", "OVERDUE"),
        (date(2026, 10, 1), "IN_PROGRESS", "DUE_TODAY"),
        (date(2026, 10, 8), "IN_PROGRESS", "DUE_SOON"),
        (date(2026, 10, 9), "IN_PROGRESS", "SAFE"),
        (date(2026, 9, 1), "COMPLETED", "COMPLETED"),
        (None, "IN_PROGRESS", None),
    ],
)
def test_deadline_state(due: date | None, status: str, expected: str | None) -> None:
    assert deadline_state(due, status, date(2026, 10, 1), 7) == expected


def test_tasks_are_scoped_and_carry_deadline_state() -> None:
    client = make_client()
    tasks = client.get(f"{API}/tasks", headers=login(client, "sim.owner.ppsun")).json()["data"]
    assert {t["ownerTeamCode"] for t in tasks} == {"PPSUN"}
    assert {t["deadlineState"] for t in tasks} == {"DUE_TODAY", "DUE_SOON"}


def test_restricted_work_is_hidden_from_internal_clearance() -> None:
    client = make_client()
    tasks = client.get(f"{API}/tasks", headers=login(client, "sim.readonly.dhtv")).json()["data"]
    assert tasks == []  # DHTV task is RESTRICTED; read_only user has INTERNAL clearance


def test_task_update_scope_and_concurrency() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    own, other = sid("task:T4"), sid("task:T1")
    assert client.patch(f"{API}/tasks/{other}", headers=staff,
                        json={"revision": 1, "status": "IN_PROGRESS"}).status_code == 404
    ok = client.patch(f"{API}/tasks/{own}", headers=staff,
                      json={"revision": 1, "status": "COMPLETED"})
    assert ok.status_code == 200
    assert ok.json()["data"]["progress"] == 100
    assert ok.json()["data"]["deadlineState"] == "COMPLETED"
    stale = client.patch(f"{API}/tasks/{own}", headers=staff, json={"revision": 1, "progress": 5})
    assert stale.status_code == 409


def test_dashboard_summary_uses_authorized_scope() -> None:
    client = make_client()
    lead = client.get(f"{API}/dashboard/summary", headers=login(client, "sim.lead.psun"))
    data = lead.json()["data"]
    assert data["scope"]["teamCodes"] == ["PSUN"]
    assert data["metrics"]["tasksOverdue"] == 1
    assert {a["ownerTeamCode"] for a in data["attention"]} == {"PSUN"}
    coordinator = client.get(f"{API}/dashboard/summary",
                             headers=login(client, "sim.coordinator")).json()["data"]
    assert coordinator["metrics"]["pendingApprovals"] == 1
    assert len(coordinator["tasksByStatus"]) == 7


def test_pending_matters_and_follow_ups() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    pending = client.get(f"{API}/pending-matters", headers=staff).json()["data"]
    follow_ups = client.get(f"{API}/follow-ups", headers=staff).json()["data"]
    assert [p["ownerTeamCode"] for p in pending] == ["PPPSUN"]
    assert follow_ups[0]["deadlineState"] == "OVERDUE"
