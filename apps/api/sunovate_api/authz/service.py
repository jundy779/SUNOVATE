"""AuthorizationService: permission AND team scope AND data classification.

Deny by default. Enforced in the API for every protected endpoint (ADR-006).
The repository may narrow candidates (`ReadScope`), but every returned record still
passes `can_read` here, for every backend.
"""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from ..core.errors import permission_denied, unauthenticated
from ..store.records import DocumentReference, Governed, KnowledgeEntry
from ..store.repository import ReadScope, Repository
from .principal import Principal


class AuthorizationService:
    def __init__(self, store: Repository) -> None:
        self._store = store

    # Principal resolution ----------------------------------------------------

    def principal_for(self, user_id: UUID) -> Principal:
        facts = self._store.principal_facts(user_id)
        if facts is None or facts.user.status != "ACTIVE":
            raise unauthenticated("Pengguna tidak aktif atau tidak dikenal")
        user = facts.user
        return Principal(
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            role_codes=facts.role_codes,
            permissions=facts.permission_codes,
            team_ids=facts.team_ids,
            clearance_code=user.clearance_code,
        )

    # Rules -------------------------------------------------------------------

    def classification_allowed(self, clearance: str, classification: str) -> bool:
        clearance_rank = self._store.classification_rank(clearance)
        record_rank = self._store.classification_rank(classification)
        if clearance_rank is None or record_rank is None:
            return False  # unknown classification -> deny
        return clearance_rank >= record_rank

    def team_in_scope(self, principal: Principal, team_id: UUID) -> bool:
        return principal.all_teams or team_id in principal.team_ids

    def can_read(self, principal: Principal, record: Governed) -> bool:
        if record.deleted_at is not None:
            return False
        if not self.classification_allowed(principal.clearance_code, record.classification_code):
            return False
        return self.team_in_scope(principal, record.owner_team_id) or record.is_directorate_shared()

    def can_write(self, principal: Principal, record: Governed) -> bool:
        """Writes never use directorate sharing: the owner team must be in scope."""
        return (
            record.deleted_at is None
            and self.classification_allowed(principal.clearance_code, record.classification_code)
            and self.team_in_scope(principal, record.owner_team_id)
        )

    # Read narrowing ----------------------------------------------------------

    def read_scope(
        self,
        principal: Principal,
        kind: type[Governed],
        *,
        max_classification: str | None = None,
    ) -> ReadScope:
        """Narrowing hint matching `can_read` (design 6.2) with the 6.3 document exception."""
        clearance_rank = self._store.classification_rank(principal.clearance_code)
        ceiling_rank = (
            self._store.classification_rank(max_classification)
            if max_classification is not None
            else None
        )
        codes: frozenset[str]
        if clearance_rank is None or (max_classification is not None and ceiling_rank is None):
            codes = frozenset()  # unknown rank -> deny, like classification_allowed
        else:
            limit = clearance_rank if ceiling_rank is None else min(clearance_rank, ceiling_rank)
            codes = frozenset(c.code for c in self._store.classifications() if c.rank <= limit)
        if kind is DocumentReference:
            # Documents are also readable through a readable parent knowledge entry.
            return ReadScope(codes, None, False)
        return ReadScope(
            classification_codes=codes,
            team_ids=None if principal.all_teams else principal.team_ids,
            include_directorate_published=kind is KnowledgeEntry,
        )

    def list_readable[G: Governed](
        self,
        principal: Principal,
        kind: type[G],
        *,
        where: Mapping[str, object] | None = None,
        max_classification: str | None = None,
    ) -> list[G]:
        scope = self.read_scope(principal, kind, max_classification=max_classification)
        records = self._store.list_governed(kind, scope=scope, where=where)
        readable = [r for r in records if self.can_read(principal, r)]
        if max_classification is not None:
            readable = [
                r
                for r in readable
                if self.classification_allowed(max_classification, r.classification_code)
            ]
        return readable

    # Enforcement -------------------------------------------------------------

    def require(self, principal: Principal, *permissions: str, resource: str) -> None:
        missing = [p for p in permissions if not principal.has(p)]
        if missing:
            self._store.audit_denial(
                actor_user_id=principal.user_id,
                action="ACCESS_DENIED",
                entity_type=resource,
                detail={"missingPermissions": missing},
            )
            raise permission_denied()

    def deny_write(self, principal: Principal, record: Governed, resource: str) -> None:
        self._store.audit_denial(
            actor_user_id=principal.user_id,
            action="ACCESS_DENIED",
            entity_type=resource,
            entity_id=record.id,
            detail={"reason": "scope_or_classification"},
        )
        raise permission_denied("Data berada di luar cakupan tim atau klasifikasi Anda")
