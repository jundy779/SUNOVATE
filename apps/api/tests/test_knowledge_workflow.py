from typing import Any

from fastapi.testclient import TestClient

from sunovate_api.store.dataset import sid
from sunovate_api.testing import login, make_client

API = "/api/v1"
PPSUN = str(sid("team:PPSUN"))
PSUN = str(sid("team:PSUN"))


def _create(client: TestClient, headers: dict[str, str], **overrides: Any) -> dict[str, Any]:
    payload = {
        "title": "SIMULASI - Draf lesson learned uji",
        "knowledgeType": "LESSON_LEARNED",
        "summary": "Ringkasan simulasi untuk pengujian alur knowledge.",
        "classificationCode": "INTERNAL",
        "sharingScope": "DIRECTORATE",
        "ownerTeamId": PPSUN,
    }
    payload.update(overrides)
    response = client.post(f"{API}/knowledge", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_update_and_revision_conflict() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    entry = _create(client, owner)
    assert entry["lifecycleStatus"] == "DRAFT"
    assert entry["revision"] == 1

    url = f"{API}/knowledge/{entry['id']}"
    updated = client.patch(url, json={"revision": 1, "summary": "Ringkasan simulasi diperbarui."},
                           headers=owner)
    assert updated.status_code == 200
    assert updated.json()["data"]["revision"] == 2

    stale = client.patch(url, json={"revision": 1, "title": "SIMULASI - Judul basi"},
                         headers=owner)
    assert stale.status_code == 409
    assert stale.json()["code"] == "REVISION_CONFLICT"
    assert stale.json()["details"] == {"currentRevision": 2}


def test_duplicate_tags_are_dropped_keeping_first_occurrence() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    entry = _create(client, owner, tags=["b", "a", "b"])
    assert entry["tags"] == ["b", "a"]

    detail = client.get(f"{API}/knowledge/{entry['id']}", headers=owner)
    assert detail.json()["data"]["tags"] == ["b", "a"]
    listed = client.get(f"{API}/knowledge", params={"pageSize": 100}, headers=owner)
    by_id = {item["id"]: item for item in listed.json()["data"]}
    assert by_id[entry["id"]]["tags"] == ["b", "a"]


def test_patch_null_means_unchanged() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    entry = _create(client, owner)
    response = client.patch(f"{API}/knowledge/{entry['id']}", headers=owner,
                            json={"revision": 1, "title": None})
    assert response.status_code == 200, response.text
    assert response.json()["data"]["title"] == entry["title"]
    assert response.json()["data"]["revision"] == 2


def test_cannot_create_for_other_team_or_above_clearance() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    other_team = client.post(f"{API}/knowledge", headers=owner, json={
        "title": "SIMULASI - Entri tim lain", "knowledgeType": "SOP",
        "summary": "Ringkasan simulasi tim lain.", "classificationCode": "INTERNAL",
        "ownerTeamId": PSUN,
    })
    assert other_team.status_code == 403
    too_high = client.post(f"{API}/knowledge", headers=owner, json={
        "title": "SIMULASI - Entri terbatas", "knowledgeType": "SOP",
        "summary": "Ringkasan simulasi terbatas.", "classificationCode": "RESTRICTED",
        "ownerTeamId": PPSUN,
    })
    assert too_high.status_code == 403


def test_read_only_cannot_create() -> None:
    client = make_client()
    response = client.post(f"{API}/knowledge", headers=login(client, "sim.readonly.dhtv"), json={})
    assert response.status_code == 403


def test_unknown_fields_are_rejected() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    entry = _create(client, owner)
    response = client.patch(f"{API}/knowledge/{entry['id']}", headers=owner,
                            json={"revision": 1, "lifecycleStatus": "PUBLISHED"})
    assert response.status_code == 422


def test_draft_is_private_to_owner_team() -> None:
    client = make_client()
    entry = _create(client, login(client, "sim.owner.ppsun"))
    staff = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/knowledge/{entry['id']}", headers=staff).status_code == 404


def test_owner_draft_search_returns_only_owned_drafts() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    owned = _create(client, owner, title="SIMULASI - Draf rekonsiliasi milik saya")

    response = client.get(
        f"{API}/knowledge/drafts/search",
        params={"q": "rekonsiliasi"},
        headers=owner,
    )
    assert response.status_code == 200, response.text
    hits = response.json()["data"]
    assert {item["knowledgeEntryId"] for item in hits} == {owned["id"]}
    assert hits[0]["accessReason"] == "OWNER"

    audit = client.get(f"{API}/audit-logs", headers=login(client, "sim.admin")).json()["data"]
    search_log = next(item for item in audit if item["entityType"] == "knowledge_draft_search")
    assert search_log["detail"] == {"queryLength": 12, "resultCount": 1}
    assert "rekonsiliasi" not in str(search_log["detail"])


def test_full_publication_flow_with_separation_of_duties() -> None:
    client = make_client()
    owner = login(client, "sim.owner.ppsun")
    entry = _create(client, owner)
    submitted = client.post(f"{API}/knowledge/{entry['id']}/submit", headers=owner,
                            json={"revision": 1})
    assert submitted.status_code == 200
    assert submitted.json()["data"]["knowledge"]["lifecycleStatus"] == "IN_REVIEW"
    approval_id = submitted.json()["data"]["approvalRequestId"]

    # Requester cannot hold approval:decide here, so the request is denied by permission.
    self_decide = client.post(f"{API}/approvals/{approval_id}/decision", headers=owner,
                              json={"decision": "APPROVE", "revision": 1, "reason": "Saya sendiri"})
    assert self_decide.status_code == 403

    # Reviewer from another team cannot see it at all.
    reviewer = login(client, "sim.reviewer.akpsun")
    hidden = client.post(f"{API}/approvals/{approval_id}/decision", headers=reviewer,
                         json={"decision": "REJECT", "revision": 1, "reason": "Bukan tim saya"})
    assert hidden.status_code == 404

    coordinator = login(client, "sim.coordinator")
    approved = client.post(f"{API}/approvals/{approval_id}/decision", headers=coordinator,
                           json={"decision": "APPROVE", "revision": 1, "reason": "Lengkap"})
    assert approved.status_code == 200
    assert approved.json()["data"]["status"] == "APPROVED"

    # Now PUBLISHED and DIRECTORATE-shared: readable by another team.
    staff = login(client, "sim.staff.pppsun")
    detail = client.get(f"{API}/knowledge/{entry['id']}", headers=staff)
    assert detail.status_code == 200
    assert detail.json()["data"]["lifecycleStatus"] == "PUBLISHED"

    again = client.post(f"{API}/approvals/{approval_id}/decision", headers=coordinator,
                        json={"decision": "REJECT", "revision": 2, "reason": "Ulang"})
    assert again.status_code == 409


def test_requester_with_decide_permission_cannot_self_approve() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    entry = _create(client, lead, ownerTeamId=PSUN)
    approval_id = client.post(f"{API}/knowledge/{entry['id']}/submit", headers=lead,
                              json={"revision": 1}).json()["data"]["approvalRequestId"]
    response = client.post(f"{API}/approvals/{approval_id}/decision", headers=lead,
                           json={"decision": "REJECT", "revision": 1, "reason": "Diri sendiri"})
    assert response.status_code == 403
    assert response.json()["code"] == "SEPARATION_OF_DUTIES"


def test_reviewer_can_reject_but_not_approve_publication() -> None:
    client = make_client()
    coordinator = login(client, "sim.coordinator")
    entry = _create(client, coordinator, ownerTeamId=str(sid("team:AKPSUN")))
    approval_id = client.post(f"{API}/knowledge/{entry['id']}/submit", headers=coordinator,
                              json={"revision": 1}).json()["data"]["approvalRequestId"]
    reviewer = login(client, "sim.reviewer.akpsun")
    approve = client.post(f"{API}/approvals/{approval_id}/decision", headers=reviewer,
                          json={"decision": "APPROVE", "revision": 1, "reason": "Setuju"})
    assert approve.status_code == 403  # approval:decide without knowledge:publish
    reject = client.post(f"{API}/approvals/{approval_id}/decision", headers=reviewer,
                         json={"decision": "REJECT", "revision": 1, "reason": "Perlu revisi"})
    assert reject.status_code == 200
    detail = client.get(f"{API}/knowledge/{entry['id']}", headers=reviewer).json()["data"]
    assert detail["lifecycleStatus"] == "DRAFT"


def test_other_team_reviewer_cannot_see_request() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    entry = _create(client, lead, ownerTeamId=PSUN)
    approval_id = client.post(f"{API}/knowledge/{entry['id']}/submit", headers=lead,
                              json={"revision": 1}).json()["data"]["approvalRequestId"]
    listed = client.get(f"{API}/approvals", headers=login(client, "sim.reviewer.akpsun"))
    assert approval_id not in {a["id"] for a in listed.json()["data"]}


def test_published_entry_cannot_be_edited() -> None:
    client = make_client()
    lead = login(client, "sim.lead.psun")
    k1 = sid("knowledge:K1")
    response = client.patch(f"{API}/knowledge/{k1}", headers=lead,
                            json={"revision": 1, "summary": "Mencoba mengubah entri terbit."})
    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATE"
