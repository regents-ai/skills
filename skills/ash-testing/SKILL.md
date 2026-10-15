---
name: ash-testing
description: Design Ash regression tests or remove redundant test coupling.
---

# Ash Testing

Choose the layer that observes the changed contract. Pure computation needs ordinary
unit tests; Ash policy/data behavior needs real actions; SQL invariants need the SQL
data layer; browser hooks and layout need browser evidence.

[Test recipes](references/test-recipes.md) covers fixtures, policy filtering, forms,
concurrency and jobs. Reuse the existing runner and its isolated test environment.

For cleanup, identify what each candidate test protects. Keep meaningful ABI, policy,
receipt and database invariants. Remove duplicate evidence and incidental source-name,
exact test-count or decorative-copy locks; replace useful assertions at the behavior
boundary before deleting them. No test-count or deletion quota applies.

Check runner discovery when changing it. Inspect aliases before using them as checks:
some format files, unlock dependencies or set up databases. Rerun tests affected by a
fix; broaden only for a changed risk or unresolved failure. Do not invent a baseline,
reviewer or evidence ceremony beyond the task's workflow.

Report executed checks separately from missing database/browser/provider evidence.
