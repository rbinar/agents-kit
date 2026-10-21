---
description: PLAN — turn a PRD or story into an SDD and a file-based implementation plan
argument-hint: <PRD, story or SDD path>
---
Input: $ARGUMENTS

1. Delegate to `sdlc:dev-tech-lead` to produce the SDD (and ADRs if needed) under `.specs/dev/`. Skip this if the input already is an SDD.
2. Delegate to `sdlc:dev-planner` with the SDD to produce the parallel-wave implementation plan.
3. Show the artefact paths and suggest `/sdlc:build` as the next step.
