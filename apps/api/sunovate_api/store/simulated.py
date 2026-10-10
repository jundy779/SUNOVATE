"""In-memory runtime store (DATA_BACKEND=simulated), an implementation of `Repository`.

Not persistent: every process restart reloads the SIMULATED_DATA dataset.
All storage is private to this file; callers use the `Repository` methods only.
"""

from __future__ import annotations

import threading
from collections.abc import Collection, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any, cast
from uuid import UUID

from ..core.config import DataBackendName
from ..core.errors import invalid_state, not_found, revision_conflict
from ..core.logging import request_id_var
from .dataset import Dataset, build_dataset
from .records import (
    AiCitation,
    AiConversation,
    AiFeedback,
    AiMessage,
    ApprovalRequest,
    AuditLog,
    DataClassification,
    DataQualityIssue,
    DocumentChunk,
    DocumentReference,
    DocumentVersion,
    FollowUp,
    Governed,
    KnowledgeEntry,
    Milestone,
    PendingMatter,
    Permission,
    Record,
    Role,
    Task,
    Team,
    TeamMembership,
    User,
    UserRole,
    WorkOutput,
    utcnow,
)
from .repository import PrincipalFacts, ReadScope, check_fields

# Governed kind -> name of the private dict holding it.
_GOVERNED: dict[type[Governed], str] = {
    KnowledgeEntry: "_knowledge",
    DocumentReference: "_documents",
    WorkOutput: "_work_outputs",
    Task: "_tasks",
    Milestone: "_milestones",
    PendingMatter: "_pending_matters",
    FollowUp: "_follow_ups",
    ApprovalRequest: "_approvals",
    DataQualityIssue: "_data_quality_issues",
}


def _index[R: Record](items: Iterable[R]) -> dict[UUID, R]:
    return {item.id: item for item in items}


def _natural[R: Record](items: Iterable[R]) -> list[R]:
    """Natural order shared by every backend: (created_at, id) ascending."""
    return sorted(items, key=lambda r: (r.created_at, r.id))


class SimulatedStore:
    def __init__(self, dataset: Dataset | None = None) -> None:
        ds = dataset or build_dataset()
        self.lock = threading.RLock()  # used only by transaction() and snapshots
        self._tx = threading.local()  # transaction depth per thread
        self._classifications: dict[str, DataClassification] = {
            c.code: c for c in ds.classifications
        }
        self._teams: dict[UUID, Team] = _index(ds.teams)
        self._roles: dict[UUID, Role] = _index(ds.roles)
        self._permissions: dict[UUID, Permission] = _index(ds.permissions)
        self._role_permissions: dict[UUID, set[UUID]] = {}
        for role_id, perm_id in ds.role_permissions:
            self._role_permissions.setdefault(role_id, set()).add(perm_id)
        self._users: dict[UUID, User] = _index(ds.users)
        self._memberships: list[TeamMembership] = list(ds.memberships)
        self._user_roles: list[UserRole] = list(ds.user_roles)
        self._knowledge: dict[UUID, KnowledgeEntry] = _index(ds.knowledge)
        self._documents: dict[UUID, DocumentReference] = _index(ds.documents)
        self._versions: dict[UUID, DocumentVersion] = _index(ds.versions)
        self._chunks: dict[UUID, DocumentChunk] = _index(ds.chunks)
        self._work_outputs: dict[UUID, WorkOutput] = _index(ds.work_outputs)
        self._tasks: dict[UUID, Task] = _index(ds.tasks)
        self._milestones: dict[UUID, Milestone] = _index(ds.milestones)
        self._pending_matters: dict[UUID, PendingMatter] = _index(ds.pending_matters)
        self._follow_ups: dict[UUID, FollowUp] = _index(ds.follow_ups)
        self._approvals: dict[UUID, ApprovalRequest] = _index(ds.approvals)
        self._data_quality_issues: dict[UUID, DataQualityIssue] = _index(ds.data_quality_issues)
        self._audit_logs: list[AuditLog] = list(ds.audit_logs)
        self._conversations: dict[UUID, AiConversation] = {}
        self._messages: dict[UUID, AiMessage] = {}
        self._citations: list[AiCitation] = []
        self._feedback: list[AiFeedback] = []

    # Transactions ------------------------------------------------------------

    def _depth(self) -> int:
        return cast(int, getattr(self._tx, "depth", 0))

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Reentrant; holds the store lock. No rollback (in-memory, current behavior)."""
        with self.lock:
            self._tx.depth = self._depth() + 1
            try:
                yield
            finally:
                self._tx.depth = self._depth() - 1

    def _require_transaction(self) -> None:
        if self._depth() == 0:
            raise RuntimeError("write di luar transaction()")

    def _governed[G: Governed](self, kind: type[G]) -> dict[UUID, G]:
        attribute = _GOVERNED.get(kind)
        if attribute is None:
            raise TypeError(f"Jenis record tidak didukung: {kind.__name__}")
        return cast(dict[UUID, G], getattr(self, attribute))

    # Reference data and identity ---------------------------------------------

    def classifications(self) -> list[DataClassification]:
        with self.lock:
            values = list(self._classifications.values())
        return sorted(values, key=lambda c: c.rank)

    def classification_rank(self, code: str) -> int | None:
        item = self._classifications.get(code)
        return item.rank if item else None

    def teams(self) -> list[Team]:
        with self.lock:
            values = list(self._teams.values())
        return _natural(values)

    def team(self, team_id: UUID) -> Team | None:
        return self._teams.get(team_id)

    def team_code(self, team_id: UUID | None) -> str | None:
        team = self._teams.get(team_id) if team_id else None
        return team.code if team else None

    def users(self) -> list[User]:
        with self.lock:
            values = list(self._users.values())
        return _natural(values)

    def user(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def user_by_email(self, email: str) -> User | None:
        wanted = email.strip().lower()
        return next((u for u in self.users() if u.email == wanted), None)

    def principal_facts(self, user_id: UUID) -> PrincipalFacts | None:
        with self.lock:
            user = self._users.get(user_id)
            if user is None:
                return None
            role_ids = {ur.role_id for ur in self._user_roles if ur.user_id == user_id}
            permission_ids: set[UUID] = set()
            for role_id in role_ids:
                permission_ids |= self._role_permissions.get(role_id, set())
            return PrincipalFacts(
                user=user,
                role_codes=frozenset(self._roles[r].code for r in role_ids),
                permission_codes=frozenset(self._permissions[p].code for p in permission_ids),
                team_ids=frozenset(m.team_id for m in self._memberships if m.user_id == user_id),
            )

    def roles(self) -> list[Role]:
        with self.lock:
            values = list(self._roles.values())
        return _natural(values)

    def permissions(self) -> list[Permission]:
        with self.lock:
            values = list(self._permissions.values())
        return _natural(values)

    def permission_codes_by_role(self) -> dict[UUID, frozenset[str]]:
        with self.lock:
            return {
                role_id: frozenset(self._permissions[p].code for p in perm_ids)
                for role_id, perm_ids in self._role_permissions.items()
            }

    def role_codes_by_user(self) -> dict[UUID, frozenset[str]]:
        with self.lock:
            pairs = [(ur.user_id, self._roles[ur.role_id].code) for ur in self._user_roles]
        result: dict[UUID, set[str]] = {}
        for user_id, code in pairs:
            result.setdefault(user_id, set()).add(code)
        return {user_id: frozenset(codes) for user_id, codes in result.items()}

    def team_ids_by_user(self) -> dict[UUID, frozenset[UUID]]:
        with self.lock:
            pairs = [(m.user_id, m.team_id) for m in self._memberships]
        result: dict[UUID, set[UUID]] = {}
        for user_id, team_id in pairs:
            result.setdefault(user_id, set()).add(team_id)
        return {user_id: frozenset(ids) for user_id, ids in result.items()}

    # Governed records --------------------------------------------------------

    def get_governed[G: Governed](self, kind: type[G], record_id: UUID) -> G | None:
        return self._governed(kind).get(record_id)

    def get_governed_many[G: Governed](
        self, kind: type[G], ids: Collection[UUID]
    ) -> dict[UUID, G]:
        if not ids:
            return {}
        items = self._governed(kind)
        with self.lock:
            return {i: items[i] for i in ids if i in items}

    def list_governed[G: Governed](
        self,
        kind: type[G],
        *,
        scope: ReadScope | None = None,  # ignored: the Python authorization check is final
        where: Mapping[str, object] | None = None,
    ) -> list[G]:
        conditions = dict(where or {})
        check_fields(kind, conditions, for_update=False)
        items = self._governed(kind)
        with self.lock:
            values = list(items.values())
        selected = [
            r
            for r in values
            if all(
                getattr(r, name) is None if expected is None else getattr(r, name) == expected
                for name, expected in conditions.items()
            )
        ]
        return _natural(selected)

    # Documents and chunks ----------------------------------------------------

    def versions_of(self, document_id: UUID) -> list[DocumentVersion]:
        with self.lock:
            values = list(self._versions.values())
        return _natural(v for v in values if v.document_reference_id == document_id)

    def chunks_of_entry(self, entry_id: UUID) -> list[DocumentChunk]:
        return self.chunks_of_entries([entry_id]).get(entry_id, [])

    def chunks_of_entries(self, entry_ids: Sequence[UUID]) -> dict[UUID, list[DocumentChunk]]:
        """Chunks of the current version of each entry's non-deleted documents."""
        if not entry_ids:
            return {}
        wanted = set(entry_ids)
        with self.lock:
            documents = list(self._documents.values())
            chunks = list(self._chunks.values())
        current: dict[UUID, set[UUID | None]] = {}
        for doc in documents:
            entry_id = doc.knowledge_entry_id
            if entry_id is not None and entry_id in wanted and doc.deleted_at is None:
                current.setdefault(entry_id, set()).add(doc.current_version_id)
        grouped: dict[UUID, list[DocumentChunk]] = {}
        for chunk in chunks:
            if chunk.document_version_id in current.get(chunk.knowledge_entry_id, set()):
                grouped.setdefault(chunk.knowledge_entry_id, []).append(chunk)
        return {
            entry_id: sorted(items, key=lambda c: (c.chunk_index, c.created_at, c.id))
            for entry_id, items in grouped.items()
        }

    # Hermes ------------------------------------------------------------------

    def conversation(self, conversation_id: UUID) -> AiConversation | None:
        return self._conversations.get(conversation_id)

    def message(self, message_id: UUID) -> AiMessage | None:
        return self._messages.get(message_id)

    # Append-only audit -------------------------------------------------------

    def audit_logs(self, action: str | None = None) -> list[AuditLog]:
        with self.lock:
            logs = list(reversed(self._audit_logs))
        if action:
            logs = [entry for entry in logs if entry.action == action]
        return logs

    def audit(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        outcome: str = "SUCCESS",
        detail: dict[str, Any] | None = None,
    ) -> AuditLog:
        now = utcnow()
        entry = AuditLog(
            occurred_at=now,
            created_at=now,
            updated_at=now,
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome=outcome,
            request_id=request_id_var.get(),
            detail=detail or {},
        )
        with self.transaction():  # joins an open transaction, else commits immediately
            self._audit_logs.append(entry)
        return entry

    def audit_denial(
        self,
        *,
        actor_user_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: UUID | None = None,
        detail: dict[str, Any] | None = None,
    ) -> AuditLog:
        return self.audit(
            actor_user_id=actor_user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            outcome="DENIED",
            dgЭvтЪ$z{-®йЬjЧќВ€K\Y]\О€ЊН\™[NВ€K\ЪYЭО€\њ™ШЉHМHЌ€И	JNВџB‚Љ€И›Ю\Ъ^љ[™О€›Ь™\‹X›ЮИBЋЋњЩ[XЭ[Ы€ИXЪЩЬ›Э[™€\ЉKYЫЫ
NИЫЫЬЋ€\ЉK[]ћKYY\
NИBљ[ИЫЫЬ‹\ШЪ[YN€YЪИШЬ›ЫX™Z]љ[ЬЋ€Ы[ЫЭИB›ЩHИX\™Ъ[Ћ€ИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]ћKYY\
NИ›Ыќ€MМKЌMH\ЉKY›ЫќX›ЩJNИBHИЫЫЬЋ€[љ\љ]И^YXЫЬ][ЫЋ€›Ы™NИBќ]Ы‹[њ]Щ[XЭ^\™XHИ›Ыќ€[љ\љ]ИBќ]Ы€ИЭ\њЫЬЋ€Ъ[ќ\ЋИBљ[њ]Щ[XЭ^\™XHИЫЫЬЋ€\ЉK[]ћKYY\
NИBЋ™›ШЭ\Л]љ\ЪX›HИЭ][™N€ЬЫЫY\ЉK[]ћJNИЭ][™K[Щ™њЩ]€њИBљK‹ЛИЭ™\™›ЭЛ]Ь\€[ћ]Ъ\™NИBљK‹ИИЫЫЬЋ€\ЉK[]ћJNИ›ЫќY[Z[N€\ЉKY›ЫќZXY[™КNИ[™KZZYЪ€KЊЋИB‹њЬ‹[Ы›HИЬЪ][ЫЋ€XњЫЫ]NИЪY€\ИZYЪ€\ИY[™О€ИX\™Ъ[Ћ€L\ИЭ™\™›ЭО€Y[ЋИЫ\€™XЭ

NИЪ]K\ЬXЩN€›ЭЬ\И›Ь™\Ћ€ИB‹њЪЪ\[[љИИЬЪ][ЫЋ€љ^YИYќ€\™[NИЬ€M™[NИ‹Z[™^€LИXЪЩЬ›Э[™€\ЉK]Ъ]JNИЫЫЬЋ€\ЉK[]ћJNИY[™О€ЌЌ\™[HЋ\™[NИ›Ь™\Ћ€њЫЫY\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИB‹њЪЪ\[[љО™›ШЭ\ИИЬ€\™[NИB‹›]]YИЫЫЬЋ€\ЉK[]]Y
NИB‚‹К€X›XИ[™[™ИYЩH
‹В‹›[™[™ИИZ[‹ZZYЪ€LљИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹њX›XЛZXY\€ИZ[‹ZZYЪ€LњИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€њ™[NИY[™О€ЌН\™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹њX›XЛXњ[™И\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€\™[NИЫЫЬЋ€\ЉK[]ћJNИB‹њX›XЛXњ[™€[YИИЪY€LОИZYЪ€]]ОИB‹њ[™Y]љY\€И[YЫ‹\Щ[Ћ€Э™]ЪИЪY€\ИZ[‹ZZYЪ€њИXЪЩЬ›Э[™€\ЉK[[™JNИB‹њ›ЩXЭ]ЫЬ™X\љИИ\Ь^N€ЬљYИШ\€ЊЬ™[NИB‹њ›ЩXЭ]ЫЬ™X\љИЭ›Ы™ИИ›Ыќ€МKЊњ™[KМH\ЉKY›ЫќZXY[™КNИ]\‹\ЬXЪ[™О€ЊY[NИB‹њ›ЩXЭ]ЫЬ™X\љИЫX[ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЋ™[NИ]\‹\ЬXЪ[™О€ЊНY[NИB‹›[™[™ЛZ\›ИИZ[‹ZZYЪ€ЊЊИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
KЌњЉHZ[›X^
МЊЌЩњЉNИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ы[\
њ™[K]ќЛ\™[JNИY[™О€Ы[\
KЊЌ\™[K]ќЛKЌ\™[JNИXЪЩЬ›Э[™€\ЉK\\\ЉNИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹љ\›ЛXЫЬHИX^]ЪY€ОLИY[™О€KЌ\™[HИB‹™^YXњ›ЭИИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌМњ™[NИ›Ыќ]ЩZYЪ€МИ]\‹\ЬXЪ[™О€ЊY[NИ^][њЩ›Ь›N€\\Ш\ЩNИB‹љ\›ЛXЫЬHHИX\™Ъ[Ћ€KЊM\™[HKЊЌ\™[NИX^]ЪY€NЪИ›Ыќ\Ъ^™N€Ы[\
‹ЌM\™[KЌ]ќЛЊњ™[JNИ›Ыќ]ЩZYЪ€ЌLИ]\‹\ЬXЪ[™О€KЊ[NИB‹љ\›Л[YHИX^]ЪY€ЌЪИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€KЊ™[NИ[™KZZYЪ€KЌОИB‹љ\›ЛXXЭ[ЫњИИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€KЌ™[NИX\™Ъ[‹]Ь€њ™[NИB‹ќ^[[љЛњЩXЭ[Ы‹ZXY[™ИKXЭ[Ы‹[[љИИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИ^YXЫЬ][ЫЋ€[™\›[™NИ^YXЫЬ][Ы‹XЫЫЬЋ€\ЉKYЫЫ
NИ^YXЫЬ][Ы‹]XЪЫ™\ЬО€њИ^][™\›[™K[Щ™њЩ]€ЊЌY[NИB‹љ\›Л\Э][Y[ќИЬЪ][ЫЋ€™[]]™NИZ[‹ZZYЪ€МИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИY[™О€Ы[\
њ™[KќЛЬ™[JNИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИ›Ю\ЪYЭО€MM™ШЉЊHMЊ€ОHИN	JNИЭ™\™›ЭО€Y[ЋИB‹љ\›Л\Э][Y[ќЋYќ\€ИЫЫќ[ќ€€ЋИЬЪ][ЫЋ€XњЫЫ]NИ[њЩ]€]]ИИZYЪ€њИXЪЩЬ›Э[™€\ЉKYЫЫ
NИB‹њЭ][Y[ќ]Ь[™HИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€\™[NИЫЫЬЋ€\ЉK[[™JNИ›Ыќ\Ъ^™N€ЌЬ™[NИ›Ыќ]ЩZYЪ€МИ]\‹\ЬXЪ[™О€ЊY[NИ^][њЩ›Ь›N€\\Ш\ЩNИB‹љ\›Л\Э][Y[ќњЭ][Y[ќZ[™^ИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ€МЌО™[KМH\ЉKY›ЫќZXY[™КNИ]\‹\ЬXЪ[™О€ЊL™[NИB‹љ\›Л\Э][Y[ќ›ШЪЬ][ЭHИX^]ЪY€MШЪИX\™Ъ[Ћ€]]ИИ›Ыќ€LЫ[\
KЌ\™[K‹ЊќќЛ‹Њ\™[JKМKЊО\ЉKY›ЫќZXY[™КNИB‹љ\›Л\Э][Y[ќИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[[™JNИ›Ыќ\Ъ^™N€ЌО™[NИB‹Ш\Xљ[]K\ЩXЭ[Ы€И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
ЌЊЌЩњЉHZ[›X^
KЊЩњЉNИШ\€Ы[\
Ь™[KќЛ™[JNИY[™О€њ™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИB‹њЩXЭ[Ы‹Z[ќ›И€ИX^]ЪY€MЪИX\™Ъ[Ћ€Ћ™[H\™[NИ›Ыќ\Ъ^™N€њ™[NИB‹њЩXЭ[Ы‹Z[ќ›И€›\ЭXЪ[ИX^]ЪY€ЪИЫЫЬЋ€\ЉK[]]Y
NИB‹Ш\Xљ[]K[\ЭИ›Ь™\‹]Ь€њЫЫY\ЉK[]ћJNИB‹Ш\Xљ[]K[\Э\ќXЫHИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€ЛЌ\™[HYњЋИШ\€KЊЌ\™[NИY[™О€KЌњ™[HИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹Ш\Xљ[]K[\Э\ќXЫH€Ь[€ИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ]ЩZYЪ€МИB‹Ш\Xљ[]K[\ЭИИX\™Ъ[Ћ€ЊН\™[NИ›Ыќ\Ъ^™N€\™[NИB‹Ш\Xљ[]K[\ЭИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИB‹њX›XЛY›ЫЭ\€И\Ь^N€›^Иќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€њ™[NИY[™О€KЌ\™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИXЪЩЬ›Э[™€\ЉK[]ћKYY\
NИЫЫЬЋ€\ЉK[[™JNИ›Ыќ\Ъ^™N€ЌН\™[NИB‚‹К€[њЭ]][Ы[X›XИЬќ[Э™\њљY\И
‹В‹љ[њЭ]][Ы‹X\€ИZ[‹ZZYЪ€НњИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€KЊњ™[NИY[™О€Ќ™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ\Ъ^™N€ЌЬ™[NИ]\‹\ЬXЪ[™О€ЊMY[NИB‹љ[њЭ]][Ы‹X\€Ь[€
ИЬ[€И›Ь™\‹[Yќ€\ЫЫY™ШЉЌMHЌMHЌMHИМ‰JNИY[™Л[Yќ€KЊњ™[NИB‹љ[њЭ]][Ы‹]ЫЫИИX\™Ъ[‹[Yќ€]]ОИB‹њX›XЛZXY\€ИZ[‹ZZYЪ€ИY[™О€ЌЌ\™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹њX›XЛXњ[™€[YИИЪY€LЊњИB‹њ›ЩXЭ]ЫЬ™X\љИЭ›Ы™ИИ›Ыќ\Ъ^™N€KЊN™[NИ]\‹\ЬXЪ[™О€Њ[NИB‹њ›ЩXЭ]ЫЬ™X\љИЫX[ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌЬ™[NИ]\‹\ЬXЪ[™О€Њ™[NИB‹њX›XЛ[]€И\Ь^N€›^И[YЫ‹\Щ[Ћ€Э™]ЪИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ы[\
KЊM\™[K‹Ќ]ќЛ‹Ќњ™[JNИX\™Ъ[‹[Yќ€]]ОИB‹њX›XЛ[]€HИZYЪ€L	NИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИ›Ь™\‹X›ЭЫN€ЬЫЫY[њЬ\™[ќИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€Ћњ™[NИ›Ыќ]ЩZYЪ€МИB‹њX›XЛ[]€NљЭ™\€И›Ь™\‹X›ЭЫKXЫЫЬЋ€\ЉKYЫЫ
NИB‹њX›XЛ[ЩЪ[‹[[љИИZ[‹]ЪY€њИB‹›[™[™ЛZ\›ИИZ[‹ZZYЪ€LИЬљY][\]KXЫЫ[[њО€Z[›X^
LЋYњЉHZ[›X^
KЌYњЉNИ[YЫ‹Z][\О€Э™]ЪИШ\€ИY[™О€ИXЪЩЬ›Э[™€\ЉK[]ћJNИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉKYЫЫ
NИB‹љ\›ЛXЫЬHИ‹Z[™^€NИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИќ\ЭYћKXЫЫќ[ќ€Щ[ќ\ЋИX^]ЪY€›Ы™NИY[™О€Ќ\™[HЬ™[HЌ\™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИЫЫЬЋ€\ЉK]Ъ]JNИB‹љ\›ЛXЫЬHHИX^]ЪY€MXЪИX\™Ъ[Ћ€KЊЬ™[NИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ€ЊЫ[\
‹ЊН\™[KЛЌЌ]ќЛЛЌЌ\™[JKМKЊHЩ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИ]\‹\ЬXЪ[™О€KЊЌY[NИB‹љ\›Л[YHИX^]ЪY€MЪИЫЫЬЋ€ЩLЩNYЋИ›Ыќ\Ъ^™N€\™[NИ[™KZZYЪ€KЌМЋИB‹ќ]Ы‹ќ]Ы‹YЫЫИ›Ь™\‹XЫЫЬЋ€\ЉKYЫЫ
NИXЪЩЬ›Э[™€\ЉKYЫЫ
NИЫЫЬЋ€\ЉK[]ћJNИB‹ќ]Ы‹ќ]Ы‹YЫЫљЭ™\€И›Ь™\‹XЫЫЬЋ€ШЊОLYNИXЪЩЬ›Э[™€ШЊОLYNИB‹ќ]Ы‹ќ]Ы‹[Э][™K[YЪИ›Ь™\‹XЫЫЬЋ€™ШЉЌMHЌMHЌMHИМ‰JNИXЪЩЬ›Э[™€[њЬ\™[ќИЫЫЬЋ€\ЉK]Ъ]JNИB‹ќ]Ы‹ќ]Ы‹[Э][™K[YЪљЭ™\€ИXЪЩЬ›Э[™€\ЉK]Ъ]JNИЫЫЬЋ€\ЉK[]ћJNИB‹љ\›ЛZ[XYЩHИZ[‹ZZYЪ€LИXЪЩЬ›Э[™€\›
‹Шњ[™ЬЭ[›Э]KZ[њЭ]][Ы[Z\›ЛљњИЉHЩ[ќ\‹ШЫЭ™\€›Л\™\X]ИB‹XШЩ\ЬЛ\Z[И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€NYњЋИ[YЫ‹Z][\О€Э™]ЪИY[™О€Ы[\
KЊЌ\™[K]ќЛKЌ\™[JNИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹XШЩ\ЬЛ\Z[€€И\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИX\™Ъ[Ћ€ИY[™Л\љYЪ€њ™[NИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[[™JNИ›Ыќ€ЊKЊН\™[KМKЊ€Щ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИB‹XШЩ\ЬЛ[[љЬИИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€™\X]
Z[›X^
YњЉJNИB‹XШЩ\ЬЛ[[љЬИHИZ[‹ZZYЪ€LИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€МYњ€]]ОИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ћ™[NИY[™О€KЊЌ\™[NИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[[™JNИB‹XШЩ\ЬЛ[[љЬИN›\ЭXЪ[И›Ь™\‹\љYЪ€ИB‹XШЩ\ЬЛ[[љЬИNљЭ™\€ИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹XШЩ\ЬЛ[[љЬИЭ™ИИЪY€Ќ\ИЫЫЬЋ€\ЉK[]ћJNИB‹XШЩ\ЬЛ[[љЬИЬ[Ћ›ќXЪ[
ЉHИ\Ь^N€ЬљYИШ\€Њњ™[NИB‹XШЩ\ЬЛ[[љЬИЭ›Ы™ИИ›Ыќ\Ъ^™N€Ћњ™[NИB‹XШЩ\ЬЛ[[љЬИЫX[ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌњ™[NИ[™KZZYЪ€KЌИB‹XШЩ\ЬЛ[[љЬИH€Ь[Ћ›\ЭXЪ[ИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ\Ъ^™N€KЊM\™[NИB‹љ[њЭ]][Ы[XЫЫќ[ќИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
Ћ™њЉHZ[›X^
KЊNњЉNИШ\€Ы[\
Ь™[KЭќЛЬ™[JNИY[™О€\™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹њЩXЭ[Ы‹[X™[ИX\™Ъ[Ћ€ЌН\™[NИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ\Ъ^™N€ЌМњ™[NИ›Ыќ]ЩZYЪ€И]\‹\ЬXЪ[™О€ЊY[NИ^][њЩ›Ь›N€\\Ш\ЩNИB‹љ[њЭ]][Ы[XЫЫќ[ќ‹]]\[™[HИX\™Ъ[Ћ€И›Ыќ€ЊЫ[\
њ™[KЭќЛ‹Ћ™[JKМKЊLИЩ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИ]\‹\ЬXЪ[™О€KЊ™[NИB‹X›Э]\Э[›Э]H€››Э
њЩXЭ[Ы‹[X™[
HИX^]ЪY€ЊЪИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЋN™[NИ[™KZZYЪ€KЌНNИB‹X›Э]\Э[›Э]H›ШЪЬ][ЭHИX\™Ъ[Ћ€њ™[HИ›Ь™\‹[Yќ€ЫЫY\ЉKYЫЫ
NИY[™О€ЊН\™[HЊН\™[HKЊЬ™[NИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ€LKЊњ™[KМKЌMHЩ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИB‹™ЫЭ™\›[ЩK[›ЭHИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€НYњЋИШ\€\™[NИY[™Л]Ь€KЌ\™[NИ›Ь™\‹]Ь€\ЫЫY\ЉK[[™JNИB‹™ЫЭ™\›[ЩK[›ЭHЭ™ИИЪY€ЋИЫЫЬЋ€\ЉK\ЭXШЩ\ЬКNИB‹™ЫЭ™\›[ЩK[›ЭHЬ[€И\Ь^N€ЬљYИШ\€ЊЌ\™[NИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌО™[NИB‹™ЫЭ™\›[ЩK[›ЭHЭ›Ы™ИИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€Ћ™[NИB‹ЫЫќ[ќZXY[™ИИ\Ь^N€›^И[YЫ‹Z][\О€[™Иќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€њ™[NИY[™ЛX›ЭЫN€KЊЌ\™[NИ›Ь™\‹X›ЭЫN€њЫЫY\ЉK[]ћJNИB‹љЫ›ЭЫYЩK[\Э€]€И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€њYњЋИШ\€\™[NИY[™О€KЊЌ\™[HИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹љЫ›ЭЫYЩK[\Э€]€€Ь[€ИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ]ЩZYЪ€ИB‹љЫ›ЭЫYЩK[\ЭИИX\™Ъ[Ћ€ЊН\™[NИ›Ыќ\Ъ^™N€ЋM\™[NИB‹љЫ›ЭЫYЩK[\ЭИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌО™[NИ[™KZZYЪ€KЌMNИB‹њ›ЭЭ\K[›ЭXЩHИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€њ™[NИY[™О€KЊњ™[HЫ[\
KЊЌ\™[K]ќЛKЌ\™[JNИ›Ь™\‹]Ь€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€\ЉK\\\ЉNИ›Ыќ\Ъ^™N€ЌН\™[NИB‹њ›ЭЭ\K[›ЭXЩH]€И\Ь^N€›^ИШ\€ЌЌ\™[NИB‹њ›ЭЭ\K[›ЭXЩHЭ›Ы™ИИЫЫЬЋ€\ЉK\ЭXШЩ\ЬКNИB‹њ›ЭЭ\K[›ЭXЩHЬ[€ИЫЫЬЋ€\ЉK[]]Y
NИB‹њX›XЛY›ЫЭ\€ИZ[‹ZZYЪ€LLИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€ЌЩњ€Yњ€KЊЩњЋИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€њ™[NИB‹њX›XЛY›ЫЭ\€]€И\Ь^N€ЬљYИШ\€Њњ™[NИB‹њX›XЛY›ЫЭ\€Э›Ы™ИИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ\Ъ^™N€\™[NИ]\‹\ЬXЪ[™О€Њ[NИB‹њX›XЛY›ЫЭ\€€Ь[Ћ›\ЭXЪ[И^X[YЫЋ€љYЪИB‚‹К€Ъ\™YЫЫќ›ЫИ
‹В‹ќ]Ы€И\Ь^N€[›[™KY›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€Щ[ќ\ЋИZ[‹ZZYЪ€И›Ь™\Ћ€\ЫЫY\ЉK[]ћJNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИY[™О€ЌЌ\™[H\™[NИ›Ыќ]ЩZYЪ€МИ[њЪ][ЫЋ€XЪЩЬ›Э[™XЫЫЬ€MЊ\ИX\ЩKЫЫЬ€MЊ\ИX\ЩK[њЩ›Ь›HMЊ\ИX\ЩK›Ю\ЪYЭИMЊ\ИX\ЩNИB‹ќ]ЫЋљЭ™\€ИXЪЩЬ›Э[™€\ЉK[]ћKYY\
NИ[њЩ›Ь›N€[њЫ]VJL\
NИ›Ю\ЪYЭО€\M™ШЉLИ€MИM	JNИB‹ќ]Ы‹њЩXЫЫ™\ћHИXЪЩЬ›Э[™€\ЉK]Ъ]JNИЫЫЬЋ€\ЉK[]ћJNИB‹ќ]Ы‹њЩXЫЫ™\ћNљЭ™\€ИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹ќ]ЫЋ™\ШX›YИЬXЪ]N€ЌЋИЭ\њЫЬЋ€›ЩЬ™\ЬОИB‹ќ^Xќ]Ы€И›Ь™\Ћ€ИXЪЩЬ›Э[™€[њЬ\™[ќИЫЫЬЋ€\ЉK[]ћJNИY[™О€Ќ\™[NИ›Ыќ]ЩZYЪ€МИBљ[њ]Щ[XЭ^\™XHИ›Ь™\Ћ€\ЫЫY\ЉK[]]Y
NИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИY[™О€ЌЌ\™[HЌН\™[NИBќ^\™XHИЪY€L	NИ™\Ъ^™N€™\ќXШ[ИB‚‹К€]]
‹В‹]]\YЩHИZ[‹ZZYЪ€LљИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
НЋYњЉHZ[›X^
ЊKЊYњЉNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹]]XЫЫќ^ИZ[‹ZZYЪ€LљИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИY[™О€Ы[\
њ™[K]ќЛ\™[JNИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ь™\‹\љYЪ€њЫЫY\ЉKYЫЫ
NИB‹]]Xњ[™ИЪY€љ]XЫЫќ[ќИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€KЊ\™[NИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ€МKЊН\™[KМH\ЉKY›ЫќZXY[™КNИ]\‹\ЬXЪ[™О€Њ[NИB‹]]Xњ[™[YИИЪY€MMИZYЪ€]]ОИB‹]]Xњ[™Ь[€И›Ь™\‹[Yќ€\ЫЫY™ШЉЌMHЌMHЌMHИЋ	JNИY[™Л[Yќ€KЊ\™[NИB‹]]XЫЫќ^HИX^]ЪY€LШЪИX\™Ъ[Ћ€\™[HИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ\Ъ^™N€Ы[\
‹Њњ™[KќЛЛЋ™[JNИ›Ыќ]ЩZYЪ€ЊИ]\‹\ЬXЪ[™О€KЊНY[NИB‹]]XЫЫќ^€]€€›\ЭXЪ[ИX^]ЪY€MЪИЫЫЬЋ€\ЉK[[™JNИB‹]]XЫЫќ^™^YXњ›ЭИИЫЫЬЋ€\ЉKYЫЫ
NИB‹]]]YЫ[™HИX^]ЪY€LЪИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[[™JNИ›Ыќ\Ъ^™N€Ћ\™[NИB‹]]\[™[И\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИY[™О€њ™[NИB‹]]\[™[Z[›™\€ИЪY€Z[ЉL	K
NИB‹]]\[™[€ИX\™Ъ[Ћ€ЌЬ™[HИ›Ыќ\Ъ^™N€њ™[NИB‹]]Y›Ь›HИ\Ь^N€ЬљYИШ\€ЌM\™[NИX\™Ъ[Ћ€KЌЬ™[H\™[NИB‹]]Y›Ь›H[њ]ИЪY€L	NИB‹]]Y›Ь›HЫX[ИЫЫЬЋ€\ЉK[]]Y
NИB‹™љY[Y\њ›Ь€ИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK\љ\ЪКNИ›Ыќ]ЩZYЪ€МИB‚‹К€[њЭ]][Ы[XШЩ\ЬИYЩH
‹В‹]]\YЩHИZ[‹ZZYЪ€LљИ\Ь^N€›ШЪОИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹]][^[Э]ИZ[‹ZZYЪ€Ш[КLљHLЊ
NИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
ЋMYњЉHZ[›X^
LKЊYњЉNИB‹]]XЫЫќ^ИЬЪ][ЫЋ€™[]]™NИZ[‹ZZYЪ€ЊЊИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИY[™О€Ы[\
Ь™[KќќЛњ™[JNИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ь™\‹\љYЪ€ИЭ™\™›ЭО€Y[ЋИB‹]]XЫЫќ^ЋYќ\€ИЫЫќ[ќ€€ЋИЬЪ][ЫЋ€XњЫЫ]NИЪY€НINИ\ЬXЭ\][О€NИљYЪ€LЌ	NИ›ЭЫN€LО	NИ›Ь™\Ћ€\ЫЫY™ШЉЌMHЌMHЌMHИM‰JNИ[њЩ›Ь›N€›Э]JYYКNИ›Ю\ЪYЭО€М™ШЉЌMHЌMHЌMHИЙJKM™ШЉЌMHЌMHЌMHИ‰JNИB‹]]]ЫЬ™X\љИИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ€ЊЫ[\
‹Ћ™[K]ќЛЋ™[JKМHЩ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИ]\‹\ЬXЪ[™О€Њ[NИB‹]][Ь™Ш[љ^][Ы€ИX\™Ъ[Ћ€Ћ™[HИЫЫЬЋ€\ЉKYЫЫ
NИ›Ыќ€LKЊ\™[KМKЊИЩ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИB‹]]XЫЫќ^›ШЪЬ][ЭHИ‹Z[™^€NИX^]ЪY€NЪИX\™Ъ[Ћ€]]ИИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ€LЫ[\
KЌЌ\™[K‹ЌЭќЛ‹ЌЌ\™[JKМKЌ€Щ[Ь™ЪXK•[Y\И™]И›ЫX[€‹Щ\љYЋИB‹]]\љ[Ъ\\ИИ‹Z[™^€NИ\Ь^N€›^ИШ\€ИB‹]]\љ[Ъ\\ИЬ[€И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Ќ]]ОИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€ЌЌ\™[NИY[™О€Њњ™[HKЌ™[NИ›Ь™\‹\љYЪ€\ЫЫY™ШЉЌMHЌMHЌMHИМ	JNИЫЫЬЋ€ЩLЩNYЋИ›Ыќ\Ъ^™N€ЌНњ™[NИB‹]]\љ[Ъ\\ИЬ[Ћ™љ\њЭXЪ[ИY[™Л[Yќ€ИB‹]]\љ[Ъ\\ИЬ[Ћ›\ЭXЪ[И›Ь™\‹\љYЪ€ИB‹]]\љ[Ъ\\ИЭ™ИИЪY€ЊњИЫЫЬЋ€\ЉKYЫЫ
NИB‹]]\[™[И\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИY[™О€Ы[\
‹Ќ\™[KќќЛњ™[JNИB‹]]\[™[Z[›™\€ИЪY€Z[ЉL	KLЊ
NИB‹]]\[™[›YHИX\™Ъ[Ћ€KЊњ™[HИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЋM\™[NИ[™KZZYЪ€KЌОИB‹]]Y›Ь›HX™[ИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИB‹]]Y›Ь›Hќ]Ы€ИZ[‹ZZYЪ€ИX\™Ъ[‹]Ь€Ќњ™[NИ›Ь™\‹\Y]\О€њИB‹]]XXЪЛ[[љИИ\Ь^N€[›[™KX›ШЪОИX\™Ъ[‹]Ь€ЌН\™[NИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИ^YXЫЬ][ЫЋ€[™\›[™NИ^YXЫЬ][Ы‹XЫЫЬЋ€\ЉKYЫЫ
NИ^][™\›[™K[Щ™њЩ]€ЊЌ\™[NИB‹]]\ЩXЭ\љ]HИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€ЌЌ\™[NИX\™Ъ[‹]Ь€њ™[NИ›Ь™\‹]Ь€\ЫЫY\ЉK[[™JNИY[™Л]Ь€KЊњ™[NИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌН\™[NИB‹]]\ЩXЭ\љ]HЭ™ИИЪY€ЊИЫЫЬЋ€\ЉK[]ћJNИB‹]]\[™[™]K[X™[И\Ь^N€›ШЪОИX\™Ъ[‹]Ь€\™[NИ›Ь™\‹[Yќ€ЬЫЫY\ЉK\ЭXШЩ\ЬКNИXЪЩЬ›Э[™€ЩYЌЩЊNИY[™О€ЌЬ™[HЋ™[NИЫЫЬЋ€\ЉK\ЭXШЩ\ЬКNИ›Ыќ\Ъ^™N€ЌЋ™[NИB‚‹К€]][ќXШ]YЪ[
‹В‹\\Ъ[ИZ[‹ZZYЪ€LљИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€ЌZ[›X^
YњЉNИB‹њЪYX\€ИZ[‹ZZYЪ€LљИ[YЫ‹\Щ[Ћ€Э™]ЪИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[]ћKYY\
NИB‹њЪYX\‹Z[›™\€ИЬЪ][ЫЋ€ЭXЪЮNИЬ€ИZ[‹ZZYЪ€LљИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИB‹њ[™ИZ[‹ZZYЪ€LНњИ\Ь^N€›^И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИќ\ЭYћKXЫЫќ[ќ€Щ[ќ\ЋИ[YЫ‹Z][\О€›^\Э\ќИY[™О€KЊЌ\™[HKЌ\™[NИ›Ь™\‹X›ЭЫN€\ЫЫY™ШЉЊM€ЊЊHЊЌИИЊ‰JNИ›Ыќ€МKЊњ™[KМH\ЉKY›ЫќZXY[™КNИ]\‹\ЬXЪ[™О€ЊY[NИB‹њ[™[YИИЪY€MњИZYЪ€]]ОИX\™Ъ[‹X›ЭЫN€Ћ\™[NИB‹њ[™ЫX[И\Ь^N€›ШЪОИX^]ЪY€ЌЪИX\™Ъ[‹]Ь€Ќ\™[NИЫЫЬЋ€\ЉK[[™JNИ›Ыќ€LЌЊЬ™[KМKЊНH\ЉKY›ЫќX›ЩJNИ]\‹\ЬXЪ[™О€ЊНY[NИB‹њЪYX\€]€И\Ь^N€ЬљYИY[™О€KЊЌ\™[HЌН\™[NИШ\€Њњ™[NИB‹њЪYX\€]€HИЬЪ][ЫЋ€™[]]™NИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€ЌН\™[NИZ[‹ZZYЪ€ИY[™О€ЌЌ\™[HЋ™[NИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИЫЫЬЋ€\ЉK\\\ЉNИ[њЪ][ЫЋ€XЪЩЬ›Э[™XЫЫЬ€ML\ИX\ЩKЫЫЬ€ML\ИX\ЩK[њЩ›Ь›HML\ИX\ЩNИB‹њЪYX\€]€NљЭ™\€ИXЪЩЬ›Э[™€™ШЉЌMHЌMHЌMHИЙJNИB‹њЪYX\€]€VШ\љXKXЭ\њ™[ќHњYЩH—HИXЪЩЬ›Э[™€™ШЉЌMHЌMHЌMHИL	JNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ]ЩZYЪ€МИ[њЩ›Ь›N€[њЫ]V
њ
NИB‹›]‹[X\љЩ\€ИЪY€ЬИZYЪ€NИXЪЩЬ›Э[™€[њЬ\™[ќИB‹њЪYX\€]€VШ\љXKXЭ\њ™[ќHњYЩH—H›]‹[X\љЩ\€ИXЪЩЬ›Э[™€\ЉKYЫЫ
NИB‹›]‹ZXЫЫ€ИЪY€ЊИZYЪ€ЊИ›^€]]ОИЫЫЬЋ€\ЉK[[™JNИB‹њЪYX\€]€VШ\љXKXЭ\њ™[ќHњYЩH—H›]‹ZXЫЫ€ИЫЫЬЋ€\ЉK]Ъ]JNИB‹њЪYX\‹[›ЭHИX\™Ъ[‹]Ь€]]ОИ\Ь^N€ЬљYИШ\€ЊЋ™[NИY[™О€KЊЌ\™[HKЌ\™[NИ›Ь™\‹]Ь€\ЫЫY™ШЉЊM€ЊЊHЊЌИИЊ‰JNИЫЫЬЋ€\ЉK[[™JNИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹њЪYX\‹[›ЭHЭ›Ы™ИИЫЫЬЋ€\ЉK]Ъ]JNИB‹ќЫЬљЬЬXЩHИZ[‹]ЪY€ИB‹ќЬ\€ИZ[‹ZZYЪ€МњИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€\™[NИY[™О€ЌН\™[HЫ[\
\™[KЭќЛњ™[JNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹™ЫШ[\ЩX\ЪИЪY€Z[ЉќќЛLЊ
NИX\™Ъ[‹\љYЪ€]]ОИB‹™ЫШ[\ЩX\Ъ[њ]ИЪY€L	NИZ[‹ZZYЪ€ИY[™Л[Yќ€Ћ\™[NИ›Ь™\‹XЫЫЬЋ€\ЉK[[™JNИB‹››ЭYљXШ][Ы‹Xќ]Ы€ИЬЪ][ЫЋ€™[]]™NИЪY€ИZYЪ€И\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИ›Ь™\Ћ€И›Ь™\‹[Yќ€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€[њЬ\™[ќИЫЫЬЋ€\ЉK[]ћJNИY[™Л[Yќ€\™[NИB‹››ЭYљXШ][Ы‹Xќ]Ы€Э™ИИЪY€Њ\ИZYЪ€Њ\ИB‹››ЭYљXШ][Ы‹Xќ]Ы€Ь[€ИЬЪ][ЫЋ€XњЫЫ]NИЬ€ИљYЪ€ЬИЪY€ЬИZYЪ€ЬИ›Ь™\Ћ€\ЫЫY\ЉK]Ъ]JNИ›Ь™\‹\Y]\О€L	NИXЪЩЬ›Э[™€\ЉK\љ\ЪКNИB‹XШЫЭ[ќ[Y[ќHИЬЪ][ЫЋ€™[]]™NИB‹XШЫЭ[ќ[Y[ќH€Э[[X\ћHИ\Э\Э[N€›Ы™NИЭ\њЫЬЋ€Ъ[ќ\ЋИB‹XШЫЭ[ќ[Y[ќH€Э[[X\ћNЋ‹]ЩXљЪ]Y]Z[Л[X\љЩ\€И\Ь^N€›Ы™NИB‹ќЬ\‹XXШЫЭ[ќИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€ЌЬ™[NИZ[‹]ЪY€Ќ\ИY[™Л[Yќ€\™[NИ›Ь™\‹[Yќ€\ЫЫY\ЉK[[™JNИB‹ќЬ\‹XXШЫЭ[ќ€]Ћ››Э
ќ\Щ\‹X]]\ЉHИ\Ь^N€ЬљYИB‹ќЬ\‹XXШЫЭ[ќЬ[€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹XШЫЭ[ќXЪ]њ›Ы€ИЪY€NИZYЪ€NИX\™Ъ[‹[Yќ€]]ОИЫЫЬЋ€\ЉK[]]Y
NИB‹XШЫЭ[ќ\ЬЭ™\€ИЬЪ][ЫЋ€XњЫЫ]NИ‹Z[™^€ЊИЬ€Ш[КL	H
ИЋ\™[JNИљYЪ€ИЪY€NLИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИY[™О€ЌЌ\™[HЌН\™[NИ›Ю\ЪYЭО€LЌ™ШЉHМHЌ€ИL‰JNИB‹XШЫЭ[ќ\ЬЭ™\€€Ь[€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹ќ\Щ\‹X]]\€ИЪY€НИZYЪ€НИ\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИ›Ь™\‹\Y]\О€L	NИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИ›Ыќ]ЩZYЪ€МИB›XZ[Ћ››Э
›[™[™Л]]\YЩJHИX^]ЪY€MИX\™Ъ[Ћ€]]ОИY[™О€‹ЊЌ\™[HЫ[\
\™[KЭќЛ‹ЊЌ\™[JH™[NИB‹њYЩKZXY\€И\Ь^N€›^Иќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИ[YЫ‹Z][\О€›^\Э\ќИШ\€њ™[NИY[™ЛX›ЭЫN€KЌН\™[NИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИBљHИX\™Ъ[Ћ€Ќ™[HЌ\™[NИ›Ыќ\Ъ^™N€Ы[\
KЌЬ™[K‹ЌќЛ‹Њ\™[JNИ]\‹\ЬXЪ[™О€KЊ™[NИBљ€И›Ыќ\Ъ^™N€\™[NИB‹›YHИX^]ЪY€ОЪИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИB‚‹К€]H™\Щ[ќ][Ы€
‹В‹›Y]љXЛYЬљY›Y]љXЬИИX\™Ъ[‹]Ь€KЌ\™[NИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€™\X]
Z[›X^
YњЉJNИШ\€\И›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹]Ь€ЬЫЫY\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИЭ™\™›ЭО€Y[ЋИ›Ю\ЪYЭО€\ЉK\ЪYЭКNИB‹›Y]љXИИZ[‹ZZYЪ€‹Ќ\™[NИY[™О€KЊњ™[HKЊЬ™[NИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ь™\‹\љYЪ€И[њЪ][ЫЋ€XЪЩЬ›Э[™XЫЫЬ€ML\ИX\ЩNИB‹›Y]љXОљЭ™\€ИXЪЩЬ›Э[™€™ШЉЌИЌHЌИИMIJNИB‹›Y]љXИИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌО™[NИB‹›Y]љXИЭ›Ы™ИИ\Ь^N€›ШЪОИX\™Ъ[‹]Ь€ЌM\™[NИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ€МKЌН\™[KМH\ЉKY›ЫќZXY[™КNИB‹њ[™[][ќ[Ы‹™]K\[™[™]Z[YЬљY™[\K\Э]HИX\™Ъ[‹]Ь€KЌ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ю\ЪYЭО€N™ШЉHМHЌ€ИIJNИЭ™\™›ЭО€Y[ЋИB‹њЩXЭ[Ы‹ZXY[™Лњ[™[ZXY\€ИZ[‹ZZYЪ€NИ\Ь^N€›^Иќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€\™[NИY[™О€Ћ\™[H\™[HЋ\™[HKЊњ™[NИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИ›Ю\ЪYЭО€[њЩ]\ЉKYЫЫ
NИB‹њЩXЭ[Ы‹ZXY[™ИњЩXЭ[Ы‹ZXY[™И‹њ[™[ZXY\€€ИX\™Ъ[Ћ€ИB‹њЩXЭ[Ы‹ZXY[™И™^YXњ›ЭИИX\™Ъ[‹X›ЭЫN€ЊЌ\™[NИB‹ќX›K]Ь\ИЭ™\™›ЭЛ^€]]ОИBќX›HИЪY€L	NИZ[‹]ЪY€ЋИ›Ь™\‹XЫЫ\ЩN€ЫЫ\ЩNИBќИY[™О€ЌО™[H\™[NИ^X[YЫЋ€YќИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИ™\ќXШ[X[YЫЋ€ЬИBќИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЋ\™[NИ]\‹\ЬXЪ[™О€ЊMY[NИ^][њЩ›Ь›N€\\Ш\ЩNИЪ]K\ЬXЩN€›ЭЬ\ИBќ›ЩHЋ›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИBќ›ЩHЋљЭ™\€ИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹њЭ]\ИИ\Ь^N€[›[™KY›^И[YЫ‹Z][\О€Щ[ќ\ЋИЪY€љ]XЫЫќ[ќИ›Ь™\‹\Y]\О€NN\ИY[™О€ЊN™[HЌM\™[NИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌМЬ™[NИ›Ыќ]ЩZYЪ€МИЪ]K\ЬXЩN€›ЭЬ\ИB‹њЭ]\Л\ЭXШЩ\ЬЛњЭ]\ЛњЭXШЩ\ЬИИXЪЩЬ›Э[™€™ШЉ€LОHИИL	JNИЫЫЬЋ€\ЉK\ЭXШЩ\ЬКNИB‹њЭ]\Л\љ\ЪЛњЭ]\Лњљ\ЪИИXЪЩЬ›Э[™€™ШЉMОННИIJNИЫЫЬЋ€\ЉK\љ\ЪКNИB‹њЭ]\Л]Ш\›љ[™ИИXЪЩЬ›Э[™€™ШЉЊHMЊ€ОHИMIJNИЫЫЬЋ€\ЉK[]ћKYY\
NИB‹њЭ]\Л[™]][ИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]ћJNИB‹Ы\ЬЪYљXШ][Ы€И\Ь^N€[›[™KY›^И›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€NN\ИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]ћJNИY[™О€ЊMњ™[HЌ\™[NИ›Ыќ\Ъ^™N€ЌЬ™[NИ›Ыќ]ЩZYЪ€МИB‹™[\K\Э]HИY[™О€‹Ќ\™[H\™[NИ^X[YЫЋ€Щ[ќ\ЋИЫЫЬЋ€\ЉK[]]Y
NИB‹њ[™[™[\K\Э]HИX\™Ъ[Ћ€И›Ь™\Ћ€И›Ю\ЪYЭО€›Ы™NИB‹™[\K\Э]H€ИX\™Ъ[‹]Ь€ИB‹™]K[X™[И\Ь^N€[›[™KY›^И[YЫ‹Z][\О€Щ[ќ\ЋИZ[‹ZZYЪ€ЋИX\™Ъ[Ћ€И›Ь™\Ћ€\ЫЫY\ЉKYЫЫ
NИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИY[™О€ЊЋ™[HЌ\™[NИЫЫЬЋ€\ЉK[]ћJNИXЪЩЬ›Э[™€™ШЉЊHMЊ€ОHИЙJNИ›Ыќ\Ъ^™N€ЌЋ™[NИ›Ыќ]ЩZYЪ€МИ]\‹\ЬXЪ[™О€ЊMY[NИЪ]K\ЬXЩN€›ЭЬ\ИB‹››ЭXЩHИ\Ь^N€›ШЪОИX\™Ъ[‹]Ь€KЊЌ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹[Yќ€ЫЫY\ЉKYЫЫ
NИXЪЩЬ›Э[™€\ЉK]Ъ]JNИY[™О€Ћ™[H\™[NИB‹ќЫЛXЫЫ[[€И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
KЊњЉHZ[›X^
ЋL™њЉNИШ\€KЌ\™[NИB‹›\ЭИ\Э\Э[N€›Ы™NИX\™Ъ[Ћ€ИY[™О€ИB‹›\ЭHИ\Ь^N€ЬљYИШ\€ЊЊњ™[NИY[™О€Ћ\™[H\™[NИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹›\ЭN›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИB‹›\ЭHЬ[€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌО™[NИB‹›\ЭKњ™\Э[ИKЪ]][ЫњИHИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИ^YXЫЬ][ЫЋ€[™\›[™NИ^YXЫЬ][Ы‹XЫЫЬЋ€\ЉKYЫЫ
NИ^][™\›[™K[Щ™њЩ]€Њ™[NИB‹™ЫЭ™\›[ЩK\Эљ\ИX\™Ъ[‹]Ь€KЌ\™[NИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€њ™[NИY[™О€KЊM\™[HKЊЌ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹[Yќ€ЫЫY\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹™ЫЭ™\›[ЩK\Эљ\€ИX\™Ъ[Ћ€ЊЌ\™[HИB‹™ЫЭ™\›[ЩK\Эљ\›\ЭXЪ[ИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИB‚‹К€\Ъ›Ш\™[YЫ™YЪ]H\›Э™Yљ\ЭX[™Y™\™[ЩH
‹В‹™\Ъ›Ш\™\YЩHИX^]ЪY€L	NИX\™Ъ[‹]Ь€KЌН\™[NИB‹™\Ъ›Ш\™\YЩHњYЩKZXY\€ИZ[‹ZZYЪ€ОИ[YЫ‹Z][\О€Щ[ќ\ЋИY[™ЛX›ЭЫN€KЊ\™[NИB‹™\Ъ›Ш\™\YЩHњYЩKZXY\€HИX\™Ъ[Ћ€ЊЌ\™[NИ›Ыќ\Ъ^™N€Ы[\
KЋ™[K‹ЊЭќЛ‹ЊЬ™[JNИB‹™\Ъ›Ш\™Y]HИ›^€]]ОИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€Ћњ™[NИB‹™\Ъ›Ш\™YЫЭ™\›[ЩHИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€KЊYњ€KЊ™њ€YњЋИX\™Ъ[‹]Ь€\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹[Yќ€ЫЫY\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹™\Ъ›Ш\™YЫЭ™\›[ЩH€]€ИZ[‹]ЪY€И\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€ЋZ[›X^
YњЉNИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€ЌН\™[NИY[™О€Ћ™[H\™[NИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[[™JNИB‹™\Ъ›Ш\™YЫЭ™\›[ЩH€]Ћ›\ЭXЪ[И›Ь™\‹\љYЪ€ИB‹™\Ъ›Ш\™YЫЭ™\›[ЩHЭ™ИИЪY€ЊњИZYЪ€ЊњИЫЫЬЋ€\ЉK[]ћJNИB‹™\Ъ›Ш\™YЫЭ™\›[ЩHЬ[€ИZ[‹]ЪY€И\Ь^N€ЬљYИШ\€Њ\™[NИB‹™\Ъ›Ш\™YЫЭ™\›[ЩHЫX[ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌ\™[NИ]\‹\ЬXЪ[™О€ЊНY[NИ^][њЩ›Ь›N€\\Ш\ЩNИB‹™\Ъ›Ш\™YЫЭ™\›[ЩHЭ›Ы™ИИЭ™\™›ЭО€Y[ЋИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌНњ™[NИ›Ыќ]ЩZYЪ€МИ^[Э™\™›ЭО€[\Ъ\ОИЪ]K\ЬXЩN€›ЭЬ\ИB‹™\Ъ›Ш\™[Y]љXЬИИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€™\X]
Z[›X^
YњЉJNИX\™Ъ[‹]Ь€KЊM\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ю\ЪYЭО€\ЉK\ЪYЭКNИB‹™\Ъ›Ш\™[Y]љXИИZ[‹ZZYЪ€LLњИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€NZ[›X^
YњЉNИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€\™[NИY[™О€\™[HKЊН\™[NИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[[™JNИB‹™\Ъ›Ш\™[Y]љXО›\ЭXЪ[И›Ь™\‹\љYЪ€ИB‹™\Ъ›Ш\™[Y]љXИ€]€ИZ[‹]ЪY€ИB‹™\Ъ›Ш\™[Y]љXИЭ›Ы™ИИ\Ь^N€›ШЪОИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ€МKЋ™[KМH\ЉKY›ЫќZXY[™КNИB‹™\Ъ›Ш\™[Y]љXИ€ИX\™Ъ[Ћ€ЊЌ\™[HЊLњ™[NИ›Ыќ\Ъ^™N€Ћ\™[NИB‹™\Ъ›Ш\™[Y]љXИИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌМњ™[NИЪ]K\ЬXЩN€›ЭЬ\ИB‹›Y]љXЛZXЫЫ€ИЪY€MњИZYЪ€MњИ\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИ›Ь™\‹\Y]\О€L	NИXЪЩЬ›Э[™€™ШЉLИ€MИЙJNИЫЫЬЋ€\ЉK[]ћJNИB‹›Y]љXЛZXЫЫ€Э™ИИЪY€ЋИZYЪ€ЋИB‹›Y]љXЛZXЫЫ‹YЫЫИXЪЩЬ›Э[™€™ШЉЊHMЊ€ОHИLЙJNИЫЫЬЋ€\ЉKYЫЫ
NИB‹›Y]љXЛZXЫЫ‹\ЭXШЩ\ЬИИXЪЩЬ›Э[™€™ШЉ€LОHИИL‰JNИЫЫЬЋ€\ЉK\ЭXШЩ\ЬКNИB‹™\Ъ›Ш\™\љ[X\ћKYЬљY™\Ъ›Ш\™\ЩXЫЫ™\ћKYЬљYИ\Ь^N€ЬљYИШ\€\™[NИX\™Ъ[‹]Ь€\™[NИ[YЫ‹Z][\О€Э™]ЪИB‹™\Ъ›Ш\™\љ[X\ћKYЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
KЌНYњЉHZ[›X^
ММYњЉNИB‹™\Ъ›Ш\™\ЩXЫЫ™\ћKYЬљYИЬљY][\]KXЫЫ[[њО€Z[›X^
KЊЋњЉHZ[›X^
ОLЋL™њЉNИB‹™\Ъ›Ш\™\љ[X\ћKYЬљY€њ[™[™\Ъ›Ш\™\ЩXЫЫ™\ћKYЬљY€њ[™[ИZ[‹]ЪY€ИZYЪ€L	NИX\™Ъ[‹]Ь€ИB‹™\Ъ›Ш\™\YЩHњЩXЭ[Ы‹ZXY[™ИИZ[‹ZZYЪ€LњИY[™О€ЌЬ™[H\™[HЌЬ™[HKЊЌ\™[NИB‹™\Ъ›Ш\™\YЩHњЩXЭ[Ы‹ZXY[™И€И›Ыќ\Ъ^™N€KЊ\™[NИB‹™\Ъ›Ш\™\YЩHњЩXЭ[Ы‹ZXY[™ИHИ›Ыќ\Ъ^™N€ЌН\™[NИB‹™\Ъ›Ш\™]\ЪЛ]X›HX›HИZ[‹]ЪY€ИX›K[^[Э]€љ^YИB‹™\Ъ›Ш\™]\ЪЛ]X›H™\Ъ›Ш\™]\ЪЛ]X›HИY[™О€ЊО™[HЌN™[NИ›Ыќ\Ъ^™N€ЌЋ™[NИ[™KZZYЪ€KЊЌNИЪ]K\ЬXЩN€›ЭЬ\ИB‹™\Ъ›Ш\™]\ЪЛ]X›HИ›Ыќ\Ъ^™N€ЌЊњ™[NИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
JK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
JHИЪY€INИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
ЉK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
ЉHИЪY€Ќ‰NИЪ]K\ЬXЩN€›Ь›X[ИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
КK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
КHИЪY€L‰NИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[

K™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[

HИЪY€MЙNИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
JK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
JHИЪY€M	NИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
ЉK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
ЉHИЪY€N	NИB‹™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
КK™\Ъ›Ш\™]\ЪЛ]X›H›ќXЪ[
КHИЪY€	NИB‹™\Ъ›Ш\™]\ЪЛ]X›HњЭ]\ИИ›Ыќ\Ъ^™N€ЌЌ\™[NИB‹ќX›KXXЭ[Ы€ИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ]ЩZYЪ€МИ^YXЫЬ][ЫЋ€[™\›[™NИ^YXЫЬ][Ы‹XЫЫЬЋ€\ЉKYЫЫ
NИ^][™\›[™K[Щ™њЩ]€Њ™[NИB‹њ\љ[ЩXЫЫќ›ЫИ\Ь^N€[›[™KY›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ќ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИY[™О€Ќ™[HЌM\™[NИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌМњ™[NИ›Ыќ]ЩZYЪ€МИB‹њ\љ[ЩXЫЫќ›ЫЭ™ИИЪY€MИZYЪ€MИB‹XЭ]љ]KXЪ\ќИX\™Ъ[Ћ€ИY[™О€ЊЬ™[HЋ™[HЌњ™[NИB‹XЭ]љ]KXЪ\ќXШ[ќ\ИИZ[‹ZZYЪ€ЊОИB‹њ]X[]K[\ЭИY[™О€ЊН\™[H\™[NИB‹њ]X[]K\›ЭИИZ[‹ZZYЪ€ЊИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€МZ[›X^
MLKЊ™њЉHZ[›X^
LМYњЉHњ]]ОИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ћ™[NИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB‹њ]X[]K\›ЭО›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИB‹њ]X[]KZXЫЫ€ИЪY€ЊњИZYЪ€ЊњИЫЫЬЋ€\ЉK[]ћJNИB‹њ]X[]KXЫЬHИ\Ь^N€ЬљYИB‹њ]X[]KXЫЬHЭ›Ы™ИИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌО™[NИB‹њ]X[]KXЫЬHЬ[€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌњ™[NИB‹њ]X[]K\›ЩЬ™\ЬИИZYЪ€\ИЭ™\™›ЭО€Y[ЋИ›Ь™\‹\Y]\О€NN\ИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹њ]X[]K\›ЩЬ™\ЬИЬ[€И\Ь^N€›ШЪОИZYЪ€L	NИ›Ь™\‹\Y]\О€[љ\љ]ИXЪЩЬ›Э[™€\ЉK\ЭXШЩ\ЬКNИB‹њ]X[]K\›ЭО›ќXЪ[
]™[ЉHњ]X[]K\›ЩЬ™\ЬИЬ[€ИXЪЩЬ›Э[™€\ЉK[]ћJNИB‹њ]X[]K][YHИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌН™[NИB‹њ]X[]K\›ЭИњЭ]\ИИќ\ЭYћKXЫЫќ[ќ€Щ[ќ\ЋИZ[‹]ЪY€LњИ›Ыќ\Ъ^™N€ЌЌњ™[NИB‹™\Ъ›Ш\™X\ЬЪ\Э[ќИ\Ь^N€ЬљYИШ\€ЌН\™[NИY[™О€Ћ\™[H\™[H\™[NИB‹™\Ъ›Ш\™X\ЬЪ\Э[ќ€ИX\™Ъ[Ћ€И›Ь™\‹[Yќ€ЬЫЫY\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK\\\ЉNИY[™О€ЌЌ\™[HЌН\™[NИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹\ЬЪ\Э[ќ\›Ы\ИИ\Ь^N€›^И›^]Ь\€Ь\ИШ\€Ќњ™[NИB‹\ЬЪ\Э[ќ\›Ы\ИHИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€NN\ИY[™О€ЊН™[HЌЌ\™[NИЫЫЬЋ€\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ыќ\Ъ^™N€ЌЋ™[NИ[њЪ][ЫЋ€›Ь™\‹XЫЫЬ€ML\ИX\ЩKXЪЩЬ›Э[™XЫЫЬ€ML\ИX\ЩNИB‹\ЬЪ\Э[ќ\›Ы\ИNљЭ™\€И›Ь™\‹XЫЫЬЋ€\ЉKYЫЫ
NИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹\ЬЪ\Э[ќZ[њ]ИZ[‹ZZYЪ€њИ\Ь^N€›^И[YЫ‹Z][\О€Щ[ќ\ЋИќ\ЭYћKXЫЫќ[ќ€ЬXЩKX™]ЩY[ЋИШ\€\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИЫЫЬЋ€\ЉK[]]Y
NИY[™Л[Yќ€Ћ™[NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹\ЬЪ\Э[ќ\Щ[™И[YЫ‹\Щ[Ћ€Э™]ЪИЪY€И\Ь^N€ЬљYИXЩKZ][\О€Щ[ќ\ЋИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИB‹\ЬЪ\Э[ќ\Щ[™Э™ИИЪY€ЊИZYЪ€ЊИB‹™\Ъ›Ш\™Y]K[›ЭHИX\™Ъ[Ћ€Ћ\™[HИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌњ™[NИ^X[YЫЋ€љYЪИB‚‹К€›Ь›\Л]Z[ЛЩX\ЪЪ]
‹В‹ќЫЫ\€ИX\™Ъ[Ћ€KЌ\™[HИ\Ь^N€›^ИШ\€ЌН\™[NИ[YЫ‹Z][\О€Щ[ќ\ЋИ›^]Ь\€Ь\ИY[™О€Ћ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹ќЫЫ\€[њ]њЩX\ЪY›Ь›H[њ]ИZ[‹]ЪY€Z[ЉМ™[KЋќКNИB‹њЩX\ЪY›Ь›HИ\Ь^N€ЬљYИШ\€Ќ\™[NИX\™Ъ[‹]Ь€KЌ\™[NИX^]ЪY€™[NИY[™О€KЊЌ\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИB‹њЩX\ЪY›Ь›H]€И\Ь^N€›^ИШ\€Ќ\™[NИB‹њ™XYЬќ[X€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€Ћ™[NИB‹њ™XYЬќ[X€HИЫЫЬЋ€\ЉK[]ћJNИ^YXЫЬ][ЫЋ€[™\›[™NИ^YXЫЬ][Ы‹XЫЫЬЋ€\ЉKYЫЫ
NИB‹™]Z[YЬљYИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€™\X]
ЛYњЉNИB‹™]Z[YЬљY]€ИY[™О€\™[NИ›Ь™\‹\љYЪ€\ЫЫY\ЉK[[™JNИB‹™]Z[YЬљY]Ћ›\ЭXЪ[И›Ь™\‹\љYЪ€ИB‹™]Z[YЬљYИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌН\™[NИB‹™]Z[YЬљYИX\™Ъ[Ћ€ЊН\™[HИ›Ыќ]ЩZYЪ€МИB‹њЩXЭ[ЫњИИX\™Ъ[Ћ€ИY[™О€\™[H\™[Hњ™[NИB‹њЩXЭ[ЫњИИИX\™Ъ[‹X›ЭЫN€ЊЌ\™[NИ›Ыќ\Ъ^™N€Ћ\™[NИB‹њ™\Э[ИИX\™Ъ[‹]Ь€KЌ\™[NИY[™О€И\Э\Э[N€›Ы™NИ\Ь^N€ЬљYИШ\€ЌН\™[NИB‹њ™\Э[ИHИXЪЩЬ›Э[™€\ЉK]Ъ]JNИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹[Yќ€ЬЫЫY\ЉK[]ћJNИY[™О€\™[NИB‹њ™\Э[ИИX\™Ъ[Ћ€ЊН\™[HИB‹ќЬ\ИЪ]K\ЬXЩN€›Ь›X[И›Ыќ\Ъ^™N€ЌН\™[NИB‹Ъ\ќИX\™Ъ[Ћ€ИY[™О€\™[NИB‹Ъ\ќXШ[ќ\ИИЪY€L	NИZ[‹ZZYЪ€ЌИB‹Ъ]И\Ь^N€ЬљYИШ\€\™[NИY[™О€\™[NИB‹Ъ][ЩЛЪ]]\›€И\Ь^N€ЬљYИШ\€\™[NИB‹Ъ]\]Y\Э[Ы€Иќ\ЭYћK\Щ[Ћ€[™ИX^]ЪY€ЪИX\™Ъ[Ћ€ИXЪЩЬ›Э[™€\ЉK[]ћJNИЫЫЬЋ€\ЉK]Ъ]JNИY[™О€ЌН\™[H\™[NИ›Ь™\‹\Y]\О€\ЉK\Y]\КNИB‹Ъ]X[њЭЩ\€ИX^]ЪY€LЪИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹[Yќ€ЫЫY\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK]Ъ]JNИY[™О€ЌН\™[H\™[NИB‹[њЭЩ\‹]^ИЪ]K\ЬXЩN€™K[[™NИB‹Ъ]][ЫњИИ\Э\Э[N€›Ы™NИX\™Ъ[Ћ€Ќ\™[HИY[™О€Ќ\™[HИ›Ь™\‹]Ь€\ЫЫY\ЉK[[™JNИ›Ыќ\Ъ^™N€Ћ\™[NИ\Ь^N€ЬљYИШ\€ЊЌ\™[NИB‹Ъ]KZ[™^И›Ыќ]ЩZYЪ€МИЫЫЬЋ€\ЉK[]ћJNИB‹™™YYXЪИИ\Ь^N€›^ИШ\€Ќ\™[NИ›^]Ь\€Ь\ИX\™Ъ[‹]Ь€Ќ\™[NИB‹Ъ]Y›Ь›HИ\Ь^N€ЬљYИШ\€Ќ\™[NИB‹›ШY[™ИИ\Ь^N€ЬљYИШ\€ЌН\™[NИY[™О€њ™[HИЫЫЬЋ€\ЉK[]]Y
NИB‹›ШY[™ЛX\€И\Ь^N€›ШЪОИЪY€Lњ™[NИZYЪ€ИXЪЩЬ›Э[™€\ЉK[[™JNИ›Ю\ЪYЭО€[њЩ]™[H\ЉK[]ћJNИB‹ќX›K\›ЭИИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€KЊЩњ€Yњ€ЌЩњЋИШ\€\™[NИY[™О€Ћ\™[H\™[NИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИ[YЫ‹Z][\О€Щ[ќ\ЋИB‹ќX›KZXY[™ИИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌН\™[NИ›Ыќ]ЩZYЪ€МИ^][њЩ›Ь›N€\\Ш\ЩNИBЫЩHИ›Ыќ\Ъ^™N€Ћ™[NИXЪЩЬ›Э[™€\ЉK\\\ЉNИY[™О€ЊЌ\™[NИB‚‹К€[Ыљ]Ьљ[™ИЩ\љN€[њЩKX›KYљ\њЭЫЫ[X[™Э\™XЩK€
‹В‹ќЫЬљЛ[X[YЩ\€И\Ь^N€ЬљYИШ\€\™[NИB‹ќЫЬљЛ]XњИИ\Ь^N€›^ИЭ™\™›ЭЛ^€]]ОИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИШЬ›Ы\‹]ЪY€[ЋИB‹ќЫЬљЛ]XњИќ]Ы€И\Ь^N€[›[™KY›^И[YЫ‹Z][\О€Щ[ќ\ЋИШ\€Ќ\™[NИZ[‹ZZYЪ€њИY[™О€Ќњ™[HЋ\™[NИ›Ь™\Ћ€И›Ь™\‹X›ЭЫN€ЬЫЫY[њЬ\™[ќИXЪЩЬ›Э[™€[њЬ\™[ќИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ€[љ\љ]И›Ыќ\Ъ^™N€ЌНњ™[NИ›Ыќ]ЩZYЪ€МИЪ]K\ЬXЩN€›ЭЬ\ИЭ\њЫЬЋ€Ъ[ќ\ЋИB‹ќЫЬљЛ]XњИќ]ЫЋљЭ™\‹ќЫЬљЛ]XњИќ]ЫЋ™›ШЭ\Л]љ\ЪX›HИЫЫЬЋ€\ЉK[]ћJNИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹ќЫЬљЛ]XњИќ]Ы‹љ\ЛXXЭ]™HИ›Ь™\‹X›ЭЫKXЫЫЬЋ€\ЉK[]ћJNИЫЫЬЋ€\ЉK[]ћJNИB‹ќЫЬљЛ]XњИЬ[€ИZ[‹]ЪY€ЊњИY[™О€Њ™[HЊНњ™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИ›Ь™\‹\Y]\О€NN\ИXЪЩЬ›Э[™€\ЉK]Ъ]JNИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЌ™[NИ^X[YЫЋ€Щ[ќ\ЋИB‹ќЫЬљЛXYИZ[‹ZZYЪ€НњИY[™О€ЌLњ™[HЋ™[NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹ќЫЬљЛY™YYXЪИИX\™Ъ[Ћ€Ћ\™[NИY[™О€ЌЌ\™[HЋ™[NИ›Ь™\‹[Yќ€ЬЫЫY\ЉKYЫЫ
NИXЪЩЬ›Э[™€\ЉK\\\ЉNИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌНњ™[NИB‹ќЫЬљЛY›Ь›HИ\Ь^N€ЬљYИЬљY][\]KXЫЫ[[њО€™\X]
ЛZ[›X^
YњЉJNИШ\€Ћ\™[NИX\™Ъ[‹X›ЭЫN€\™[NИY[™О€\™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™JNИXЪЩЬ›Э[™€\ЉK\\\ЉNИB‹ќЫЬљЛY›Ь›HX™[И\Ь^N€ЬљYИ[YЫ‹XЫЫќ[ќ€Э\ќИШ\€ЊН\™[NИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌЋ™[NИ›Ыќ]ЩZYЪ€МИB‹ќЫЬљЛY›Ь›H[њ]ќЫЬљЛY›Ь›HЩ[XЭќЫЬљЛY›Ь›H^\™XKќЫЬљЛ]X›HЩ[XЭИЪY€L	NИZ[‹ZZYЪ€ОИY[™О€Ќ\™[HЌЊњ™[NИ›Ь™\Ћ€\ЫЫY\ЉK[[™K\Э›Ы™КNИ›Ь™\‹\Y]\О€ЬИXЪЩЬ›Э[™€\ЉK]Ъ]JNИЫЫЬЋ€\ЉKZ[љКNИ›Ыќ€[љ\љ]И›Ыќ\Ъ^™N€ЌНњ™[NИB‹ќЫЬљЛY›Ь›H^\™XHИZ[‹ZZYЪ€ОИ™\Ъ^™N€™\ќXШ[ИB‹ќЫЬљЛY›Ь›K]ЪYHИЬљYXЫЫ[[Ћ€Ь[€ЋИB‹ќЫЬљЛY›Ь›KXXЭ[ЫњИИЬљYXЫЫ[[Ћ€HИLNИ\Ь^N€›^Иќ\ЭYћKXЫЫќ[ќ€›^Y[™ИШ\€Ќњ™[NИY[™Л]Ь€Њњ™[NИB‹ќЫЬљЛY›Ь›KXXЭ[ЫњИќ]Ы€ИZ[‹ZZYЪ€НњИY[™О€Ќ\™[HЋ\™[NИ›Ыќ\Ъ^™N€ЌМњ™[NИB‹ќЫЬљЛ]X›HX›HИZ[‹]ЪY€ИB‹ќЫЬљЛ]X›H™љ\њЭXЪ[ИZ[‹]ЪY€ЊМИЪ]K\ЬXЩN€›Ь›X[ИB‹ќЫЬљЛ]X›H™љ\њЭXЪ[Э›Ы™ИИ\Ь^N€›ШЪОИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ\Ъ^™N€ЌНњ™[NИB‹ќЫЬљЛ]X›H™љ\њЭXЪ[ЫX[И\Ь^N€›ШЪОИX\™Ъ[‹]Ь€ЊN™[NИЫЫЬЋ€\ЉK\љ\ЪКNИ›Ыќ\Ъ^™N€ЌЊњ™[NИB‹ќЫЬљЛ]X›HЩ[XЭИZ[‹ZZYЪ€МњИY[™О€ЊЬ™[HЌ™[NИ›Ыќ\Ъ^™N€ЌЋ™[NИB‹њ›ЭЛXXЭ[ЫњИИ\Ь^N€›^ИШ\€ЌM\™[NИB‹њ›ЭЛXXЭ[ЫњИќ]Ы€ИY[™О€И›Ь™\Ћ€ИXЪЩЬ›Э[™€[њЬ\™[ќИЫЫЬЋ€\ЉK[]ћJNИ›Ыќ€[љ\љ]И›Ыќ\Ъ^™N€ЌЋ™[NИ›Ыќ]ЩZYЪ€МИ^YXЫЬ][ЫЋ€[™\›[™NИ^][™\›[™K[Щ™њЩ]€ЬИЭ\њЫЬЋ€Ъ[ќ\ЋИB‹њ›ЭЛXXЭ[ЫњИ™[™Щ\‹[[љИИЫЫЬЋ€\ЉK\љ\ЪКNИB‹ќЫЬљЛ\ЫXЮK[›ЭHИX\™Ъ[Ћ€ИЫЫЬЋ€\ЉK[]]Y
NИ›Ыќ\Ъ^™N€ЌЬ™[NИ[™KZZYЪ€KЌMNИB‚ђYYXH
X^]ЪY€LЊ
HВ€™\Ъ›Ш\™[Y]љXЬИИЬљY][\]KXЫЫ[[њО€™\X]
‹Z[›X^
YњЉJNИB€™\Ъ›Ш\™[Y]љXО›ќXЪ[
ЉHИ›Ь™\‹\љYЪ€ИB€™\Ъ›Ш\™[Y]љXО›ќXЪ[
[€
ИЉHИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€™\Ъ›Ш\™\љ[X\ћKYЬљY™\Ъ›Ш\™\ЩXЫЫ™\ћKYЬљYИЬљY][\]KXЫЫ[[њО€YњЋИBџB‚ђYYXH
X^]ЪY€L
HВ€›[™[™ЛZ\›ИИЬљY][\]KXЫЫ[[њО€YњЋИШ\€ИY[™ЛX›ЭЫN€Ь™[NИB€љ\›ЛXЫЬHИY[™Л\љYЪ€ИB€љ\›Л\Э][Y[ќИZ[‹ZZYЪ€НИB€Ш\Xљ[]K\ЩXЭ[Ы€ИЬљY][\]KXЫЫ[[њО€YњЋИШ\€њ™[NИB€]]\YЩHИЬљY][\]KXЫЫ[[њО€YњЋИB€]]XЫЫќ^ИZ[‹ZZYЪ€НИBџB‚ђYYXH
X^]ЪY€L
HВ€\\Ъ[ИЬљY][\]KXЫЫ[[њО€YњЋИB€њЪYX\€ИZ[‹ZZYЪ€]]ОИB€њЪYX\‹Z[›™\€ИЬЪ][ЫЋ€Э]XОИZ[‹ZZYЪ€]]ОИB€њ[™ИZ[‹ZZYЪ€MњИ›^Y\™XЭ[ЫЋ€›ЭОИ[YЫ‹Z][\О€Щ[ќ\ЋИШ\€\™[NИB€њ[™[YИИЪY€LMњИX\™Ъ[Ћ€ИB€њ[™ЫX[И\Ь^N€›Ы™NИB€њЪYX\€]€И\Ь^N€›^ИЭ™\™›ЭЛ^€]]ОИY[™О€ЌЌ\™[NИB€њЪYX\€]€HИ›^€]]ОИB€њЪYX\‹[›ЭHИ\Ь^N€›Ы™NИB€ќЬ\€И›^]Ь\€Ь\ИB€™ЫШ[\ЩX\ЪИЪY€L	NИЬ™\Ћ€ЋИB€ќЬ\‹XXШЫЭ[ќИX\™Ъ[‹[Yќ€ИY[™Л[Yќ€И›Ь™\‹[Yќ€ИB€›Y]љXЛYЬљY›Y]љXЬИИЬљY][\]KXЫЫ[[њО€™\X]
‹YњЉNИB€›Y]љXО›ќXЪ[
ЉHИ›Ь™\‹\љYЪ€ИB€›Y]љXО›ќXЪ[
[€
ИЉHИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€ќЫЛXЫЫ[[€ИЬљY][\]KXЫЫ[[њО€YњЋИB€™\Ъ›Ш\™YЫЭ™\›[ЩHИЬљY][\]KXЫЫ[[њО€YњЋИB€™\Ъ›Ш\™YЫЭ™\›[ЩH€]€И›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€™\Ъ›Ш\™YЫЭ™\›[ЩH€]Ћ›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИBџB‚ђYYXH
X^]ЪY€MЊ
HВ€њX›XЛZXY\€ИZYЪ€]]ОИY[™ЛX›ШЪО€\™[NИB€њX›XЛXњ[™€[YИИЪY€LLњИB€њ[™Y]љY\‹њ›ЩXЭ]ЫЬ™X\љИИ\Ь^N€›Ы™NИB€љ\›ЛXЫЬHИY[™ЛX›ШЪО€ЛЌ\™[NИB€љ\›ЛXЫЬHHИ›Ыќ\Ъ^™N€‹ЌM\™[NИB€љ\›ЛXXЭ[ЫњЛњX›XЛY›ЫЭ\‹њYЩKZXY\‹™ЫЭ™\›[ЩK\Эљ\И[YЫ‹Z][\О€›^\Э\ќИ›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИB€љ\›Л\Э][Y[ќИY[™О€њ™[NИB€Ш\Xљ[]K\ЩXЭ[Ы€ИY[™ЛX›ШЪО€™[NИB€]]XЫЫќ^ИZ[‹ZZYЪ€ИY[™О€њ™[NИB€]]\[™[ИY[™О€‹Ќ\™[HKЊЌ\™[NИB€ќЬ\‹XXШЫЭ[ќЬ[€И\Ь^N€›Ы™NИB€ќЬ\‹XXШЫЭ[ќИZ[‹]ЪY€ИY[™Л[Yќ€И›Ь™\‹[Yќ€ИB€ќЬ\‹XXШЫЭ[ќЭ›Ы™ЛXШЫЭ[ќXЪ]њ›Ы€И\Ь^N€›Ы™NИB€››ЭYљXШ][Ы‹Xќ]Ы€И›Ь™\‹[Yќ€ИY[™Л[Yќ€ИB€™\Ъ›Ш\™[Y]љXЬИИЬљY][\]KXЫЫ[[њО€YњЋИB€™\Ъ›Ш\™[Y]љXИИ›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€™\Ъ›Ш\™[Y]љXО›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИB€њ]X[]K\›ЭИИЬљY][\]KXЫЫ[[њО€ЋZ[›X^
YњЉH]]ОИШ\€ЌЌ\™[NИY[™О€ЌЌ\™[HИB€њ]X[]K\›ЩЬ™\ЬИИЬљYXЫЫ[[Ћ€€ИLNИЪY€L	NИB€њ]X[]K][YHИЬљYXЫЫ[[Ћ€ЋИB€њ]X[]K\›ЭИњЭ]\ИИЬљYXЫЫ[[Ћ€ОИЬљY\›ЭО€ОИB€XZ[Ћ››Э
›[™[™Л]]\YЩJHИY[™ЛZ[›[™N€\™[NИB€›Y]љXЛYЬљY›Y]љXЬИИЬљY][\]KXЫЫ[[њО€YњЋИB€›Y]љXИИ›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€›Y]љXО›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИB€ќЫЫ\€И[YЫ‹Z][\О€Э™]ЪИ›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИB€ќЫЫ\€[њ]ќЫЫ\€Щ[XЭњЩX\ЪY›Ь›H[њ]ИЪY€L	NИZ[‹]ЪY€ИB€ќX›K\›ЭЛ™]Z[YЬљYИЬљY][\]KXЫЫ[[њО€YњЋИB€™]Z[YЬљY]€И›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€њЩX\ЪY›Ь›H]€И[YЫ‹Z][\О€Э™]ЪИ›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИBџB‚ђYYXH
X^]ЪY€НЊ
HВ€ќЫЬљЛY›Ь›HИЬљY][\]KXЫЫ[[њО€YњЋИB€ќЫЬљЛY›Ь›K]ЪYHИЬљYXЫЫ[[Ћ€]]ОИBџB‚ђYYXH
X^]ЪY€L
HВ€њX›XЛ[]€И\Ь^N€›Ы™NИB€›[™[™ЛZ\›ИИЬљY][\]KXЫЫ[[њО€YњЋИY[™ЛX›ЭЫN€ИB€љ\›ЛXЫЬHИY[™Л\љYЪ€Ы[\
KЊЌ\™[K]ќЛKЌ\™[JNИB€љ\›ЛZ[XYЩHИZ[‹ZZYЪ€ОИB€XШЩ\ЬЛ\Z[ИЬљY][\]KXЫЫ[[њО€YњЋИB€XШЩ\ЬЛ\Z[€€ИZ[‹ZZYЪ€МњИ›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€XШЩ\ЬЛ[[љЬИИЬљY][\]KXЫЫ[[њО€™\X]
‹Z[›X^
YњЉJNИB€XШЩ\ЬЛ[[љЬИN›ќXЪ[
ЉHИ›Ь™\‹\љYЪ€ИB€XШЩ\ЬЛ[[љЬИN›ќXЪ[
[€
ИЉHИ›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€љ[њЭ]][Ы[XЫЫќ[ќИЬљY][\]KXЫЫ[[њО€YњЋИШ\€™[NИB€]][^[Э]ИЬљY][\]KXЫЫ[[њО€YњЋИB€]]XЫЫќ^ИZ[‹ZZYЪ€LЊИBџB‚ђYYXH
X^]ЪY€MЊ
HВ€љ[њЭ]][Ы‹X\€ИZ[‹ZZYЪ€МњИB€љ[њЭ]][Ы‹X\€Ь[Ћ›ќXЪ[
ЉKљ[њЭ]][Ы‹]ЫЫИИ\Ь^N€›Ы™NИB€њX›XЛZXY\€ИZ[‹ZZYЪ€НњИY[™ЛX›ШЪО€ЌЌ\™[NИB€њX›XЛXњ[™€[YИИЪY€LИB€њ[™Y]љY\€И\Ь^N€›Ы™NИB€њ›ЩXЭ]ЫЬ™X\љИИ\Ь^N€ЬљYИB€њ›ЩXЭ]ЫЬ™X\љИЭ›Ы™ИИ›Ыќ\Ъ^™N€Ћ\™[NИB€њ›ЩXЭ]ЫЬ™X\љИЫX[И\Ь^N€›Ы™NИB€њX›XЛ[ЩЪ[‹[[љИИZ[‹]ЪY€]]ОИY[™ЛZ[›[™N€Ћ™[NИB€љ\›ЛXЫЬHИY[™ЛX›ШЪО€ЛЌ\™[NИB€љ\›ЛXЫЬHHИ›Ыќ\Ъ^™N€‹ЊН\™[NИB€љ\›ЛXXЭ[ЫњИИ[YЫ‹Z][\О€Э™]ЪИB€љ\›ЛZ[XYЩHИZ[‹ZZYЪ€ЌЊИB€XШЩ\ЬЛ[[љЬИИЬљY][\]KXЫЫ[[њО€YњЋИB€XШЩ\ЬЛ[[љЬИHИZ[‹ZZYЪ€И›Ь™\‹\љYЪ€И›Ь™\‹X›ЭЫN€\ЫЫY\ЉK[[™JNИB€XШЩ\ЬЛ[[љЬИN›\ЭXЪ[И›Ь™\‹X›ЭЫN€ИB€ЫЫќ[ќZXY[™Лњ›ЭЭ\K[›ЭXЩHИ[YЫ‹Z][\О€›^\Э\ќИ›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИB€њ›ЭЭ\K[›ЭXЩHИШ\€Ќ\™[NИB€њ›ЭЭ\K[›ЭXЩH]€И›^Y\™XЭ[ЫЋ€ЫЫ[[ЋИШ\€Њњ™[NИB€њX›XЛY›ЫЭ\€И\Ь^N€›^ИB€њX›XЛY›ЫЭ\€€Ь[Ћ›\ЭXЪ[И^X[YЫЋ€YќИB€]]XЫЫќ^ИZ[‹ZZYЪ€МИY[™О€‹Ќ\™[HKЌ\™[NИB€]]\љ[Ъ\\ИИ\Ь^N€ЬљYИШ\€ЌН\™[NИB€]]\љ[Ъ\\ИЬ[€И›Ь™\‹\љYЪ€ИY[™О€ИBџB‚ђYYXH
™Y™\њЛ\™YXЩY[[Э[ЫЋ€™YXЩJHВ€[ИШЬ›ЫX™Z]љ[ЬЋ€]]ОИB€
‹
ЋЋ™Y›Ь™K
ЋЋYќ\€ИШЬ›ЫX™Z]љ[ЬЋ€]]ИZ[\Ьќ[ќИ[њЪ][Ы‹Y\][ЫЋ€Њ[\ИZ[\Ьќ[ќИBџB‚