# Authentication Flow

**Status:** NEEDS MENTOR VALIDATION  
**Last Updated:** 2026-10-01

## Development baseline

- **CONFIRMED:** production SSO is unavailable.
- **PROPOSED:** development authentication uses seeded `SIMULATED_DATA` identities and an explicitly visible development-mode marker.
- **PROPOSED:** the API creates or validates the local session and loads roles/scopes on every protected request.
- **OUT OF SCOPE:** presenting development authentication as production identity assurance.

```mermaid
sequenceDiagram
    actor U as User
    participant W as Next.js Web
    participant A as FastAPI API
    participant I as Development Identity Adapter
    participant D as PostgreSQL
    U->>W: Select simulated identity
    W->>A: Authenticate (development only)
    A->>I: Validate seeded identity
    I-->>A: Identity reference
    A->>D: Load active user, roles, scopes
    D-->>A: Authorization context
    A-->>W: Secure session
    W-->>U: Show simulated-data banner
```

## Production gate

The production identity provider, claims mapping, session lifetime, MFA, account provisioning, deprovisioning, and emergency access are **OPEN QUESTION**. No SSO implementation should be labeled production-ready before these are approved and tested.

## Related Documents

- [Security baseline](README.md)
- [Open questions](../11-governance/open-questions.md)
- [Acceptance](../12-validation/acceptance.md)
