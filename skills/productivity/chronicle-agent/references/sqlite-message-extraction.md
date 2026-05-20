# SQLite Message Extraction Pattern

## Primary Data Source

The `state.db` SQLite database at `/root/.hermes/state.db` is the primary source for session and message data.

## Tables

| Table | Purpose |
|-------|---------|
| `sessions` | Session metadata (id, source, model, timestamps, message_count) |
| `messages` | Individual messages (content, role, tool_calls, timestamp) |
| `messages_fts` | Full-text search index for messages |

## Session Query Pattern

```python
import sqlite3
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))  # CST
conn = sqlite3.connect('/root/.hermes/state.db')
cur = conn.cursor()

# Get sessions in time window
window_start_ts = (datetime.now(tz) - timedelta(hours=2)).timestamp()
now_ts = datetime.now(tz).timestamp()

cur.execute("""
    SELECT id, source, model, started_at, ended_at, message_count
    FROM sessions
    WHERE started_at >= ? AND started_at <= ?
    ORDER BY started_at DESC
""", (window_start_ts, now_ts))
sessions = cur.fetchall()
```

## Message Extraction Pattern

```python
# Get user messages for a session
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'user'
    ORDER BY timestamp ASC
""", (session_id + '%',))

for content, ts in cur.fetchall():
    dt = datetime.fromtimestamp(ts, tz=tz).strftime('%H:%M:%S')
    print(f"[USER {dt}] {content[:500]}")

# Get assistant non-tool-call responses
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'assistant'
      AND (tool_calls IS NULL OR tool_calls = '')
    ORDER BY timestamp ASC
""", (session_id + '%',))
```

## Sessions Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Session ID |
| `source` | TEXT | `cli`, `telegram`, `weixin`, `api_server`, `cron`, etc. |
| `model` | TEXT | Model name |
| `started_at` | REAL | Unix timestamp |
| `ended_at` | REAL | Unix timestamp (NULL if still running) |
| `message_count` | INTEGER | Total messages in session |
| `tool_call_count` | INTEGER | Number of tool calls |
| `title` | TEXT | Session title |

## Messages Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Message ID |
| `session_id` | TEXT | Parent session ID |
| `role` | TEXT | `user`, `assistant`, `tool` |
| `content` | TEXT | Message content |
| `tool_calls` | TEXT | JSON array of tool calls (NULL if none) |
| `timestamp` | REAL | Unix timestamp |
| `token_count` | INTEGER | Token count |
| `reasoning` | TEXT | Reasoning content (if any) |

## Filtering by Source

```python
# Valid user-initiated sources
USER_SOURCES = ['cli', 'telegram', 'weixin', 'discord', 'whatsapp', 'api_server']

# Exclude these
SYSTEM_SOURCES = ['cron', 'curator']
```

## Session File Format

Session files are stored as standard `.json` files in `/root/.hermes/sessions/`:

```
session_20260518_070224_958b54.json
```

Each file is a single JSON object with `source`, `model`, and `messages` keys:

```json
{
  "source": "cli",
  "model": "deepseek-v4-flash",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "...", "tool_calls": [...]},
    {"role": "tool", "content": "...", "tool_name": "write_file"}
  ]
}
```

## Pitfalls

1. **Session IDs are partial matches**: Use `LIKE` with `%` wildcard when querying by session ID prefix
2. **Timestamps are Unix floats**: Convert with `datetime.fromtimestamp(ts, tz=tz)`
3. **`tool_calls` is JSON string**: Parse with `json.loads()` if not NULL
4. **Messages table may not exist**: The `messages` table in state.db is not guaranteed to exist in all Hermes versions. Always wrap message queries in try/except and fall back to reading session JSON files directly if `no such table` error occurs.
5. **Session JSON files are the authoritative source**: SQLite is secondary and often incomplete. The session `.json` files contain the full message content including user messages.
6. **`api_server` sessions**: Web UI interactions appear with unusual session IDs (UUID format)