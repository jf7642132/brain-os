---
name: chronicle-agent
description: >-
  Chronicle Agent (史官) — scan recent Hermes session records across all platforms (CLI, Telegram, WeChat, etc.), extract substantive human interactions (decisions, task assignments, technical discussions, conclusions, commitment changes), and write a structured chronological log to the wiki. Use as a periodic cron job (e.g. every 2 hours) or on-demand when asked "what happened recently" / "回顾最近聊天记录".
tags: [productivity, logging, audit]
---
  Use as a periodic cron job (e.g. every 2 hours) or on-demand when asked "what happened recently" / "回顾最近聊天记录".
---

# Chronicle Agent (史官)

## Purpose

Periodically scan recent Hermes session records across all platforms (CLI, Telegram, WeChat, etc.) and produce a structured chronological log of substantive human-AI interactions — decisions, task assignments, technical discussions, important conclusions, and commitment changes. Designed to run as a cron job or on-demand.

## When to use

- Scheduled cron (every 2 hours recommended)
- User asks "what happened recently" / "回顾一下最近的聊天记录"
- User asks "what did we discuss about X across sessions"
- Generating daily activity summaries

## How it works — step by step

### Step 1: Search recent sessions

**⚠️ IMPORTANT**: The `session_search` tool is invoked directly (not via Python import). The `hermes_tools` module import will fail with `ImportError`. Always use the tool directly:

```python
# ✅ Correct - invoke tool directly
session_search(query="recent", limit=20)

# ❌ WRONG - this will fail
from hermes_tools import session_search  # ImportError!
```

This returns the most recent sessions with platform, timestamp, and summary.

**⚠️ CRITICAL**: `session_search` in cron context returns only cron sessions. User-initiated sessions (Telegram, WeChat, CLI, API server) are invisible to it. **Do not use `session_search` as the primary recall mechanism.** Use SQLite query on `state.db` as the primary method.

**⚠️ CRITICAL**: Session files in `/root/.hermes/sessions/` are **archived/historical** (weeks/months old), NOT recent sessions. Recent sessions are stored only in `state.db`. See `references/session-storage-behavior.md` for details.

### Step 2: Identify user-initiated sessions in the time window

#### 2a. Get current time window

First, get the current time and compute the 2-hour window:

```python
from datetime import datetime, timezone, timedelta
tz = timezone(timedelta(hours=8))  # CST
now = datetime.now(tz)
window_start = now - timedelta(hours=2)
window_start_ts = window_start.timestamp()
now_ts = now.timestamp()
```

#### 2b. Primary method — query sessions table

Query `state.db` directly for sessions whose `started_at` falls within the window:

```python
import sqlite3
conn = sqlite3.connect('/root/.hermes/state.db')
cur = conn.cursor()
cur.execute("""
    SELECT id, source, model, started_at, ended_at, message_count, user_id, title
    FROM sessions
    WHERE started_at >= ? AND started_at <= ?
    ORDER BY started_at ASC
""", (window_start_ts, now_ts))
sessions = cur.fetchall()
```

Filter for non-cron sources: `cli`, `telegram`, `weixin`, `discord`, `whatsapp`, `api_server` — these are real user conversations. Ignore `cron` sessions (automated tasks). Also exclude `curator` source — it's a system background skill (umbrella consolidation), not a user conversation.

#### 2c. ⚠️ CRITICAL FALLBACK — messages table timestamp query

**⚠️ Sessions with `started_at` BEFORE the window may still have user messages WITHIN the window.** Long-running CLI sessions (e.g. a single session spanning 3+ hours) are missed by the `sessions.started_at` filter because `started_at < window_start`. These sessions contain substantive user interactions that must not be ignored.

**Always run this catch-all query** to find user messages from sessions that started before the window:

```python
cur.execute("""
    SELECT DISTINCT session_id
    FROM messages
    WHERE timestamp >= ? AND timestamp <= ? AND role = 'user'
""", (window_start_ts, now_ts))
extra_session_ids = [row[0] for row in cur.fetchall()]

# Combine with sessions from 2b, deduplicate
all_session_ids = set()
for s in sessions:
    all_session_ids.add(s[0])  # s[0] is session id
for sid in extra_session_ids:
    all_session_ids.add(sid)

# Now query messages for EACH session_id found
for sid in sorted(all_session_ids):
    cur.execute("""
        SELECT content, timestamp, role
        FROM messages
        WHERE session_id = ? AND timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp ASC
    """, (sid, window_start_ts, now_ts))
    # ... process messages
```

**Implementation notes**:
- The `messages.timestamp` column stores Unix timestamps (float) for each individual message
- Use `role = 'user'` filter in the catch-all so cron/system noise doesn't inflate results
- Deduplicate against sessions already found by the Step 2b query — a session may appear in both

**⚠️ CRITICAL UPDATE (2026-05-09)**: When scanning for sessions, exclude `source='cron'` sessions that are system-generated automation tasks. Only `cli`, `telegram`, `weixin`, `discord`, `whatsapp`, and `api_server` represent user-initiated interactions. Cron sessions should be treated as noise unless they produced meaningful output (rare).

**⚠️ CRITICAL UPDATE (2026-05-18)**: Session files in `/root/.hermes/sessions/` are **archived/historical** (weeks/months old), NOT recent sessions. Do NOT use session files as the primary method for recent scans. Use `state.db` for all recent time-window queries. Session files should only be used as fallback for historical context or when `state.db` is unavailable.

**⚠️ CRITICAL: Session files are `.jsonl` (JSON Lines) format, NOT `.json`. Each line is a separate message object.**

**Parsing pattern**:
```python
from pathlib import Path
import json

sessions_dir = Path("/root/.hermes/sessions")
for f in sessions_dir.glob("*.jsonl"):
    with open(f, 'r', encoding='utf-8') as fp:
        for line_num, line in enumerate(fp, 1):
            data = json.loads(line)  # Parse each line as separate message
            # Process data
```

**See `references/session-file-format.md` for complete session file parsing pattern including timezone handling.**

**See `references/state-db-schema.md` for database schema, query patterns, and api_server session behavior.**

**Critical implementation pattern**: Always use `execute_code` with `json.loads()` per line for programmatic parsing of session files — NEVER use `read_file`. Session files are 200K-300K chars and contain full system prompts/tool lists. Files are `.jsonl` (JSON Lines), each line is a separate message object.

**See `references/session-file-format.md` for complete parsing pattern including timezone handling.**

### Step 3: Extract full message content via SQLite (primary method)

**Critical**: `session_search()` returns session metadata (IDs, timestamps, summaries) but NOT actual message content. Content is stored in:
1. **Primary**: `/root/.hermes/state.db` SQLite database (`messages` table)
2. **Secondary**: `/root/.hermes/sessions/session_{session_id}.json` files (only if they exist)

Use `execute_code` to query `state.db` directly — this gives you per-message content AND per-message timestamps:

```python
import sqlite3, json
from datetime import datetime, timezone, timedelta

tz = timezone(timedelta(hours=8))
conn = sqlite3.connect('/root/.hermes/state.db')
cur = conn.cursor()

# For each session_id found in Step 2:
session_id = "20260425_..."  # partial match with LIKE

# Get user messages (the key data)
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'user'
    ORDER BY timestamp ASC
""", (session_id + '%',))
for content, ts in cur.fetchall():
    dt = datetime.fromtimestamp(ts, tz=tz).strftime('%H:%M:%S')
    print(f"[USER {dt}] {content[:500]}")

# Get assistant responses (non-tool-call messages for content)
cur.execute("""
    SELECT content, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'assistant'
      AND (tool_calls IS NULL OR tool_calls = '')
    ORDER BY timestamp ASC
""", (session_id + '%',))
for content, ts in cur.fetchall():
    dt = datetime.fromtimestamp(ts, tz=tz).strftime('%H:%M:%S')
    print(f"[ASSISTANT {dt}] {content[:600]}")

# Optionally get tool call names (for reconstructing actions)
cur.execute("""
    SELECT tool_calls, timestamp
    FROM messages
    WHERE session_id LIKE ? AND role = 'assistant'
      AND tool_calls IS NOT NULL AND tool_calls != ''
    ORDER BY timestamp ASC
""", (session_id + '%',))
for tc_json, ts in cur.fetchall():
    dt = datetime.fromtimestamp(ts, tz=tz).strftime('%H:%M:%S')
    tc = json.loads(tc_json)
    for call in tc:
        fn = call.get('function', {}).get('name', '?')
        print(f"  [TOOL {dt}] {fn}")
```

### Step 4: Filter for substantive content

**Critical**: Only user-initiated messages should be considered for substantive content. Tool-call outputs and assistant tool-call responses are system-generated automation artifacts, NOT substantive human interactions.

From extracted messages, keep only:
- ✅ **User messages** that contain substantive content (decisions, tasks, technical discussions, conclusions, commitment changes)
- ✅ **Assistant non-tool-call responses** that contain substantive content

Filter out:
- ❌ Tool-call outputs (`role='tool'`) — these are system execution artifacts
- ❌ Assistant messages with tool_calls — these are automation responses
- ❌ 闲聊、问候、表情包 ("你好", "谢谢", "好的", "没问题")
- ❌ 无意义的简短应答 ("收到", "明白了", "好的")
- ❌ 系统自动提示/Auto-generated messages
- ❌ `[SYSTEM: You are running as a scheduled cron job...]` headers
- ❌ Context compaction notes (`[CONTEXT COMPACTION — REFERENCE ONLY]`)
- ❌ Session continuation markers ("继续", "接着说")

**Filtering implementation**:
```python
import re

def is_substantive(content, role):
    # CRITICAL: Only user messages or assistant non-tool-call responses are substantive
    if role == 'tool':
        return False
    if role == 'assistant':
        # Assistant messages with tool_calls are automation responses, not substantive
        # (tool_calls field exists and is non-empty)
        return False
    
    if not content or len(content) < 50:
        return False
    
    # Filter system messages
    if '[SYSTEM:' in content or 'You are running as a scheduled cron job' in content:
        return False
    
    # Filter context compaction notes
    if '[CONTEXT COMPACTION' in content:
        return False
    
    # Filter greetings/chitchat (case-insensitive)
    chitchat_patterns = [
        r'^你好', r'^hello', r'^hi',  # Greetings
        r'谢谢', r'thanks', r'great', r'awesome', r'perfect',  # Gratitude/positive
        r'收到', r'明白了', r'好的', r'没问题',  # Acknowledgments
        r'继续', r'接着说',  # Continuation markers
    ]
    if any(re.search(p, content, re.IGNORECASE) for p in chitchat_patterns):
        return False
    
    return True
```

**Categorization keywords** (for event type classification):
- **Decisions**: "decision", "decided", "选择", "决定", "确定", "方案", "配置"
- **Tasks**: "task", "assign", "todo", "需要", "应该", "创建", "部署", "生成"
- **Technical**: "technical", "code", "api", "error", "fix", "bug", "implementation", "技术", "代码", "错误", "修复", "排查", "分析"
- **Conclusions**: "conclusion", "summary", "report", "完成", "结果", "发现", "结论", "生成", "提交"
- **Changes**: "update", "change", "modify", "改进", "更新", "修改", "调整", "变更"

## Pitfalls

1. **Use direct file scan, not session_search**: In cron context, `session_search` returns only cron sessions. Direct file scan of `/root/.hermes/sessions/` by mtime is the only reliable method. See "Step 1: Direct file scan" above.

2. **Session files are `.jsonl` (JSON Lines), NOT `.json`**: Each line is a separate message object. **⚠️ CRITICAL FIX (2026-05-18)**: The SKILL.md frontmatter previously incorrectly stated session files are "standard `.json` format (single JSON object per file, NOT `.jsonl`)" — this was **WRONG**. The actual files are `.jsonl`. Always use `json.loads()` per line, never `read_file` for session files (they are large and contain full system prompts).

3. **⚠️ CRITICAL: Session files are archived, not recent**: The `/root/.hermes/sessions/` directory contains **archived/historical sessions** (weeks/months old), NOT recent sessions. Recent sessions (last 24-48 hours) are stored only in `state.db`. **Always query `state.db` for recent time-window scans**. Session files should only be used as fallback for historical context or when `state.db` is unavailable. See `references/session-storage-behavior.md` for details.

4. **Per-message timestamps exist in SQLite**: The `messages.timestamp` column is a Unix timestamp (float). Convert with `datetime.fromtimestamp(ts, tz=tz)`.

4. **Memory is limited**: The agent's long-term memory (2,200 chars) fills up quickly. Don't try to save Chronicle techniques to memory — save as a skill instead.

5. **Cron sessions are noise**: Ignore sessions from `source='cron'` unless they produced meaningful output (rare). Focus on `cli`, `telegram`, `weixin`, `api_server` sources.

6. **⚠️ CRITICAL: Exclude cron sessions during filtering**: When scanning sessions, explicitly exclude `source='cron'` sessions as they are system-generated automation tasks, not user-initiated interactions. Only `cli`, `telegram`, `weixin`, `discord`, `whatsapp`, and `api_server` represent real user conversations.

7. **api_server sessions capture Web UI interactions**: Sessions from Hermes Dashboard Web UI show up with `source='api_server'`. Session IDs can be UUIDs (`16742469-6ea5-4635-9cf8-ea645aa7242d`), `eph_*`, or `api-*`. Query with LIKE match, not exact prefix — the ID format varies.

   **⚠️ CRITICAL PITFALL: api_server sessions may be context compaction checkpoints**: Web UI sessions may contain only system-generated context summaries (not actual user conversations). When this happens:
   - User message contains system instruction: "You are a summarization agent creating a context checkpoint..."
   - Assistant message contains structured summary (Active Task, Goal, Constraints, Completed Actions)
   - These are **NOT substantive user interactions** and should be filtered out
   - See `references/session-storage-behavior.md` for detection pattern

   **⚠️ CRITICAL PITFALL: api_server sessions may have NO user messages in `state.db`**: Hermes Dashboard Web UI sessions may only store assistant (with `tool_calls`) and tool messages — user messages can be completely absent in the `messages` table. When this happens:
   - You cannot extract the user's actual intent, decision, or task assignment
   - You can *infer* activity from assistant final responses (those with `finish_reason='stop'` and no `tool_calls`), but note these are speculative — log them as "从 assistant 响应推断" with appropriate caveats
   - Check `content` length: if the only non-tool messages are assistant `finish_reason='stop'` messages, you're in this situation
   - Add a note in the Chronicle log explaining the limitation so the user knows Web UI conversations aren't being fully captured
   - This is a known limitation of the Web UI gateway — it may not persist user messages to state.db
   
   **See `references/state-db-schema.md` for detection pattern and query examples.**

8. **Duplicate sessions across context compaction**: The same Telegram/WeChat conversation may spawn multiple session files due to context compression (titles like "当前使用模型 #2", "#3", "#4"). These are consecutive segments of the same discussion. Deduplicate by checking user messages for "继续" (continue) or context compaction markers.

9. **CONTEXT COMPACTION marker**: Assistant responses containing `[CONTEXT COMPACTION — REFERENCE ONLY]` are handoff notes from context compression — do NOT treat these as new content. The real content is in the user messages that follow.

10. **[SILENT] protocol + Empty window handling**: These two rules work together:
    - **Write the log file** to `/root/.hermes/knowledge/09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md` with a minimal status message explaining the empty window (scan timestamp, window, "无实质性内容" section).
    - **Commit the log file** to git as normal.
    - **Respond with `[SILENT]`** (exactly this, nothing else) to suppress delivery to the user. The log file exists for record-keeping; the user doesn't need a report when there's nothing to report.
    - **Never combine [SILENT] with content** — either produce a full report (when substantive content exists) or `[SILENT]` (when empty).
    
    **Decision tree**:
    - Substantive content found → write detailed log + full report response
    - No substantive content → write minimal log + `[SILENT]` response

11. **Empty window log format**: When no substantive content is found, the log file should include:
    - Scan timestamp and window in header
    - Session source statistics (cron vs non-cron counts)
    - Clear "无实质性内容" section explaining only cron/system messages were present
    - Git commit with `auto: Chronicle Agent scan YYYY-MM-DD HH:MM`

12. **Session files with offset-aware timestamps**: Some session files contain ISO timestamps with timezone info (e.g., `2026-05-04T01:06:04.804275Z`). When parsing, use `datetime.fromisoformat(session_start.replace('Z', '+00:00'))` then convert to local timezone with `.astimezone(tz).replace(tzinfo=None)` to ensure naive datetime comparison works correctly.

13. **state.db schema may vary**: Some SQLite queries have failed with errors like `no such column: session_id` or `no such column: created_at`. The schema is not guaranteed to be stable. **Always fall back to session files** if `state.db` queries fail. See `references/state-db-schema.md` for the complete session file parsing pattern.

14. **session_search import will fail**: The `session_search` tool is invoked directly, NOT via Python import. Attempting `from hermes_tools import session_search` will raise `ImportError`. Always use the tool directly:
    ```python
    session_search(query="recent", limit=20)  # ✅ Correct
    ```

**⚠️ session_search returns summaries only, not full content**: The `session_search` tool returns session metadata (IDs, timestamps, summaries) but the summaries are often truncated or empty for cron sessions. When `session_search` returns only cron sessions or empty summaries, **do not stop** — this is expected behavior for cron context. Proceed to Step 1 (SQLite query on state.db) to find any user sessions. In practice, `session_search` is blind to user sessions when running in cron context — it only sees other cron tasks. This is not a failure state; it means there may be no user conversations, which is a valid result.

**⚠️ CRITICAL: session_search is blind to user sessions in cron context**: When running as a cron job, `session_search` almost exclusively returns other cron sessions. User-initiated sessions (Telegram, WeChat, CLI, API server) are completely invisible to it. **Do not use session_search as the primary recall mechanism.** Use direct SQLite query on `state.db` as the primary method — this catches ALL user sessions regardless of indexing status.

15. **⚠️ CRITICAL: Long-running sessions may be missed by `sessions.started_at` filter**. A CLI session that started at 13:04 and spans 3+ hours will NOT be found by `WHERE started_at >= window_start_ts` when your window is 13:52-15:52. Yet this session may contain user messages at 15:49, well within the window. **Always run the Step 2c messages-table catch-all** as a mandatory second pass. Do not stop after Step 2b — you will miss substantive content. \
    \
    **Real-world example** from 2026-05-20: A CLI session `20260518_130337_f833b9` started at 13:04 and had user messages at 15:49. The Step 2b sessions query (window 13:52-15:52) did not return it. Only the messages-table timestamp catch-all (`SELECT DISTINCT session_id FROM messages WHERE timestamp >= ? AND timestamp <= ? AND role = 'user'`) found it.

16. **⚠️ CRITICAL: Check if target log file already exists before writing**. The output path uses a fixed hour-based filename (`09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md`). If a file with the same hour already exists (e.g., from a previous scan that ran early or overlapped), overwriting it will DESTROY the previous scan's output.  \
    **Always check first**: `ls -la /root/.hermes/knowledge/09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md`  \
    **If it exists**: Use a different hour suffix (e.g., if the 21.md was already written for 21:00-23:00 and your window overlaps to 23:14, write to 23.md instead). Do NOT overwrite.  \
    **Recovery if you already overwrote**: `cd /root/.hermes/knowledge && git checkout <commit_hash> -- "09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md"` — find the last commit that touched the file with `git log --oneline -- "09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md"`.

## Verification checklist

- [ ] Step 2b sessions table query ran (non-cron sessions in window)
- [ ] Step 2c messages table catch-all ran (catches sessions that started before the window)
- [ ] All session IDs from both queries checked and deduplicated
- [ ] api_server sessions inspected for user messages (may be absent — see pitfall #7)
- [ ] User messages extracted from session JSON files (not summaries)
- [ ] Substantive content identified (decisions, tasks, discussions)
- [ ] Filters applied (noise removed)
- [ ] Log file written to correct wiki path (check no overwrite of existing file)
- [ ] Git committed
- [ ] Output follows Markdown format with session metadata and event categorization

## Support Files

- `references/directory-structure-migration.md` — **新增**: 目录结构迁移记录（2026-05-19 输出路径从 `03-个人运营/05-频道历史` 迁移至 `09-personal-ops/05-channel-history`）
- `references/session-storage-behavior.md` — **Critical**: Session file archival behavior and api_server context compaction checkpoint pattern
- `references/session-search-behavior.md` — `session_search` tool behavior reference
- `references/sqlite-message-extraction.md` — SQLite message extraction patterns
- `references/log-format.md` — Chronicle log format specification
- `references/session-file-format.md` — Session file parsing pattern
- `references/state-db-schema.md` — Database schema and query patterns
- `references/todo-validation-workflow.md` — **新增**: 待办验证工作流（来自 `personal-ops-driver` 技能）

## Scripts

- `scripts/extract-chronicle-todos.py` — 从史官记录中提取待办事项的脚本，支持从"未解决"和"决策"部分提取高质量待办，去重后写入 todo-backlog.md。
- `scripts/chronicle-commit.sh` — Chronicle 日志提交脚本

## Todo 提取（新增 2026-05-18）

### 从史官记录提取待办

Chronicle Agent 除了记录会话历史外，还可以从史官记录中提取待办事项：

**触发条件**：
- 史官记录文件包含"未解决"或"决策"部分
- 用户要求"提取史官记录中的待办"
- 作为 Brain OS P2 阶段任务运行

**提取模式**：

| 模式 | 说明 |
|------|------|
| **未解决部分** | 从"## 未解决"章节提取待办（最准确） |
| **决策部分** | 从"## 决策"章节提取后续行动项 |
| **全文扫描** | 扫描全文寻找待办关键词（噪音较高） |

**推荐模式**：优先提取"未解决"和"决策"部分，噪音最低。

**提取脚本**：
```bash
python3 ~/.hermes/scripts/extract-chronicle-todos.py
```

**输出**：
- 写入 `todo-backlog.md`（待办列表）
- 写入 `dialogue-mining-tracker.md`（提取日志）

**分类体系**：
```
bug | config | deploy | docs | feature | general | meeting | ops | research | test
```

**状态体系**：
```
待执行 | 待确认 | 进行中 | 阻塞 | 已解决
```

**⚠️ 噪音过滤**：
- 跳过 Markdown 标题（`#`, `##`, `###`）
- 跳过纯描述性内容（不含行动动词）
- 跳过系统输出（频道日志、会话来源、技术栈介绍等）
- 只保留含行动关键词的条目（需要/应该/必须/修复/更新/优化等）

### 待办数据流

史官待办提取的完整数据流：

| 阶段 | 数量 | 说明 |
|------|------|------|
| 史官扫描 149 个文件 | 6106 条 | 初步提取（含大量重复） |
| 去重后 | 4218 条 | 仍含冗余 |
| 精准模式 1 | 71 条 | 第一次筛选 |
| 精准模式 2 | 65 条 | 第二次筛选 |
| 最终有效待办 | 21 条 | 去重合并后 |

**⚠️ 重要**: 史官提取的待办包含大量重复/冗余记录，**处理前必须验证问题是否仍存在**（见 `personal-ops-driver` 技能的 `references/todo-validation-workflow.md`）。

### Todo Backlog 文件结构演进

2026-05-19 后，`todo-backlog.md` 被重构为分片归档结构：

| 文件 | 内容 |
|------|------|
| `06-context/todo-tracking/todo-backlog.md` | 活跃待办（仅 open/in_progress） |
| `06-context/todo-tracking/archive/YYYY-MM.md` | 已完成/已解决待办归档 |
| `06-context/todo-tracking/tracker/todo-tracker.md` | 统计信息 |

**Git 历史恢复**: 如果待办数据被归档/重构，使用 `git log -p` 恢复历史内容：
```bash
cd /root/.hermes/knowledge
git log --all -p -- 06-context/todo-tracking/todo-backlog.md
```

**⚠️ 用户偏好**: 用户明确要求"处理前先核验证该待办问题是否还存在"，这是第一优先级规则。

## Cron job setup

Schedule: `0 */2 * * *` (every 2 hours) or `30 */2 * * *`

Prompt template:
```
作为 Chronicle Agent（史官），扫描最近2小时的聊天记录，提取实质性内容：

提取要求：
- 只记录：决策、任务分配、技术讨论、重要结论、承诺变更
- 过滤：闲聊、表情包、无意义插话
- 不评论、不干预，只记录

输出到：09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md

工作目录：/root/.hermes/knowledge
```

Output path:
```
/root/.hermes/knowledge/09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md
```

**⚠️ 目录结构变更 (2026-05-19)**: 输出路径已从 `03-个人运营/05-频道历史` 迁移至 `09-personal-ops/05-channel-history`。历史文件仍保留在原路径，新扫描应写入新路径。

**⚠️ Note**: The nightly digest (conversation mining output) goes to a different location:
```
/root/.hermes/knowledge/04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-YYYY-MM-DD.md
```

Format:
```markdown
# Chronicle Agent 扫描报告
**扫描时间**: YYYY-MM-DD HH:MM
**窗口**: YYYY-MM-DD HH:MM - YYYY-MM-DD HH:MM

---

## 1. [Platform] · [Topic] (HH:MM-HH:MM)

**会话**: [Platform] / [Model]
**用户**: [User name if available]

**事件**:
- ...

**技术分析**:
- ...

**决策与解决**:
- ✅ ...

---

## 2. [Platform] · [Topic] (HH:MM-HH:MM)

...
```

### Step 5: Git commit

```bash
cd /root/.hermes/knowledge
git add -A
git commit -m "auto: Chronicle Agent scan YYYY-MM-DD HH:MM"
```