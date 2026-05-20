# Article Notes Integration

Dedicated nightly skill for the **02:00 article integration stage** in the split knowledge flywheel.

## Why this skill exists

The old monolithic nightly flywheel mixed together:
- article normalization
- transcript mining
- cross-source synthesis
- research amplification

This skill isolates the article side so the nightly system becomes easier to:
- reason about
- validate
- rerun partially
- operate with clear ownership

## Ownership

This skill owns:
- scanning yesterday's new article notes
- re-checking pending article notes
- updating article relation / integration metadata
- updating lightweight topic/index surfaces
- emitting article-derived candidates for downstream amplification

This skill does **not** own:
- coding transcript mining
- daily suggestions from transcripts
- heavy external research execution
- full graph/global rewrite

## Inputs

Primary source:
- `/tmp/brain-os-test/vault/03-KNOWLEDGE/01-DOMAINS/Article-Notes/`

Context sources:
- `/tmp/brain-os-test/vault/03-KNOWLEDGE/06-INDEXES/`
- `/tmp/brain-os-test/vault/05-PROJECTS/`

## Outputs

Typical output set:
- integration report
- article note relation updates
- cautious topic / open-question / pattern-candidate updates
- a list of high-value article candidates for 04:00 amplification

## Operating Principle

Prefer:
- fewer, meaningful writes
- candidate-first extraction
- conservative project linking
- explicit no-op when there is no signal

over:
- large automatic rewrites
- fake activity
- forcing every article into a pattern
- pretending uncertain links are certain
