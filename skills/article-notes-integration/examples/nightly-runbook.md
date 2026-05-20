# Article Notes Integration Nightly Runbook

## Happy Path

Expected 02:00 result:
- article integration report generated
- only article-related metadata/index surfaces touched
- no transcript-derived notes created here
- Brain commit exists if changes were justified
- result is Obsidian-visible

## Common Failure Modes

- no new/pending article notes
- malformed frontmatter or conflicting metadata
- index update resolves to no-op
- Brain repo dirty/conflicted before write
- post-commit visibility not confirmed

## Operator Response

- If no new notes: accept no-op, do not rerun blindly
- If one note fails: isolate that note, mark review-needed path, rerun only this stage
- If repo is dirty: stop and resolve repo state before retry
- If visibility is missing after commit: treat as not complete yet
