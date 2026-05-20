# Knowledge Flywheel Amplifier Nightly Runbook

## Happy Path

Expected 04:00 result:
- amplifier report generated
- compact topic/open-question/pattern-candidate updates when justified
- optional research seeds / context-pack drafts
- no automatic heavy deep research
- Brain commit exists if changes were justified
- result is Obsidian-visible

## Common Failure Modes

- Stage A output missing
- Stage B output missing
- both upstream stages missing
- no real cross-source signal
- topic merge confidence too low
- Brain repo dirty/conflicted before write

## Operator Response

- If one upstream stage is missing: continue in degraded mode, report which side is partial
- If both are missing: emit no-op amplifier report and stop
- If merge confidence is low: keep separate candidates; do not over-merge
- If research question is too vague: do not escalate to deep research
- If repo is dirty: stop before write and resolve state
