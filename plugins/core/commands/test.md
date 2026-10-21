---
description: VERIFY — write and run tests for a change; debug failures
argument-hint: <story, AC or changed files>
---
Target: $ARGUMENTS (if empty, use the current uncommitted changes)

1. Delegate to `core:dev-test-engineer` to derive and run tests for the target.
2. If tests fail for a reason outside the test code, delegate to `core:dev-debugger` with the failure output.
3. Report the result and suggest `/review` as the next step.
