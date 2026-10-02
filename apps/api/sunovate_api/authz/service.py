"""AuthorizationService: permission AND team scope AND data classification.

Deny by default. Enforced in the API for every protected endpoint (ADR-006).
"""

from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from ..core.errors import permission_denied, unauthenticated
from ..store.records import Governed
from ..store.simulated import SimulatedStore
from .principal import Principal


class AuthorizationService:
    def __init__(self, store: SimulatedStore) -> None:
        self._store = store

    # Principal resolution ----------------------------------------------------

    def principal_for(self, user_id: UUID) -> Principal:
        user = self._store.users.get(user_id)
        if user is None or user.status != "ACTIVE":
            raise unauthenticated("Pengguna tidak aktif atau tidak dikenal")
        role_ids = {ur.role_id for ur in self._store.user_roles if ur.user_id == user_id}
        permission_ids: set[UUID] = set()
        for role_id in role_ids:
            permission_ids |= self._store.role_permissions.get(role_id, set())
        return Principal(
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            role_codes=frozenset(self._store.roles[r].code for r in role_ids),
            permissions=frozenset(self._store.permissions[p].code for p in permission_ids),
            team_ids=frozenset(m.team_id for m in self._store.memberships if m.user_id == user_id),
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

    def readable[G: Governed](self, principal: Principal, records: Iterable[G]) -> list[G]:
        return [r for r in records if self.can_read(principal, r)]

    # Enforcement -------------------------------------------------------------

    def require(self, principal: Principal, *permissions: str, resource: str) -> None:
        missing = [p for p in permissions if not principal.has(p)]
        if missing:
            self._store.audit(
                actor_user_id=principal.user_id,
                action="ACCESS_DENIED",
                entity_type=resource,
                outcome="DENIED",
                detail={"missingPermissions": missing},
            )
            raise permission_denied()

    def deny_write(self, principal: Principal, record: Governed, resource: str) -> None:
        self._store.audit(
            actor_user_id=principal.user_id,
            action="ACCESS_DENIED",
            entity_type=resource,
            entity_id=record.id,
            outcome="DENIED",
            detail={"reason": "scope_or_classification"},
        )
        raise permission_denied("Data berada di luar cakupan tim atau klasifikasi Anda")
