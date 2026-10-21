---
description: SHIP — build verification, changelog, PR, merge and tag
argument-hint: <branch or PR>
---
Target: $ARGUMENTS (if empty, use the current branch)

Delegate to `core:dev-shipper` to ship the target. Before any merge, push or tag, confirm with the user.
