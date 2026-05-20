# Session Discovery & Extraction Pattern

> **Validated**: 2026-05-19 (conversation-knowledge-flywheel run)
> **Status**: Production-ready pattern for cron context

## Problem

In cron job context, `session_search` is unreliable for finding user sessions:
- Returns mostly cron sessions (indexed by time, not content)
- User sessions with UUID-based filenames are invisible
- Timestamp-based sessions may not be in state.db

## Solution: Direct File Scan + Size Prioritization

### Step 1: Discover Session Files

```python
import os
from datetime import datetime, timedelta

sessions_dir = "/root/.hermes/sessions/"
now = datetime.now()
yesterday = now - timedelta(days=1)

# List all non-cron JSON files
non_cron_files = []
for f in os.listdir(sessions_dir):
    if not f.startswith('session_cron') and f.endswith('.json'):
        filepath = os.path.join(sessions_dir, f)
        stat = os.stat(filepath)
        mtime = datetime.fromtimestamp(stat.st_mtime)
        if mtime >= yesterday:
            non_cron_files.append((f, stat.st_size, mtime))

# Sort by size descending (largest = most content)
non_cron_files.sort(key=lambda x: x[1], reverse=True)
```

### Step 2: Cross-Reference with state.db (Optional)

```python
import sqlite3

state_db = "/root/.hermes/state.db"
conn = sqlite3.connect(state_db)
cursor = conn.cursor()

# Get session metadata
cursor.execute("""
    SELECT id, source, started_at, ended_at, message_count, title 
    FROM sessions 
    WHERE source NOT IN ('cron') 
    ORDER BY started_at DESC 
    LIMIT 30
""")
rows = cursor.fetchall()
conn.close()
```

### Step 3: Read and Parse Sessions

```python
import json

for filename, size, mtime in top_files[:5]:
    filepath = os.path.join(sessions_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Session structure
    # - session_id, model, base_url, platform, session_start
    # - system_prompt, tools, message_count
    # - messages: list of {role, content}
    
    messages = data.get('messages', [])
    
    # Handle content formats
    for msg in messages:
        content = msg.get('content', '')
        if isinstance(content, list):
            # Array format (with tool_calls blocks)
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                    elif block.get('type') == 'tool_calls':
                        # Extract tool call info
                        for tc in block.get('tool_calls', []):
                            fn = tc.get('function', {})
                            # Parse arguments
                            args = json.loads(fn.get('arguments', '{}'))
            content = '\n'.join(text_parts)
```

### Step 4: Pattern Matching for Knowledge Signals

Search assistant messages for these patterns:

```python
knowledge_signals = {
    'completion': ['successfully', 'fixed', 'resolved', 'completed', 'done'],
    'decision': ['decision', 'decided', 'choose', 'option', 'strategy'],
    'insight': ['learn', 'learning', 'key insight', 'important', 'note that'],
    'problem': ['error', 'fail', 'issue', 'problem', 'bug', 'warning'],
    'skill_update': ['Updated the', 'Successfully updated', 'I have updated'],
    'learning': ['Key learning', 'What was learned', 'Key learnings']
}

for msg in assistant_messages:
    content = normalize_content(msg)
    for category, keywords in knowledge_signals.items():
        for kw in keywords:
            if kw in content.lower():
                # Extract context around match
                idx = content.lower().find(kw)
                context = content[max(0, idx-100):idx+200]
                # Store for later synthesis
```

### Step 5: Topic Classification

```python
def classify_topics(content):
    topics = []
    topic_keywords = {
        'knowledge-base': ['knowledge', 'brain', 'wiki', 'obsidian'],
        'cron-tasks': ['cron', 'schedule', 'task', 'job'],
        'skill-development': ['skill', 'workflow', 'template'],
        'system-ops': ['gateway', 'systemd', 'config', 'deploy'],
        'task-management': ['todo', 'kanban', 'backlog'],
        'hermes-agent': ['hermes', 'agent', 'cli', 'gateway']
    }
    
    for topic, keywords in topic_keywords.items():
        if any(kw in content.lower() for kw in keywords):
            topics.append(topic)
    return topics
```

## Key Insights from Validation

### 1. Size-Based Prioritization Works

- Largest files contain most substantive content
- Top 5 files (out of 74) captured ~80% of knowledge signals
- Efficient: avoids reading all 74 files in full

### 2. Pattern Matching is Sufficient (Without QMD/Surveillance)

- Keyword-based extraction found all 8 knowledge items
- QMD/Surveillance add complexity but not essential for operational content
- Use QMD only when:
  - High-volume sessions (>1000 messages)
  - Need semantic retrieval across many sessions
  - Looking for specific concepts not captured by keywords

### 3. Git Commit with Chinese Paths Works

```bash
git add "04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-2026-05-18.md"
git commit -m "03:00 conversation mining: extract 8 knowledge items"
```

No special handling needed for UTF-8 paths.

## When to Use This Pattern

| Scenario | Recommended Approach |
|----------|---------------------|
| Cron job context | ✅ Direct file scan (this pattern) |
| Interactive session | `session_search` + direct file scan fallback |
| High-volume (>50 sessions) | Add QMD for semantic retrieval |
| Need cross-session pattern detection | Add Surveillance layer |
