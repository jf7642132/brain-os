# Surveillance Scan Spec

## Purpose

Use a fast, cheap model layer to do broad candidate recall after transcript collection and project grouping.

## What Surveillance should do

- scan per-project transcript groups quickly
- surface likely high-value conversations
- avoid deciding final knowledge shape
- reduce miss risk before final manual synthesis

## Inputs

- daily manifest
- project-grouped transcript lists
- Brain-side project briefs from `05-PROJECTS/` when a project can be mapped
- QMD recalled candidate chunks (preferred)
- optional recent Knowledge context

## Recall Standard (not final knowledge standard)

Surveillance exists to reduce miss risk before Brain OS Manager reads deeply.
It should score candidates using recall-oriented signals:

1. **Project relevance**
   - strongly tied to active projects / active operational systems
2. **Structural density**
   - contains decisions, comparisons, review conclusions, architecture edges, rules, or reusable methods
3. **Next-day leverage**
   - likely to affect tomorrow's execution or judgment
4. **Pattern / anomaly recurrence**
   - repeated issue, repeated theme, or systemic signal across multiple transcripts

## Outputs

For each project, produce:
- top candidate transcript paths
- stable project anchor when known (`project_ref`, project name, optional project brief path)
- one-line reason each candidate may matter
- priority bucket (`P1`, `P2`, `P3`)
- possible continuation questions
- optional external-research seed

## Explicit non-goals

- no final note writing
- no hard taxonomy enforcement
- no claim that a candidate is definitely worth long-term memory
- no direct Brain write
- no hallucinated project mapping when project confidence is low
- no overriding Brain OS Manager judgment
