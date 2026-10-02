# System Context

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

SUNOVATE sits between authorized users and approved information sources. Dashed nodes are future integration boundaries, not available production services.

```mermaid
C4Context
    title SUNOVATE System Context
    Person(user, "Authorized SUN User", "Uses management and knowledge capabilities")
    System(sunovate, "SUNOVATE", "Integrated management and knowledge platform")
    System_Ext(hermes, "Hermes", "AI orchestration through APIs only")
    System_Ext(identity, "Production Identity Provider", "Unavailable; future approved SSO")
    System_Ext(docs, "Document Systems", "Unavailable; future SharePoint or approved repository")
    System_Ext(official, "Official/External Systems", "Unavailable; Kemenkeu Satu, BI, market data, Power BI and channels")

    Rel(user, sunovate, "Uses over authenticated UI/API")
    Rel(hermes, sunovate, "Calls permission-aware APIs")
    Rel(sunovate, identity, "Future authentication", "Unavailable")
    Rel(sunovate, docs, "Future metadata/reference sync", "Unavailable")
    Rel(sunovate, official, "Future approved integration", "Unavailable")
```

## Context rules

- **CONFIRMED:** Hermes has no direct database path.
- **CONFIRMED:** unavailable systems must be represented by adapters/mocks and labeled as such.
- **PROPOSED:** SUNOVATE stores document metadata and references while approved document repositories remain source of truth where applicable.
- **OPEN QUESTION:** authoritative source and update cadence for each SUN business dataset.

## Related Documents

- [Architecture index](README.md)
- [Container architecture](containers.md)
- [Integration boundaries](integration-boundaries.md)
