"""AuthorizationService over Repository: SQL narrowing is a hint, can_read stays final.

The fake repository ignores the scope it receives and returns everything, like a
narrowing predicate that is too wide. list_readable must still filter (AC-02.4).
"""

from collections.abc import Mapping, Sequence
from typing import Any, cast

import pytest

from sunovate_api.authz.principal import ALL_TEAMS, Principal
from sunovate_api.authz.service import AuthorizationService
from sunovate_api.store.dataset import SEED_TIME, build_dataset, sid
from sunovate_api.store.records import (
    DataClassification,
    DocumentReference,
    Governed,
    KnowledgeEntry,
    Task,
)
from sunovate_api.store.repository import ReadScope, Repository

PPPSUN = sid("team:PPPSUN")
PSUN = sid("team:PSUN")


class FakeRepository:
    def __init__(self, records: Sequence[Governed]) -> None:
        self._records = list(records)
        self._classifications = build_dataset().classifications
        self.scopes: list[ReadScope | None] = []

    def classifications(self) -> list[DataClassification]:
        return sorted(self._classifications, key=lambda c: c.rank)

    def classification_rank(self, code: str) -> int | None:
        return next((c.rank for c in self._classifications if c.code == code), None)

    def list_governed(
        self,
        kind: type[Governed],
        *,
        scope: ReadScope | None = None,
        where: Mapping[str, object] | None = None,
    ) -> list[Governed]:
        self.scopes.append(scope)  # recorded, deliberately not applied
        return [r for r in self._records if isinstance(r, kind)]


def _principal(*, clearance: str = "INTERNAL", all_teams: bool = False) -> Principal:
    return Principal(
        user_id=sid("user:sim.staff.pppsun"),
        email="sim.staff.pppsun@sunovate.local",
        display_name="Staf Simulasi PPPSUN",
        role_codes=frozenset({"staff"}),
        permissions=frozenset({"knowledge:read", *([ALL_TEAMS] if all_teams else [])}),
        team_ids=frozenset({PPPSUN}),
        clearance_code=clearance,
    )


def _knowledge(title: str, **overrides: Any) -> KnowledgeEntry:
    values: dict[str, Any] = {
        "title": title,
        "knowledge_type": "SOP",
        "summary": "Ringkasan simulasi uji otorisasi.",
        "owner_team_id": PPPSUN,
        "classification_code": "INTERNAL",
        "lifecycle_status": "PUBLISHED",
        "created_at": SEED_TIME,
        "updated_at": SEED_TIME,
    }
    values.update(overrides)
    return KnowledgeEntry(**values)


def _service(records: Sequence[Governed]) -> tuple[AuthorizationService, FakeRepository]:
    fake = FakeRepository(records)
    return AuthorizationService(cast(Repository, fake)), fake


def test_list_readable_filters_records_a_wide_scope_returned() -> None:
    own = _knowledge("SIMULASI - Milik tim sendiri")
    other_team = _knowledge("SIMULASI - Tim lain", owner_team_id=PSUN)
    shared = _knowledge("SIMULASI - Dibagikan", owner_team_id=PSUN, sharing_scope="DIRECTORATE")
    confidential = _knowledge("SIMULASI - Sangat terbatas", classification_code="CONFIDENTIAL")
    deleted = _knowledge("SIMULASI - Terhapus", deleted_at=SEED_TIME)
    unknown_cls = _knowledge("SIMULASI - Klasifikasi asing", classification_code="SECRET")
    authz, fake = _service([own, other_team, shared, confidential, deleted, unknown_cls])

    readable = authz.list_readable(_principal(), KnowledgeEntry)

    assert [e.id for e in readable] == [own.id, shared.id]
    assert fake.scopes and fake.scopes[0] is not None


def test_list_readable_applies_hermes_ceiling() -> None:
    internal = _knowledge("SIMULASI - Internal")
    restricted = _knowledge("SIMULASI - Terbatas", classification_code="RESTRICTED")
    authz, _ = _service([internal, restricted])
    principal = _principal(clearance="RESTRICTED")

    assert len(authz.list_readable(principal, KnowledgeEntry)) == 2
    capped = authz.list_readable(principal, KnowledgeEntry, max_classification="INTERNAL")
    assert [e.id for e in capped] == [internal.id]


def test_read_scope_staff_knowledge() -> None:
    authz, _ = _service([])
    scope = authz.read_scope(_principal(), KnowledgeEntry)
    assert scope == ReadScope(frozenset({"PUBLIC", "INTERNAL"}), frozenset({PPPSUN}), True)


def test_read_scope_non_knowledge_has_no_directorate_branch() -> None:
    authz, _ = _service([])
    scope = authz.read_scope(_principal(), Task)
    assert scope == ReadScope(frozenset({"PUBLIC", "INTERNAL"}), frozenset({PPPSUN}), False)


def test_read_scope_all_teams_has_no_team_predicate() -> None:
    authz, _ = _service([])
    scope = authz.read_scope(_principal(clearance="RESTRICTED", all_teams=True), KnowledgeEntry)
    assert scope.team_ids is None
    assert scope.classification_codes == frozenset({"PUBLIC", "INTERNAL", "RESTRICTED"})


def test_read_scope_ceiling_is_the_lower_rank() -> None:
    authz, _ = _service([])
    scope = authz.read_scope(
        _principal(clearance="RESTRICTED"), KnowledgeEntry, max_classification="INTERNAL"
    )
    assert scope.classification_codes == frozenset({"PUBLIC", "INTERNAL"})


@pytest.mark.parametrize(
    ("clearance", "ceiling"), [("UNKNOWN", None), ("INTERNAL", "UNKNOWN")]
)
def test_read_scope_unknown_rank_denies_every_classification(
    clearance: str, ceiling: str | None
) -> None:
    authz, _ = _service([])
    scope = authz.read_scope(
        _principal(clearance=clearance), KnowledgeEntry, max_classification=ceiling
    )
    assert scope.classification_codes == frozenset()


def test_read_scope_documents_skip_team_predicate() -> None:
    """Documents may be readable through a readable parent entry (design 6.3)."""
    authz, _ = _service([])
    scope = authz.read_scope(_principal(), DocumentReference)
    assert scope == ReadScope(frozenset({"PUBLIC", "INTERNAL"}), None, False)
