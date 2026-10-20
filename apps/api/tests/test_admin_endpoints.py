from sunovate_api.testing import login, make_client

API = "/api/v1"


def test_teams_are_the_six_confirmed_codes() -> None:
    client = make_client()
    teams = client.get(f"{API}/teams", headers=login(client, "sim.staff.pppsun")).json()["data"]
    assert [t["code"] for t in teams] == ["AKPSUN", "DHTV", "PPPSUN", "PPSUN", "PSUN",
                                         "SUN_TEMATIK"]
    tematik = next(t for t in teams if t["code"] == "SUN_TEMATIK")
    assert tematik["validationStatus"] == "OPEN_QUESTION"
    assert all(t["dataOrigin"] == "SIMULATED_DATA" for t in teams)


def test_roles_and_permissions_require_role_read() -> None:
    client = make_client()
    assert client.get(f"{API}/roles", headers=login(client, "sim.staff.pppsun")).status_code == 403
    admin = login(client, "sim.admin")
    roles = client.get(f"{API}/roles", headers=admin).json()["data"]
    assert len(roles) == 8
    permissions = client.get(f"{API}/permissions", headers=admin).json()["data"]
    descriptions = {item["code"]: item["description"] for item in permissions}
    assert descriptions["hermes:query"] == "Bertanya kepada SAVI AI"
    assert descriptions["hermes:feedback"] == ("Memberikan penilaian terhadap jawaban SAVI AI")
    visible_text = " ".join(descriptions.values()).lower()
    assert "hermes" not in visible_text
    assert "permission" not in visible_text
    assert "pending matter" not in visible_text


def test_audit_log_requires_permission_and_records_denials() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    assert client.get(f"{API}/audit-logs", headers=staff).status_code == 403
    logs = client.get(f"{API}/audit-logs?action=ACCESS_DENIED",
                      headers=login(client, "sim.auditor")).json()["data"]
    assert logs[0]["entityType"] == "audit_log"
    assert logs[0]["outcome"] == "DENIED"


def test_providers_report_no_production_integration() -> None:
    client = make_client()
    body = client.get(f"{API}/providers", headers=login(client, "sim.admin")).json()
    assert body["meta"]["productionIntegrations"] == "DISABLED"
    assert not any(p["productionReady"] for p in body["data"])


def test_sme_question_intake_requires_review_and_all_team_scope() -> None:
    client = make_client()
    path = f"{API}/hermes/sme-question-intake"

    assert client.get(path, headers=login(client, "sim.staff.pppsun")).status_code == 403
    assert client.get(path, headers=login(client, "sim.reviewer.akpsun")).status_code == 403
    assert client.get(path, headers=login(client, "sim.admin")).status_code == 403

    body = client.get(path, headers=login(client, "sim.coordinator")).json()
    assert body["meta"]["dataLabel"] == "MENTOR_PROVIDED_DRAFT"
    assert body["meta"]["runtimeEligibility"] == "BLOCKED"
    assert body["data"]["activationStatus"] == "EXCLUDED_FROM_RUNTIME"
    assert len(body["data"]["cases"]) == 8
    assert all(case["runtimeEligibility"] == "BLOCKED" for case in body["data"]["cases"])


def test_glossary_intake_requires_review_and_separates_runtime_states() -> None:
    client = make_client()
    path = f"{API}/hermes/glossary-intake"

    assert client.get(path, headers=login(client, "sim.staff.pppsun")).status_code == 403
    assert client.get(path, headers=login(client, "sim.reviewer.akpsun")).status_code == 403
    body = client.get(path, headers=login(client, "sim.coordinator")).json()
    assert body["meta"]["dataLabel"] == "CONTROLLED_GLOSSARY_DRAFT"
    assert body["meta"]["runtimeEligibility"] == "MIXED_PER_ENTRY"
    entries = body["data"]["entries"]
    assert len(entries) == 12
    assert sum(item["runtimeEligibility"] == "LIMITED_SPELLING_RETRY" for item in entries) == 5


def test_data_quality_and_classifications() -> None:
    client = make_client()
    issues = client.get(f"{API}/data-quality-issues",
                        headers=login(client, "sim.coordinator")).json()["data"]
    assert len(issues) == 2
    classes = client.get(f"{API}/classifications",
                         headers=login(client, "sim.readonly.dhtv")).json()["data"]
    assert [c["code"] for c in classes] == ["PUBLIC", "INTERNAL", "RESTRICTED", "CONFIDENTIAL"]


def test_pagination_meta_and_bounds() -> None:
    client = make_client()
    admin = login(client, "sim.admin")
    body = client.get(f"{API}/users?page=1&pageSize=3", headers=admin).json()
    assert body["meta"] == {"dataLabel": "SIMULATED_DATA", "page": 1, "pageSize": 3,
                            "total": 8, "totalPages": 3}
    assert client.get(f"{API}/users?pageSize=500", headers=admin).status_code == 422


def test_search_returns_only_authorized_published_entries() -> None:
    client = make_client()
    staff = login(client, "sim.staff.pppsun")
    hits = client.get(f"{API}/search?q=close out note", headers=staff).json()["data"]
    assert hits == []
    owner_hits = client.get(f"{API}/search?q=close out note",
                            headers=login(client, "sim.owner.ppsun")).json()["data"]
    assert owner_hits[0]["title"].startswith("SIMULASI - Playbook")
