"""SAVI administrative tasks: draft from readable data, employee review, audit without content."""

from __future__ import annotations

from uuid import uuid4

from sunovate_api.testing import login, make_client

API = "/api/v1"


def test_work_report_is_a_draft_built_only_from_readable_work() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    response = client.post(f"{API}/savi/tasks/work-report", headers=staff)
    assert response.status_code == 201
    draft = response.json()["data"]
    assert draft["status"] == "AWAITING_REVIEW"
    assert draft["text"].startswith("Draf laporan pekerjaan per ")
    assert "Periksa dan lengkapi sebelum digunakan." in draft["text"]
    readable = {
        row["id"]
        for row in client.get(f"{API}/dashboard/summary", headers=staff).json()["data"]["attention"]
    }
    assert {source["id"] for source in draft["sources"]} <= readable


def test_summary_counts_match_the_listed_items_and_dates_are_local() -> None:
    client = make_client()
    draft = client.post(
        f"{API}/savi/tasks/work-report", headers=login(client, "sim.staff.pppsun")
    ).json()["data"]
    listed = [line for line in draft["text"].splitlines() if ", tindak lanjut):" in line]
    assert f"- Tindak lanjut terlambat atau jatuh tempo dekat: {len(listed)}" in draft["text"]
    assert "tenggat 20" not in draft["text"], "dates use dd-mm-yyyy, not ISO"


def test_report_scope_follows_the_caller() -> None:
    client = make_client()
    staff = client.post(f"{API}/savi/tasks/work-report", headers=login(client, "sim.staff.pppsun"))
    coordinator = client.post(
        f"{API}/savi/tasks/work-report", headers=login(client, "sim.coordinator")
    )
    assert "Cakupan: PPPSUN" in staff.json()["data"]["text"]
    assert "Cakupan: Seluruh tim Direktorat SUN" in coordinator.json()["data"]["text"]
    assert (
        coordinator.json()["data"]["counts"]["activeTasks"]
        >= staff.json()["data"]["counts"]["activeTasks"]
    )


def test_review_is_recorded_without_the_report_text() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    draft = client.post(f"{API}/savi/tasks/work-report", headers=staff).json()["data"]
    review = {
        "draftId": draft["draftId"],
        "kind": "WORK_REPORT",
        "decision": "ACCEPTED",
        "edited": True,
    }
    assert client.post(f"{API}/savi/tasks/reviews", json=review, headers=staff).status_code == 201
    logs = client.get(
        f"{API}/audit-logs?action=SAVI_TASK_REVIEWED", headers=login(client, "sim.auditor")
    ).json()["data"]
    assert logs[0]["detail"]["decision"] == "ACCEPTED"
    assert logs[0]["detail"]["edited"] is True
    assert "Draf laporan" not in str(logs)


def test_review_rejects_unknown_decisions_and_requires_permission() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    bad = {"draftId": str(uuid4()), "kind": "WORK_REPORT", "decision": "AUTO_SEND"}
    assert client.post(f"{API}/savi/tasks/reviews", json=bad, headers=staff).status_code == 422
    admin = login(client, "sim.admin")  # no hermes:query
    assert client.post(f"{API}/savi/tasks/work-report", headers=admin).status_code == 403


def _approved_text(client, headers) -> tuple[str, str]:  # type: ignore[no-untyped-def]
    draft = client.post(f"{API}/savi/tasks/work-report", headers=headers).json()["data"]
    return draft["draftId"], draft["text"] + "\nCatatan pegawai: sudah diperiksa."


def test_word_export_contains_the_approved_text_and_is_not_stored() -> None:
    from io import BytesIO

    from docx import Document

    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    draft_id, text = _approved_text(client, staff)
    body = {"draftId": draft_id, "kind": "WORK_REPORT", "text": text}
    response = client.post(f"{API}/savi/tasks/documents/word", json=body, headers=staff)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert "no-store" in response.headers["cache-control"]
    assert "attachment" in response.headers["content-disposition"]
    document = Document(BytesIO(response.content))
    paragraphs = [p.text for p in document.paragraphs]
    assert paragraphs[0].startswith("Draf laporan pekerjaan per ")
    assert document.paragraphs[0].style.name == "Heading 1"
    assert "Catatan pegawai: sudah diperiksa." in paragraphs
    assert any(p.style.name == "List Bullet" for p in document.paragraphs)
    logs = client.get(
        f"{API}/audit-logs?action=SAVI_TASK_EXPORTED", headers=login(client, "sim.auditor")
    ).json()["data"]
    assert logs[0]["detail"]["format"] == "DOCX"
    assert "Catatan pegawai" not in str(logs), "the audit never holds the draft text"


def test_word_export_strips_characters_word_cannot_hold_and_limits_size() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    draft_id, _ = _approved_text(client, staff)
    unsafe = {"draftId": draft_id, "kind": "WORK_REPORT", "text": "Judul\nIsi\x00\x07 aman"}
    assert (
        client.post(f"{API}/savi/tasks/documents/word", json=unsafe, headers=staff).status_code
        == 200
    )
    too_long = {"draftId": draft_id, "kind": "WORK_REPORT", "text": "x" * 20_001}
    assert (
        client.post(f"{API}/savi/tasks/documents/word", json=too_long, headers=staff).status_code
        == 422
    )
    admin = login(client, "sim.admin")
    assert (
        client.post(f"{API}/savi/tasks/documents/word", json=unsafe, headers=admin).status_code
        == 403
    )
