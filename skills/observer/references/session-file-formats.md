# Session File Format Reference

Hermes Agent stores session files in multiple formats. Observer skill must check all patterns.

## Format Patterns

| Format | Extension | Naming Pattern | Status |
|--------|-----------|----------------|--------|
| Current JSON | `.json` | `session_YYYYMMDD_HHMMSS_XXXXXX.json` | Active |
| Legacy JSON | `.json` | `YYYYMMDD_HHMMSS_XXXXXX.json` | Legacy |
| Old JSONL | `.jsonl` | `YYYYMMDD_*.jsonl` | Deprecated |

## Detection Logic

```python
today_date = datetime.now().strftime("%Y%m%d")
sessions_dir = os.path.expanduser("~/.hermes/sessions/")

today_sessions = [
    f for f in os.listdir(sessions_dir) 
    if (f.startswith(f"session_{today_date}") or 
        f.startswith(f"{today_date}_")) and 
       (f.endswith('.jsonl') or f.endswith('.json'))
]
```

## Pitfalls

1. **Only checking `.jsonl`** - Will miss all current session files (Hermes Agent switched to `.json` format)
2. **Only checking `YYYYMMDD_*` prefix** - Will miss `session_YYYYMMDD_*` pattern
3. **Session files may not exist for today** - Cron may run before any sessions are created; fallback to yesterday

## Example Files

```
session_20260519_105333_314e8b.json     # Current format
session_20260519_000151_78534c.json     # Current format
20260518_094807_becca394.jsonl          # Legacy JSONL (rare)
```

## Verification

After running observer, verify:
1. `.learnings/observer/plans/YYYY-MM-DD-iteration-plan.md` exists
2. Session count matches expected (check `~/.hermes/sessions/` for today's files)
3. If plan file missing but task status shows "ok", check session format detection logic
