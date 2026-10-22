---
description: VERIFY — write and run tests for a change; debug failures
argument-hint: <story, AC or changed files>
---
Target: $ARGUMENTS (if empty, use the current uncommitted changes)

1. Delegate to `sdlc:dev-test-engineer` to derive and run tests for the target.
2. If tests fail for a reason outside the test code, delegate to `sdlc:dev-debugger` with the failure output.
3. If the debugger proposes a fix, delegate it to `sdlc:dev-coordinator` and re-run the tests.
4. Report the result and suggest `/sdlc:review` as the next step.
