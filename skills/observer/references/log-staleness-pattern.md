# Log Staleness Pattern — Error Logs vs Current State

## Problem

Error logs in `~/.hermes/logs/errors.log` accumulate historical entries and do not auto-purge when issues are fixed. This creates a misleading picture of current system health.

## Example from 2026-05-20 Observer Run

| Observation | Finding |
|-------------|---------|
| `grep -c 'Falling back to default config' errors.log` | 57 occurrences |
| `python -c "import yaml; yaml.safe_load(open('config.yaml'))"` | **Valid** — no error |

**Conclusion**: The 57 "Falling back to default config" entries are historical (from 2026-05-17). The current config.yaml is valid.

## Root Cause

- Logs are append-only; they don't track when issues are resolved
- Error patterns persist in logs even after root cause is fixed
- `grep -c` counts all historical occurrences, not just current-day issues

## Detection Pattern

Always verify current state with live validation, not just log grep:

```bash
# Check logs for historical count
grep -c 'Falling back to default config' ~/.hermes/logs/errors.log || echo 0

# Verify current state
python -c "import yaml; yaml.safe_load(open('<HERMES_CONFIG>'))" && echo "Valid" || echo "Invalid"

# Check recent errors only (last 24 hours)
grep "$(date +%Y-%m-%d)" ~/.hermes/logs/errors.log | grep -c 'Falling back to default config' || echo 0
```

## Reporting Guidance

When reporting errors in observer daily reports, distinguish:

| Metric | Source | Meaning |
|--------|--------|---------|
| **Historical count** | `grep -c` on full log | Total occurrences ever logged |
| **Current status** | Live validation | What's actually broken NOW |
| **Today's count** | `grep "$(date)"` | New occurrences today |

**Report format**:
```
**Falling back to default config**: 57 historical occurrences (last seen 2026-05-19)
⚠️ Note: YAML validation shows config.yaml is currently valid. Errors in logs are historical.
```

## Action Items

1. If live validation passes but logs show errors → note as "historical, not current"
2. If live validation fails → report as active issue with severity
3. Consider adding log rotation or error deduplication to reduce staleness

## Related Files

- `~/.hermes/logs/errors.log` — primary error log
- `~/.hermes/logs/gateway.log` — normal requests
- `~/.hermes/logs/agent.log` — agent activity
- `~/.hermes/config.yaml` — configuration file