# Security test design

Select cases relevant to the actual feature. Resolve real helper names and policy
error contracts from the target project; this is not executable Elixir.

| Attempt | Evidence required |
| --- | --- |
| Anonymous caller invokes protected action directly | No unauthorized read/write, safe documented result |
| User edits another user's record | Real action denies; persisted state unchanged |
| Member of tenant A supplies tenant B's ID | Tenant membership checked, not just a query filter |
| Valid parent references a child from another tenant | Nested relationship operation cannot link or reveal the child |
| Allowed UI button is followed by membership revocation | Action reevaluates intended current permission |
| Caller passes owner/role/tenant attributes through a form | Privileged fields remain server-controlled |
| Wrapper adds `actor: nil` to a valid scope | Test exposes and removes the unintended override |
| User lists records, counts, and exports | Protected records/fields do not leak in alternate read shapes |
| An update is sent directly without rendering the page | Policy still enforced |
| A worker retries after a user's access is revoked | Explicit user/service execution contract upheld |
| A shared PubSub topic announces another tenant's update | No private payload leakage; scoped reread stays authorized |
| API asks for sensitive fields through includes/relationships | Serialization and field-level access remain correct |
| An action request is replayed | No duplicate irreversible effect where idempotency is required |

For read filtering, a successful response with fewer records can be correct. Assert
that forbidden IDs/data are absent and authorized data remains visible. Do not write
an assertion that every authorization failure must be `Ash.Error.Forbidden`.

For writes, assert persistence, not just a status code or a flash message. Test a direct
backend call separately from the UI guard. Avoid blanket authorization bypasses in
fixtures for the operation being tested; a privileged fixture setup is a separate,
explicitly scoped concern.

## Version-sensitive policy details

For policies over to-many relationships, distinguish a condition on the same related
row from separate existential conditions. Inspect documented `exists/2` support and
test the intended combinations; a plausible-looking relationship filter can be too
restrictive or refer to a different business condition.

In the Ash 3.32.3 docs, create filter checks can authorize after insertion and after
`after_action` hooks, within a transaction. An eventual denial rolls back database
work, not an already sent HTTP request. Do not infer “finally authorized” from reaching
an action hook. Inspect the locked version's transaction requirements and any
`allow_post_action_authorization?` opt-in before changing this behavior. Never add that
opt-in merely to silence a preflight error. Test the denied path and side-effect absence.

Do not mix all failure mechanisms into one enormous test. Use small named examples
that state the security property and fail for a meaningful reason.

Sources: [index](../../ash-stack/references/source-index.md), S04-S06, S14, S28.
