# Forms and LiveView: boundary checks

## Select the real form constructor

Inspect `AshPhoenix` in the domain's extensions and its `forms` configuration. Generated
`form_to_*` helpers follow code-interface configuration; their positional arguments
are not safely guessed from the action's name. An update may require a record first.
Read generated docs or a compiling caller. Do not copy `MyApp` placeholders into an app.

A direct `AshPhoenix.Form.for_create/for_update/for_action` constructor is legitimate
when supported and appropriate. The action still owns validation, policy, and writes.
Use a correct explicit domain when the resource belongs to more than one. Preserve the
project's representation of the form rather than converting inconsistently on each event.

The usual lifecycle is construction with trusted scope, conversion for Phoenix's
form components, validation on change, and submission on submit. Error submission
returns the form needed for rendering; retaining it matters. Verify the exact API
contract in the installed version before coding.

## Error diagnostic sequence

When a field error does not appear, inspect the action error first. Then check action
argument/attribute names, submitted root key, form field path, nested form configuration,
component field binding, and touched-input behavior. A policy/transaction error may
not belong to a field; show a safe form-level message. Do not suppress warnings about
unhandled errors without understanding them.

For a custom error, check the installed `AshPhoenix.FormData.Error` protocol or error
transformation API. Preserve field/path semantics. Do not rewrite all errors to a
generic success-shaped result or display raw internal exceptions to the user.

## Nested form contract

Before implementation answer: which child actions are called; can the caller relate
existing records; what does remove do; does omission leave existing children unchanged;
what does an empty list mean; where do child authorization and tenant checks happen?
For editing existing children, load the required relationships under the current
scope before constructing the form; absent loads must not masquerade as no children.
Test at least one invalid child and one malicious related ID. Prefer stable form paths
and supported add/remove helpers to manually editing internal form structures.

## Changing scope while a form is open

On organization switch, identity refresh, or revoked membership, do not submit a form
under a previous tenant and then render success in the new tenant. Rebuild or explicitly
update the action context through a verified API. The real action must evaluate the
current authorization contract; refreshing a UI assign alone is not sufficient.

## Useful LiveView design choices

Keep one owner for URL parameters, one owner for form state, and one owner for each
JS-controlled island. Separate temporary UI preferences from server-authoritative data.
Do not fetch data during render. For updates from other actors, requery under the
viewer's scope; do not trust that the broadcast producer chose safe fields for them.

For async results, follow [async state](async-state.md): each read is owned by the
account, wallet or route that started it. Check reversed completion order. For
streams, use the required container update mode and DOM IDs, and reset on changed
filter/sort scope when necessary. Do not assume a stream is a normal enumerable retained in assigns.

## UI-affordance checks are not final authorization

A permission preflight may return a different result from the action when state or
membership changes between the two. Make the action's result authoritative and handle
that denial safely. A disabled submit button is not an idempotency mechanism.

Sources: [index](../../ash-stack/references/source-index.md), S23-S29.
