# session_search Tool Behavior Reference

## Overview

The `session_search` tool is the primary entry point for Chronicle Agent session discovery. Understanding its behavior is critical for accurate scanning.

## Tool Invocation

```python
# ✅ Correct - invoke directly
session_search(query="recent", limit=20)  # Recent sessions (no query)
session_search(query="keyword", limit=10)  # Keyword search

# ❌ WRONG - will fail with ImportError
from hermes_tools import session_search
```

## Return Structure

```json
{
  "success": true,
  "query": "search query or empty for recent",
  "results": [
    {
      "session_id": "20260517_084118_...",
      "when": "May 17, 2026 at 08:41 AM",
      "source": "cron",
      "model": "sensenova-6.7-flash-lite",
      "summary": "[Raw preview — summarization unavailable]\n[USER]: [IMPORTANT: You are running as a scheduled cron job..."
    }
  ],
  "count": 5,
  "sessions_searched": 5
}
```

## Key Behaviors

### 1. Recent Mode (no query)
- Returns most recent sessions regardless of content
- Sorts by `last_active` timestamp
- Summaries are LLM-generated from session content
- **Limitation**: Summaries may be truncated or empty for cron sessions

### 2. Keyword Search Mode
- Uses FTS5 full-text search on session content
- Supports boolean operators: `OR`, `AND`, `NOT`
- Supports prefix search: `deploy*`
- **Important**: FTS5 defaults to AND logic — use OR between keywords for best results

### 3. Cron Session Behavior

When scanning a window that contains only cron sessions:

| Observation | Meaning |
|-------------|---------|
| `source: "cron"` | Automated task, not user-initiated |
| `summary: "[Raw preview — summarization unavailable]"` | Cron prompt was the only content |
| `message_count: 4-20` | Only system messages + tool calls |
| `model: "sensenova-6.7-flash-lite"` | Default cron model |

**Pattern**: Cron sessions show the cron prompt itself in the summary:
```
"[Raw preview — summarization unavailable]
[USER]: [IMPORTANT: You are running as a scheduled cron job. DELIVERY: ..."
```

This is a reliable signal that the window contains **no user-initiated interactions**.

### 4. Time Range Limitations

`session_search` does NOT support explicit time-range filtering. The query parameter is keyword-based, not temporal.

**Workaround**: Use SQLite query on `state.db` for precise time filtering:
```python
import sqlite3
conn = sqlite3.connect('<HERMES_STATE_DB>')
cur = conn.cursor()
cur.execute("""
    SELECT id, source, started_at
    FROM sessions
    WHERE started_at >= ? AND started_at <= ?
""", (window_start_ts, now_ts))
```

### 5. Session ID Formats

Different sources produce different session ID formats:

| Source | Session ID Format |
|--------|-------------------|
| `cli` | `YYYYMMDD_HHMMSS_...` |
| `cron` | `cron_<hash>_<YYYYMMDD_HHMMSS>` |
| `weixin` | `YYYYMMDD_HHMMSS_...` |
| `api_server` | UUID (`16742469-6ea5-...`) or `eph_*` |
| `telegram` | `YYYYMMDD_HHMMSS_...` |

When querying `state.db`, use `LIKE` match for partial IDs.

## Common Search Patterns

```python
# Get recent sessions (all sources)
session_search(limit=10)

# Search for specific keywords
session_search(query="decision OR task OR technical", limit=10)

# Search for specific session ID
session_search(query="20260516_074336", limit=5)

# Boolean search (use OR for broad results)
session_search(query="cron OR weixin OR cli", limit=20)
```

## When session_search Returns Nothing

If `session_search` returns 0 results or only cron sessions:

1. **Do not conclude "no activity"** — proceed to SQLite query
2. **SQLite may have different data** — `session_search` summaries are cached/summarized
3. **Check `state.db` directly** for sessions in the time window
4. **Fallback to session files** if `state.db` is unavailable

## Related Skills

- `chronicle-agent`: Main skill for session scanning
- `conversation-knowledge-flywheel`: Transcript mining for cross-session knowledge
- `knowledge-flywheel-amplifier`: Cross-source amplification

## Version History

| Date | Change |
|------|--------|
| 2026-05-17 | Documented cron session summary pattern from live scan |
