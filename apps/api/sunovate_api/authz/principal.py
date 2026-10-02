"""Authenticated principal resolved from the store for each request."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

ALL_TEAMS = "scope:all_teams"


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    email: str
    display_name: str
    role_codes: frozenset[str]
    permissions: frozenset[str]
    team_ids: frozenset[UUID]
    clearance_code: str

    def has(self, permission: str) -> bool:
        return permission in self.permissions

    @property
    def all_teams(self) -> bool:
        return ALL_TEAMS in self.permissions
