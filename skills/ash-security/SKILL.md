---
name: ash-security
description: Change or review Ash authorization, trusted scopes and field exposure.
---

# Ash Security

Follow the operation's actor, tenant and accepted inputs from its actual entry point
to the resource action. Reuse the application's trusted scope representation.
A supplied tenant ID is not proof of membership; a browser state is not authorization.

[Threat cases](references/threat-cases.md) covers cross-tenant references, privilege
changes, nested data, field exposure and background execution.
[Operator actions](references/operator-actions.md) covers who an operator is, staff
pages, release commands that change live data, the record they leave and development
tools.
[Component session check](references/component-session-check.md) covers LiveComponents,
whose events skip the page's session re-check.

Explicit Ash options can replace scope-derived values: `actor: nil` may erase the
scope's actor. Inspect wrapper defaults and keyword merges. In callbacks, propagate
the supplied context using the installed API rather than stale request state.

Unauthorized reads can filter records or return not-found; test non-disclosure under
the actual policy contract instead of requiring Forbidden everywhere. For writes,
prove that a rejected operation did not change protected state.

For Regent Privy/session work, consult [Privy reconciliation](../ash-stack/references/privy-reconciliation.md).
This review guidance does not create another workflow stage or approval boundary.
