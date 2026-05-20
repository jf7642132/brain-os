# Session File Format Detection

## Problem

Hermes Agent stores session files in multiple formats depending on the context:

| Format | Extension | Structure | Use Case |
|--------|-----------|-----------|----------|
| **JSON (single object)** | `.json` | Single JSON object with `session_id`, `model`, `tools`, etc. | Interactive sessions, API server sessions |
| **JSONL (line-delimited)** | `.jsonl` | Each line is a separate JSON object | Structured logging, batch processing |
| **Conversation format** | `.jsonl` | Contains `role`, `content`, `timestamp` fields | Dialogue records (not for stats extraction) |

## Detection Pattern

```python
import os, json

def detect_session_format(filepath):
    """Detect session file format and return parser function."""
    if filepath.endswith('.jsonl'):
        return parse_jsonl_session
    elif filepath.endswith('.json'):
        return parse_json_session
    else:
        raise ValueError(f"Unknown session format: {filepath}")

def parse_json_session(filepath):
    """Parse single JSON object session (Hermes Agent format)."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    # Extract: session_id, model, session_start, last_updated, tools, etc.
    return {
        'session_id': data.get('session_id'),
        'model': data.get('model'),
        'session_start': data.get('session_start'),
        'last_updated': data.get('last_updated'),
        'is_error': data.get('isError', False),
        'tools': data.get('tools', []),
    }

def parse_jsonl_session(filepath):
    """Parse JSONL session (each line is a JSON object)."""
    records = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                records.append(data)
    return records
```

## Shell Pattern for Cron Jobs

```bash
# Check both .json and .jsonl extensions
TODAY_DATE=$(date +%Y%m%d)
YESTERDAY_DATE=$(date -d "yesterday" +%Y%m%d)

TODAY_SESSIONS_JSON=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.json 2>/dev/null | wc -l)
TODAY_SESSIONS_JSONL=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.jsonl 2>/dev/null | wc -l)
TOTAL_TODAY=$((TODAY_SESSIONS_JSON + TODAY_SESSIONS_JSONL))

if [ "$TOTAL_TODAY" -eq 0 ]; then
    # Fallback to yesterday
    SESSIONS=$(ls ~/.hermes/sessions/${YESTERDAY_DATE}_*.json 2>/dev/null; ls ~/.hermes/sessions/${YESTERDAY_DATE}_*.jsonl 2>/dev/null)
    REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
else
    SESSIONS=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.json 2>/dev/null; ls ~/.hermes/sessions/${TODAY_DATE}_*.jsonl 2>/dev/null)
    REPORT_DATE=$(date +%Y-%m-%d)
fi
```

## Pitfalls

### Pitfall 1: Assuming .jsonl Only

**Problem**: Observer skill originally only checked `.jsonl` files.

**Impact**: Cron jobs running at 00:30 found no sessions (Hermes stores as `.json`), fell back to yesterday's data, generating stale reports.

**Fix**: Always check both `.json` and `.jsonl` extensions.

### Pitfall 2: JSONL vs Conversation Format

**Problem**: Both use `.jsonl` extension but have different structures.

**Detection**: Check first line's keys:
```python
with open(session_file, 'r') as f:
    first_line = json.loads(f.readline())
    if 'type' not in first_line and 'role' in first_line:
        # Conversation format — cannot extract structured stats
        print("Session file is in conversation format, skipping structured analysis")
```

### Pitfall 3: Empty Files

**Problem**: Some session files may be empty or truncated.

**Fix**: Always check file size before parsing:
```bash
if [ -s "$session_file" ]; then
    # File has content, safe to parse
else
    echo "Empty session file: $session_file"
fi
```

## Session Date Fallback Logic

When running as a cron job early in the day before any sessions are created:

1. Check today's sessions (both `.json` and `.jsonl`)
2. If none found, fall back to yesterday's sessions
3. If neither today nor yesterday has sessions, fall back to the most recent available session data
4. Report date should reflect the actual data date, not the calendar date

```python
from datetime import datetime, timedelta
import os

today_date = datetime.now().strftime("%Y%m%d")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
sessions_dir = os.path.expanduser("~/.hermes/sessions/")

# Check both formats
today_sessions = [
    f for f in os.listdir(sessions_dir)
    if f.startswith(today_date) and (f.endswith('.jsonl') or f.endswith('.json'))
]

if not today_sessions:
    # Fallback to yesterday
    today_sessions = [
        f for f in os.listdir(sessions_dir)
        if f.startswith(yesterday_date) and (f.endswith('.jsonl') or f.endswith('.json'))
    ]
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
else:
    report_date = datetime.now().strftime("%Y-%m-%d")
```

## Telegram Delivery Issue (2026-05-19)

### Problem

Observer cron job configured with `deliver: telegram` and `telegram_chat_id: <YOUR_TELEGRAM_CHAT_ID>` failed with:

```
Forbidden: the bot can't send messages to the bot
```

### Root Cause

The `telegram_chat_id` was a bot's chat ID, not a user's. Telegram bots cannot send messages to other bots.

### Solution

Change delivery target:

```json
{
  "deliver": "local",
  "telegram_chat_id": null
}
```

Or configure a user/group chat ID:

```json
{
  "deliver": "telegram",
  "telegram_chat_id": "<YOUR_TELEGRAM_CHAT_ID>"  // User's chat ID, not bot's
}
```

### Verification

After fix, observer cron job should:
1. Successfully detect `.json` session files
2. Generate iteration plan without falling back to yesterday's data
3. Deliver summary to local channel (or correct Telegram target)

## Related Skills

- `observer` — Uses this pattern for session data collection
- `chronicle-agent` — May also need session format detection
