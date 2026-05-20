# 429 Rate Limit Concentration Analysis

## Overview

429 errors (HTTP Too Many Requests) often concentrate in specific sessions rather than being evenly distributed. Identifying the concentration pattern is critical for actionable recommendations.

## Analysis Pattern

```bash
# Extract session IDs from 429 errors and calculate concentration
grep 'Error code: 429' errors.log | grep -oP '(?<=\[)[^\]]+(?=\])' | sort | uniq -c | sort -rn
```

## Example Output (2026-05-18)

```
     68 20260516_074336_8fa6ff
      6 20260517_112145_f8221d
      3 20260517_140545_66e4d1
      2 6b7fed6f-4467-4ca1-a620-bfd6be32a2b5
      2 19bfef7d-46c5-4c02-9a9b-b747d2e5eb6b
      1 266a40bd-6033-40c7-a11c-f49edfe3caff
      1 20260517_192801_285f9c
```

## Interpretation

| Metric | Value | Action |
|--------|-------|--------|
| Total 429 errors | 83 | Baseline |
| Top session count | 68 | 82% concentration |
| Top session ID | 20260516_074336_8fa6ff | Long-running session |
| Other sessions | 15 | Distributed across 6 sessions |

**Key insight**: When >70% of errors come from a single session, the problem is **session-specific** (long-running, high-frequency calls) rather than **systemic** (global rate limit).

## Recommendations by Concentration Level

### High Concentration (>70% from one session)

**Root cause**: Long-running session making frequent API calls

**Actions**:
1. Implement session-level rate limiting
2. Add request queuing with exponential backoff
3. Split long tasks into multiple shorter sessions
4. Add cooldown periods between API calls

### Medium Concentration (30-70% from one session)

**Root cause**: Multiple sessions competing for rate limit

**Actions**:
1. Implement global rate limiting across all sessions
2. Add request prioritization
3. Consider increasing rate limit quota with provider

### Low Concentration (<30% from any session)

**Root cause**: Systemic rate limit issue

**Actions**:
1. Reduce overall API call frequency
2. Implement caching for repeated queries
3. Negotiate higher rate limits with provider
4. Consider alternative models/providers

## Extraction of Model Names from 429 Errors

429 errors may include model information in the nested JSON:

```bash
# Extract model name from 429 error message
grep 'Error code: 429' errors.log | grep -oP "'model': '\K[^']+" | sort | uniq -c | sort -rn
```

This helps identify which models are most affected by rate limiting.

## Historical Data

| Date | Total 429 | Top Session | Concentration | Action Taken |
|------|-----------|-------------|---------------|--------------|
| 2026-05-17 | 83 | 20260516_074336_8fa6ff | 82% | Documented |
| 2026-05-18 | 83 | 20260516_074336_8fa6ff | 82% | Same session, persistent issue |

**Note**: The same session (`20260516_074336_8fa6ff`) appears across multiple days, indicating a persistent long-running session that needs intervention.