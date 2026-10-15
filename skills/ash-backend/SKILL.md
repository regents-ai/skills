---
name: ash-backend
description: Design or simplify Ash resources, actions and domain interfaces.
---

# Ash Backend

Keep business rules in Ash actions and policies. Keep plain computation in ordinary
Elixir. Prefer a built-in before a custom change, and a custom change before a manual
action when each expresses the same requirement correctly.

Named domain interfaces and action-bound forms are intended application boundaries.
A one-line interface is not automatically waste. Remove local wrappers only when
they add no meaningful behavior, callback contract, actor propagation or error handling.
Ecto remains appropriate for migrations, diagnostics and justified data-layer work.

- [Action and resource decisions](references/decision-guide.md): accepted inputs,
  relationships, derived values and choosing an implementation boundary.
- [Integrations](references/integrations.md): jobs, external effects and adapters.
  Durable, retried or scheduled work is Oban; see [elixir-stack](../elixir-stack/SKILL.md).

Generic persistent idempotency or outbox guidance never authorizes blocking a Regent
user-signed wallet transaction. Every distinct button press reaches the wallet.
A wallet panel's signer is Privy's active wallet when it is one of the signed-in
account's linked wallets, checked on the server against the verified session; any
other wallet only prompts a switch. See the wallet rule in regent-workflow.
Keep the assignment’s acceptance and self-review; this skill adds no plan or reviewer.
