# UX and Information Architecture

**Status:** PROPOSED  
**Last Updated:** 2026-10-01

## Navigation

- Dashboard / Management Cockpit
- SUN Business
- Kinerja Tim Kerja
- Knowledge Hub
- Reporting & Analytics
- Ask SUNOVATE
- Administration

**PROPOSED:** menus and actions are permission-aware; the API remains the authorization authority. Exact labels, route depth, dashboard indicators, and mobile behavior need user validation.

## Design baseline

- Navy `#0D2E5E` for primary navigation, headings, and primary actions.
- Gold `#C9A227` for identity and focus accents, not operational status.
- White `#FFFFFF`, background `#F7F8FA`, line `#D8DDE3`, muted text `#6B7280`.
- Emerald `#2E8B57` for success; crimson `#B22222` for risk or lateness.
- Aptos Display headings; Aptos body; Segoe UI/system fallbacks.

Operational pages provide loading, empty, error, denied, and conflict states. Tables use server-side pagination and filters. Forms retain visible labels, keyboard operation, useful focus, and text alongside color.

## Validation needs

- **OPEN QUESTION:** approved menu names and terminology per team.
- **OPEN QUESTION:** priority tasks and device/browser constraints.
- **OPEN QUESTION:** accessibility acceptance criteria beyond WCAG-informed practice.
- **OUT OF SCOPE:** decorative dashboards without a validated decision purpose.

## Related Documents

- [Product](../01-product/README.md)
- [Requirements](../02-requirements/README.md)
- [Security](../06-security/README.md)
