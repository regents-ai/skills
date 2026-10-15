---
name: ash-frontend
description: Build or refine AshPhoenix forms and LiveView interfaces.
---

# Ash Frontend

Keep domain behavior in the action and presentation in the component or LiveView.
Action-bound AshPhoenix forms are a supported boundary; do not add an Ecto changeset
pipeline around them. Verify generated helper signatures against the installed version.

- [Forms and LiveView](references/forms-and-liveview.md): validation/submission,
  nested forms, omitted inputs, async results and reconnect behavior.
- [Async state](references/async-state.md): reads owned by an account, wallet or
  route; late answers dropped; loading, ready, empty, stale and error kept apart.
  Every page read goes through the template's `Read`; never stop one with
  `cancel_async`, which takes the read's database connection down with it.
- [UI review](references/ui-review.md): accessibility, responsive states and hooks.

Reuse Regent UI primitives while retaining each product's theme, navigation and
layout. Components own no authentication, database or wallet admission decisions.
A second on-chain button press must still reach the wallet while the first is pending.

Keep the returned error form after failed submission. LiveView tests do not execute
browser hooks; use a browser when the changed behavior depends on JavaScript or layout.
