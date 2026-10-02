# Risk Register

**Status:** NEEDS MENTOR VALIDATION  
**Last Updated:** 2026-10-01

Scores and owners are intentionally omitted until the project adopts an agreed method. The order below is not a quantified priority.

## Active risks

### R-001 — Unvalidated business rules

- **Evidence:** CONFIRMED
- **Condition:** SUN process, approval, and role details are not fully validated.
- **Impact:** implementation may encode incorrect behavior.
- **Response:** keep uncertain behavior configurable or unimplemented; record it in open questions; obtain mentor acceptance before build.
- **Owner:** OPEN QUESTION

### R-002 — Mock mistaken for production

- **Evidence:** CONFIRMED
- **Condition:** simulated data or adapter screens may look authoritative.
- **Impact:** misleading demonstrations and unsafe decisions.
- **Response:** label every seed and mock response `SIMULATED_DATA`; display environment/integration status; prohibit production claims.
- **Owner:** project team, pending named owner.

### R-003 — Unauthorized knowledge disclosure

- **Evidence:** PROPOSED
- **Condition:** search or RAG retrieves content outside user scope.
- **Impact:** confidentiality breach.
- **Response:** authorize before retrieval, filter by classification and scope, deny by default, and test negative paths.
- **Owner:** OPEN QUESTION

### R-004 — AI output treated as fact

- **Evidence:** PROPOSED
- **Condition:** generated answers lack adequate citations or confidence boundaries.
- **Impact:** incorrect operational interpretation.
- **Response:** source-linked answers, explicit no-source behavior, and human approval for sensitive writes.
- **Owner:** OPEN QUESTION

### R-005 — External access unavailable

- **Evidence:** CONFIRMED
- **Condition:** production SSO, repositories, messaging, BI, and market-data access are unavailable.
- **Impact:** integration scope cannot be completed or validated.
- **Response:** use interfaces and honest mocks; separate integration readiness from core MVP acceptance.
- **Owner:** OPEN QUESTION

### R-006 — Schedule overreach

- **Evidence:** CONFIRMED
- **Condition:** broad platform scope exceeds the 21 September 2026–20 March 2027 period.
- **Impact:** incomplete core flows and weak documentation.
- **Response:** phase delivery; prioritize platform foundation, Kinerja Tim Kerja, Knowledge Hub foundation, RBAC, and audit.
- **Owner:** project and mentor, pending validation.

### R-007 — Personal or sensitive data in repository

- **Evidence:** PROPOSED
- **Condition:** developers copy internal files or identities into seeds/logs.
- **Impact:** data exposure.
- **Response:** simulated seeds only, content-safe logs, repository review, and secret scanning where available.
- **Owner:** project team.

### R-008 — SUN Tematik assumptions

- **Evidence:** OPEN QUESTION
- **Condition:** the sixth team's function is inferred without evidence.
- **Impact:** incorrect navigation, data ownership, or permission model.
- **Response:** retain only its confirmed name until mentor clarification.
- **Owner:** mentor validation required.

## Review rule

- Review at each scope or architecture decision.
- Close a risk only with evidence, date, and approver.
- Escalate any risk involving real data, permissions, or external publication immediately.

## Related Documents

- [Open questions](open-questions.md)
- [Decision log](decision-log.md)
- [Validation](../12-validation/README.md)
