# Session File Format — Chronicle Agent Reference

**Last updated**: 2026-05-18

## Format

Session files are stored in **`.jsonl` (JSON Lines)** format, NOT `.json`.

Each line is a **separate JSON object** representing one message in the conversation.

## File Location

```
<HERMES_SESSIONS_DIR>/
```

## Line Structure

Each line contains a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `role` | string | Message role: `user`, `assistant`, `system`, `tool`, `SESSION_META` |
| `content` | string | Message text content |
| `timestamp` | number or string | Unix timestamp (float) or ISO string |
| `tool_calls` | array | Tool call requests (for assistant messages) |
| `tool_call_id` | string | Tool call ID (for tool responses) |
| `finish_reason` | string | `stop`, `tool_calls`, `length`, etc. |
| `token_count` | integer | Token count for this message |

## Timestamp Handling

Timestamps can appear in two formats:

1. **Unix timestamp (float)**: `1779098766.610738`
2. **ISO string with timezone**: `"2026-05-18T09:48:24.000000+08:00"`

**Parsing pattern**:
```python
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))  # CST

def parse_timestamp(ts):
    if isinstance(ts, str):
        # Handle ISO string
        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    else:
        # Handle Unix timestamp
        return datetime.fromtimestamp(ts, tz=tz)
```

## Common Pitfalls

1. **Never use `read_file` for session files** — they are large (200K-300K chars) and contain full system prompts. Use `execute_code` with `json.loads()` per line.

2. **SESSION_META lines** — Some files contain a `SESSION_META` role line at the beginning. These are metadata markers, not actual messages.

3. **Empty lines** — Skip empty lines between JSON objects.

4. **Malformed lines** — Some lines may fail JSON parsing. Handle gracefully with try/except.

## Example

```jsonl
{"role": "SESSION_META", "timestamp": 1779098766.610738}
{"role": "user", "content": "你好", "timestamp": 1779098766.610738}
{"role": "assistant", "content": "你好！Hermes在线。", "timestamp": 1779098767.0}
```

## Correction History

**2026-05-18**: The SKILL.md frontmatter incorrectly stated session files are "standard `.json` format (single JSON object per file, NOT `.jsonl`)" — this was **WRONG**. The actual files are `.jsonl` (JSON Lines). This reference document was created to document the correct format.
