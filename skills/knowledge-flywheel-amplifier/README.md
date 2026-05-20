# Knowledge Flywheel Amplifier

Dedicated nightly skill for the **04:00 amplifier stage** in the split knowledge flywheel.

## Why this skill exists

The old nightly flywheel mixed together three very different jobs:
- article integration
- transcript mining
- cross-source amplification

This skill isolates the third job: take already-produced knowledge signals and decide whether they form a stronger cross-source pattern worth indexing, clustering, or researching further.

## Ownership

This skill owns:
- cross-source topic merging
- open-question clustering
- pattern-candidate consolidation
- research seed drafting
- context-pack candidate drafting
- cautious graph/index updates after Stage A + Stage B

This skill does **not** own:
- raw article normalization
- raw transcript mining
- automatic heavy deep research every night
- broad graph surgery

## Inputs

Upstream sources:
- outputs from `article-notes-integration`
- outputs from `conversation-knowledge-mining`

Read-only context:
- relevant Brain notes
- project briefs
- topic maps
- open-question surfaces

## Outputs

Typical output set:
- amplifier report
- compact cross-source graph/index updates
- research seeds
- context-pack drafts

## Operating Principle

Prefer:
- conservative merging
- provenance-preserving synthesis
- optional escalation
- high-signal small writes

over:
- large nightly rewrites
- flattening all inputs into one blob
- pretending every overlap deserves research
- auto-running deep research without a scoped question
