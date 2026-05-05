# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root
- `docs/adr/` for ADRs that touch the area about to be changed

If any of these files do not exist, proceed silently. Do not flag their absence or suggest creating them upfront.

## File structure

Single-context repo:

```text
/
|-- CONTEXT.md
|-- docs/
|   `-- adr/
|       |-- 0001-example-decision.md
|       `-- 0002-example-decision.md
`-- src/
```

## Use the glossary's vocabulary

When output names a domain concept in an issue title, refactor proposal, hypothesis, or test name, use the term as defined in `CONTEXT.md`.

If the concept is not in the glossary yet, either reconsider whether the term belongs to this project or note the gap for future domain documentation.

## Flag ADR conflicts

If output contradicts an existing ADR, surface it explicitly rather than silently overriding it.
