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
    assert data["metrics"]["totalActiveTasks"] == 1
    assert data["metrics"]["attentionCount"] == 2
    assert data["metrics"]["inProgressTasks"] == 1
    assert data["metrics"]["completedThisWeek"] == 0
    assert data["metrics"]["tasksOverdue"] == 1
    assert {a["ownerTeamCode"] for a in data["attention"]} == {"PSUN"}
    assert data["attention"][0]["category"] == "Tugas"
    assert data["attention"][0]["assigneeName"] == "Ketua Tim Simulasi PSUN"
    assert data["attention"][0]["workStatus"] == "IN_PROGRESS"
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


def test_work_output_and_task_crud_are_scoped_and_audited() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    team_id = str(sid("team:PPPSUN"))

    created_output = client.post(
        f"{API}/work-outputs",
        headers=staff,
        json={
            "title": "Output simulasi pengujian",
            "description": "Deskripsi output hanya untuk pengujian otomatis.",
            "ownerTeamId": team_id,
            "classificationCode": "INTERNAL",
            "targetDate": "2026-10-20",
        },
    )
    assert created_output.status_code == 201
    output = created_output.json()["data"]
    assert output["dataOrigin"] == "USER_ENTERED"

    created_task = client.post(
        f"{API}/tasks",
        headers=staff,
        json={
            "title": "Tugas simulasi pengujian",
            "ownerTeamId": team_id,
            "workOutputId": output["id"],
            "classificationCode": "INTERNAL",
            "dueDate": "2026-10-18",
        },
    )
    assert created_task.status_code == 201
    task = created_task.json()["data"]

    updated = client.patch(
        f"{API}/tasks/{task['id']}",
        headers=staff,
        json={"revision": task["revision"], "status": "COMPLETED"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["progress"] == 100

    deleted = client.delete(
        f"{API}/tasks/{task['id']}?revision={updated.json()['data']['revision']}",
        headers=staff,
    )
    assert deleted.status_code == 204
    ids = {
        item["id"]
        for item in client.get(f"{API}/tasks?pageSize=100", headers=staff).json()["data"]
    }
    assert task["id"] not in ids


def test_pending_and_follow_up_crud_require_manage_permission() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    staff = login(client, "sim.staff.pppsun")
    team_id = str(sid("team:PSUN"))
    body = {
        "title": "Pending matter simulasi baru",
        "description": "Catatan simulasi untuk pengujian pengelolaan pending matter.",
        "ownerTeamId": team_id,
        "classificationCode": "INTERNAL",
        "dueDate": "2026-10-20",
    }

    assert client.post(f"{API}/pending-matters", headers=staff, json=body).status_code == 403
    created = client.post(f"{API}/pending-matters", headers=lead, json=body)
    assert created.status_code == 201
    pending = created.json()["data"]

    follow_up = client.post(
        f"{API}/follow-ups",
        headers=lead,
        json={
            "title": "Tindak lanjut simulasi",
            "ownerTeamId": team_id,
            "pendingMatterId": pending["id"],
            "classificationCode": "INTERNAL",
            "dueDate": "2026-10-19",
        },
    )
    assert follow_up.status_code == 201
    item = follow_up.json()["data"]
    updated = client.patch(
        f"{API}/follow-ups/{item['id']}",
        headers=lead,
        json={"revision": item["revision"], "status": "DONE"},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["deadlineState"] == "COMPLETED"


def test_document_version_rejects_unsafe_local_paths() -> None:
    """AUD-20: only plain local:// segments, so no future provider can escape its storage root."""
    client = make_client()
    lead = login(client, "sim.lead.psun")
    doc = sid("doc:K1")
    for location in (
        "local://../../etc/passwd",
        "local://simulated/../rahasia.pdf",
        "local:///absolut.pdf",
        "local://simulated\\\\k1.pdf",
        "local://simulated/%2e%2e/k1.pdf",
        "local://simulated//k1.pdf",
    ):
        body = {"versionLabel": "v9", "checksumSha256": "b" * 64, "providerLocation": location}
        response = client.post(f"{API}/documents/{doc}/versions", json=body, headers=lead)
        assert response.status_code == 422, location
    ok = {"versionLabel": "v9", "checksumSha256": "b" * 64,
          "providerLocation": "local://simulated/k1-v9.pdf"}
    assert client.post(f"{API}/documents/{doc}/versions", json=ok, headers=lead).status_code == 201
