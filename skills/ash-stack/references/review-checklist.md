# Risk-directed final review

Use only relevant questions; do not paste an unfilled checklist into a handoff.

**Domain:** Is there one named action owning the behavior? Are action arguments,
accepted attributes, public fields, and privileged derived values distinct? Does a
new abstraction eliminate real duplication? Are callback contracts verified?

**Access:** Does the real write/read authorize? Is the scope trusted and fresh enough?
Can an explicit option erase its actor? Can a nested relationship cross tenants?
Can a read, count, search, export, log, or subscription reveal protected data?

**Data:** Does the invariant survive concurrent requests, alternate entry points,
and retries? Are identities backed by the intended constraint? Are migrations safe
for existing data and old/new releases? Are generated snapshots consistent?

**Side effects:** What survives a process crash? What happens after a timeout with
unknown remote outcome? Is idempotency persisted? Is a job scheduled atomically with
the business state when needed? Is any notification being sent before commit?

**UI:** Is the actual primary task obvious? Are loading, no-results, empty, invalid,
denied, stale, and offline states distinguishable where relevant? Is a persisted
success shown only after the action succeeds? Does navigation or reconnect restore
the correct scope and data? Are form errors accessible and inputs preserved?

**Performance:** Are loads/pagination bounded? Does rendering initiate database work?
Is there an N+1 loop? Does async work capture more state than it needs? Is a claimed
optimization backed by representative measurements rather than added infrastructure?

**Evidence:** Is there a regression or negative test? Were project gates actually run?
Does a browser-only behavior have browser evidence? Are blocked checks clearly marked?
Did the change leave unrelated work, credentials, and production state untouched?
