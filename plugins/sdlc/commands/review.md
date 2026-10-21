---
description: REVIEW — code review, plus security review for high-risk changes
argument-hint: <PR number, branch or path>
---
Target: $ARGUMENTS (if empty, use the current diff)

1. Delegate to `sdlc:dev-reviewer` to review the target.
2. If the change touches auth/authz, infra, payments, secrets or personal data, also delegate to `sdlc:dev-security`.
3. Summarize the findings by severity and suggest `/sdlc:ship` when nothing blocking remains.
