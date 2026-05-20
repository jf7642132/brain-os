# Session File Format Handling

> Validated: 2026-05-19 observer fix + 2026-05-20 conversation mining

## Problem

Hermes Agent stores sessions in `.json` format (single JSON object), but some skills expected `.jsonl` format (one JSON object per line). This caused session discovery failures.

## Solution

Handle both formats:

```python
import os
import json

def parse_session_file(filepath):
    """Parse session file handling both .json and .jsonl formats."""
    
    if filepath.endswith('.jsonl'):
        # JSONL format: each line is a JSON object
        sessions = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip():
                    sessions.append(json.loads(line))
        return sessions
    
    elif filepath.endswith('.json'):
        # JSON format: single JSON object (Hermes Agent session)
        with open(filepath, 'r') as f:
            data = json.load(f)
        return [data]  # Wrap in list for consistent processing
    
    return []
```

## Detection Logic

```bash
# Check both extensions
ls ~/.hermes/sessions/*.json 2>/dev/null
ls ~/.hermes/sessions/*.jsonl 2>/dev/null

# In Python
if session_file.endswith('.jsonl'):
    # Process as JSONL
elif session_file.endswith('.json'):
    # Process as single JSON object
```

## Session File Naming Patterns

| Pattern | Format | Source |
|---------|--------|--------|
| `session_YYYYMMDD_HHMMSS_*.json` | JSON | CLI, Telegram, WeChat |
| `session_<uuid>.json` | JSON | API Server, Web UI |
| `session_cron_*_YYYYMMDD_HHMMSS.json` | JSON | Cron tasks |
| `YYYYMMDD_HHMMSS_*.jsonl` | JSONL | Legacy format |

## Date Fallback

When no sessions found for today, fall back to yesterday:

```python
from datetime import datetime, timedelta

today_date = datetime.now().strftime("%Y%m%d")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

# Try today first
today_sessions = [f for f in os.listdir(sessions_dir) 
                  if f.startswith(f"session_{today_date}") or f.startswith(f"{today_date}_")]

if not today_sessions:
    # Fall back to yesterday
    today_sessions = [f for f in os.listdir(sessions_dir) 
                      if f.startswith(f"session_{yesterday_date}") or f.startswith(f"{yesterday_date}_")]
    report_date = yesterday_date
else:
    report_date = today_date
```

## Verification

After implementing format handling, verify:

```bash
# Check session files exist
ls -la ~/.hermes/sessions/*.json | head -5

# Verify parsing works
python3 -c "
import json, os
for f in os.listdir('~/.hermes/sessions/')[:3]:
    if f.endswith('.json'):
        path = os.path.join('~/.hermes/sessions/', f)
        with open(path) as fp:
            data = json.load(fp)
            print(f'{f}: session_id={data.get(\"session_id\", \"N/A\")}')
"
```