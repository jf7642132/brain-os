# State DB Schema & Session Behavior Reference

**Last updated**: 2026-05-18

## Database Location

```
/root/.hermes/state.db
```

## Tables

| Table | Purpose |
|-------|---------|
| `sessions` | Session metadata (id, source, model, timestamps, message_count, title) |
| `messages` | Per-message content (role, content, timestamp, tool_calls, etc.) |
| `messages_fts*` | Full-text search indexes for messages |
| `state_meta` | System metadata |

## Sessions Table Schema

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    source TEXT,              -- 'cli', 'telegram', 'weixin', 'cron', 'api_server', etc.
    model TEXT,
    started_at REAL,          -- Unix timestamp
    ended_at REAL,
    message_count INTEGER,
    user_id TEXT,
    title TEXT
);
```

## Messages Table Schema

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    role TEXT,                -- 'user', 'assistant', 'tool', 'system'
    content TEXT,
    tool_call_id TEXT,
    tool_calls TEXT,          -- JSON array of tool calls
    tool_name TEXT,
    timestamp REAL,
    token_count INTEGER,
    finish_reason TEXT,
    reasoning TEXT,
    reasoning_details TEXT,
    ...
);
```

## Session Sources

| Source | Description | Substantive? |
|--------|-------------|--------------|
| `cli` | Terminal/CLI interactions | ✅ Yes |
| `telegram` | Telegram messages | ✅ Yes |
| `weixin` | WeChat messages | ✅ Yes |
| `discord` | Discord messages | ✅ Yes |
| `whatsapp` | WhatsApp messages | ✅ Yes |
| `api_server` | Web UI / API server | ⚠️ May lack user messages |
| `cron` | Automated cron tasks | ❌ No (noise) |
| `dingtalk` | DingTalk messages | ✅ Yes |
| `acp` | ACP/Copilot CLI | ⚠️ Rare |

## ⚠️ Critical: api_server Sessions May Lack User Messages

**Discovery (2026-05-18)**: `api_server` sessions (from Hermes Dashboard Web UI) may have **NO user messages** in the `messages` table.

When this happens:
- The `messages` table contains only assistant (with `tool_calls`) and tool messages
- User's actual intent/decision/task assignment is **not captured**
- You can only infer activity from assistant final responses (`finish_reason='stop'`, no `tool_calls`)
- These are **speculative** — log as "从 assistant 响应推断" with appropriate caveats

**Detection pattern**:
```python
cur.execute("""
    SELECT role, content, tool_calls, finish_reason
    FROM messages
    WHERE session_id LIKE ?
""", (session_id + '%',))

# If only assistant messages with tool_calls exist, and no user messages:
# → User messages are absent from state.db
# → Infer from assistant final response only
```

## Query Patterns

### Get sessions in time window
```python
cur.execute("""
    SELECT id, source, started_at, message_count, title
    FROM sessions
    WHERE started_at >= ? AND started_at <= ?
    ORDER BY started_at ASC
""", (window_start_ts, now_ts))
```

### Get user messages for a session
```python
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'user'
    ORDER BY timestamp ASC
""", (session_id + '%',))
```

### Get assistant non-tool-call responses
```python
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'assistant'
      AND (tool_calls IS NULL OR tool_calls = '')
    ORDER BY timestamp ASC
""", (session_id + '%',))
```

## Schema Variability

⚠️ **The `messages` table schema may vary across versions**. Some queries have failed with errors like:
- `no such column: session_id`
- `no such column: created_at`

**Fallback**: If `state.db` queries fail, fall back to direct session file scan in `/root/.hermes/sessions/`.

## Session ID Formats

Session IDs vary by source:
- `cli`: `20260518_155050_5fce...` (date_time_hash format)
- `cron`: `cron_ce8a1963857a_20...` (cron_prefix_hash format)
- `api_server`: `fe2fea62-2c44-4fe7-8...` (UUID format) or `eph_*`, `api-*`

**Use `LIKE` matching, not exact prefix**:
```python
cur.execute("... WHERE session_id LIKE ?", (session_id_prefix + '%',))
```
