# Session Storage Behavior Reference

**Last updated**: 2026-05-18

## Overview

Hermes stores session data in two locations:
- **`state.db` (SQLite)** — Primary storage for recent sessions
- **`/root/.hermes/sessions/*.jsonl`** — Archive storage for historical sessions

## Critical Finding: Session Files Are Archived

**Discovery (2026-05-18)**: The `/root/.hermes/sessions/` directory contains **archived/historical sessions**, not recent ones.

| Storage | Content | Use Case |
|---------|---------|----------|
| `state.db` | Recent sessions (last ~24-48 hours) | Primary source for Chronicle Agent scans |
| `/root/.hermes/sessions/*.jsonl` | Archived sessions (weeks/months old) | Historical reference, not for recent scans |

**Evidence**: Session files in the directory are dated from April 2026 (e.g., `20260411_221351_*.jsonl`, `20260415_*.jsonl`), while recent sessions from May 18 only exist in `state.db`.

## Implications for Chronicle Agent

### Primary Method: Use `state.db`

For time-window scans (e.g., last 2 hours), **always query `state.db` first**:

```python
import sqlite3
conn = sqlite3.connect('/root/.hermes/state.db')
cur = conn.cursor()
cur.execute("""
    SELECT id, source, started_at, message_count, title
    FROM sessions
    WHERE started_at >= ? AND started_at <= ?
    ORDER BY started_at ASC
""", (window_start_ts, now_ts))
```

### Fallback: Session Files for Historical Context

Session files should only be used when:
- `state.db` is unavailable or incomplete
- You need historical sessions outside the recent window
- You need to verify session content that may have been pruned from `state.db`

### api_server Sessions: Context Compaction Checkpoints

**Discovery (2026-05-18)**: `api_server` sessions from Hermes Dashboard Web UI are **context compaction checkpoints**, not actual user conversations.

These sessions contain:
1. **User message**: System instruction to generate a context summary
2. **Assistant message**: Structured summary of prior conversation (Active Task, Goal, Constraints, Completed Actions)

**They are NOT substantive user interactions** and should be filtered out.

**Detection pattern**:
```python
cur.execute("""
    SELECT role, content, tool_calls
    FROM messages
    WHERE session_id LIKE ?
    ORDER BY timestamp ASC
""", (session_id + '%',))

# If messages are:
# - [user]: "You are a summarization agent creating a context checkpoint..."
# - [assistant]: "## Active Task..." (structured summary)
# → This is a context compaction checkpoint, NOT a user conversation
```

## Session ID Format Summary

| Source | ID Format | Example |
|--------|-----------|---------|
| `cli` | `YYYYMMDD_HHMMSS_hash` | `20260518_155050_5fce...` |
| `cron` | `cron_hash_YYYYMMDD_HHMMSS` | `cron_ce8a1963857a_20...` |
| `api_server` | UUID | `5d8fddeb-1774-484a-bd86-...` |
| `weixin` | `YYYYMMDD_HHMMSS_hash` | (same as cli) |
| `telegram` | `YYYYMMDD_HHMMSS_hash` | (same as cli) |

**Query pattern**: Always use `LIKE` with partial ID match, never exact match.

## Version History

| Date | Change |
|------|--------|
| 2026-05-18 | Documented session file archival behavior and api_server checkpoint pattern |
