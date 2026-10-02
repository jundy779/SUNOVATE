# RAG and Hermes Boundary

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

## Retrieval flow

```mermaid
sequenceDiagram
    actor User
    participant UI as Ask SUNOVATE
    participant API as SUNOVATE API
    participant H as Hermes
    participant S as Authorized Search
    participant DB as PostgreSQL FTS + pgvector
    User->>UI: Submit question
    UI->>API: Question + user context
    API->>API: Authorize scope and classification
    API->>H: Approved tool request
    H->>API: Call search tool
    API->>S: Permission-filtered retrieval
    S->>DB: Hybrid search
    DB-->>S: Candidate passages
    S-->>API: Authorized evidence
    API-->>H: Evidence with citations
    H-->>API: Grounded answer
    API-->>UI: Answer + citations + limitations
```

## Guardrails

- **CONFIRMED:** Hermes has no direct database credentials or query path.
- **PROPOSED:** combine PostgreSQL FTS and pgvector ranking after permission filtering.
- **PROPOSED:** answers cite accessible source entries and state when evidence is insufficient.
- **PROPOSED:** retrieval and tool calls emit audit events without logging unnecessary sensitive content.
- **PROPOSED:** resist prompt injection by treating retrieved content as evidence, never system instructions.
- **OPEN QUESTION:** approved embedding/model provider, hosting boundary, retention, and evaluation thresholds.
- **OUT OF SCOPE:** autonomous consequential writes and access beyond the caller's permissions.

## Related Documents

- [Knowledge Hub](README.md)
- [Authorization](../06-security/authorization.md)
- [API contract](../07-api/README.md)
