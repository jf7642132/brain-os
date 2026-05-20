# Session Discovery & Knowledge Extraction Workflow

> Validated: 2026-05-20 conversation mining session
> Source: `session_20260519_162845_e16035.json`, `session_20260519_122546_603e38.json`, `session_20260519_111159_790784.json`

## Validated Workflow

### Step 1: Discover Recent Sessions

```python
import os
import time
from datetime import datetime

sessions_dir = "/root/.hermes/sessions"
now = time.time()
threshold = now - 86400  # 24 hours

# List all non-cron session files
recent_files = []
for f in os.listdir(sessions_dir):
    if f.endswith('.json') and 'cron' not in f:
        filepath = os.path.join(sessions_dir, f)
        file_epoch = os.path.getmtime(filepath)
        if file_epoch > threshold:
            size = os.path.getsize(filepath)
            recent_files.append((filepath, size, file_epoch))

# Sort by modification time (most recent first)
recent_files.sort(key=lambda x: x[2], reverse=True)
```

### Step 2: Prioritize by Size

```python
# Sort by size (largest first) - largest sessions contain most content
recent_files.sort(key=lambda x: x[1], reverse=True)

# Read top N largest sessions for deep analysis
for filepath, size, epoch in recent_files[:5]:
    # Parse and extract knowledge items
```

### Step 3: Filter by Time Window (Epoch-Based)

```python
# More robust than -mmin approach
current_epoch = int(time.time())
for f in os.listdir(sessions_dir):
    if f.endswith('.json') and 'cron' not in f:
        filepath = os.path.join(sessions_dir, f)
        file_epoch = os.path.getmtime(filepath)
        hours_since = (current_epoch - file_epoch) / 3600
        if hours_since < 24:
            # Process this file
```

### Step 4: Extract Knowledge from Assistant Messages

```python
import json

with open(filepath, 'r') as f:
    data = json.load(f)

messages = data.get('messages', [])
knowledge_items = []

for msg in messages:
    if msg.get('role') == 'assistant':
        content = msg.get('content', '')
        if isinstance(content, str):
            # Skill update patterns
            if any(kw in content for kw in ['Updated the', 'Successfully updated', 'I have updated']):
                knowledge_items.append({
                    'type': 'skill_update',
                    'content': content[:500]
                })
            # Learning patterns
            elif any(kw in content for kw in ['Key learning', 'What was learned', 'Key learnings']):
                knowledge_items.append({
                    'type': 'learning',
                    'content': content[:500]
                })
            # Fix/patch patterns
            elif any(kw in content for kw in ['patched', 'fixed', 'created', 'written']):
                knowledge_items.append({
                    'type': 'system_change',
                    'content': content[:500]
                })
```

### Step 5: Cross-Reference with state.db

```python
import sqlite3

db_path = '/root/.hermes/state.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get session metadata
cursor.execute("""
    SELECT id, source, started_at, ended_at, message_count, title
    FROM sessions
    WHERE source NOT IN ('cron')
    ORDER BY started_at DESC
    LIMIT 30
""")

sessions_metadata = cursor.fetchall()
conn.close()
```

## Cron Task Filtering Patterns

| Pattern | Description | Action |
|---------|-------------|--------|
| `session_cron_*` | General cron task sessions | Skip |
| `session_cron_ce8a1963857a` | Chronicle Agent's own cron tasks | Skip |
| `session_YYYYMMDD_HHMMSS_*` | Timestamp-based user sessions | Process |
| `session_<uuid>.json` | UUID-based user sessions (API server) | Process |

## Knowledge Extraction Patterns

| Pattern | Type | Example |
|---------|------|---------|
| `Updated the` | skill_update | "Updated the SKILL.md in skill 'cron-kanban-integration'" |
| `Successfully updated` | skill_update | "Successfully updated the skill library" |
| `Key learning` | learning | "Key learning: TODO_PATH configuration error" |
| `What was learned` | learning | "What was learned: session format mismatch" |
| `patched` | system_change | "Patched SKILL.md in skill 'observer'" |
| `fixed` | system_change | "Fixed TELEGRAM_HOME_CHANNEL configuration" |
| `created` | system_change | "Created new skill 'telegram-channel-troubleshooting'" |
| `written` | system_change | "File written to references/..." |

## Session File Format Detection

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

## Output Manifest Format

```json
{
  "date": "YYYY-MM-DD",
  "generated_at": "YYYY-MM-DDTHH:MM:SS+08:00",
  "source_dir": "/root/.hermes/sessions",
  "sessions_scanned": 70,
  "sessions_analyzed": 3,
  "knowledge_items": [
    {
      "type": "skill_update",
      "skill": "cron-kanban-integration",
      "action": "patch",
      "summary": "Description of change",
      "session": "session_filename.json"
    }
  ],
  "files_written": [
    {
      "path": "relative/path/to/file.md",
      "type": "machine_report|human_digest",
      "size_bytes": 1234
    }
  ],
  "git_commit": "abc123",
  "status": "success"
}
```

## Validation Checklist

After running conversation mining:

- [ ] Session files discovered (count matches expected)
- [ ] Time window filtering applied (epoch-based)
- [ ] Cron sessions excluded (`session_cron_*` patterns)
- [ ] Knowledge items extracted with patterns
- [ ] Manifest JSON written to `/tmp/`
- [ ] Machine report written to `04-知识库/99-系统/03-集成报告/YYYY-MM-DD/`
- [ ] Human digest written to `04-知识库/01-阅读消化/04-摘要汇总/`
- [ ] Git commit created
- [ ] Files verified visible (`git status --short` shows clean)