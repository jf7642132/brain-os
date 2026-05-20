---
name: observer
description: >
  Agent self-evolution observer skill. Collects daily Agent session data and Gateway log anomalies,
  analyzes patterns, updates the .learnings/ ledger, generates a human-readable "daily iteration plan",
  and announces to the observer channel.
  Triggers: (1) daily cron (2) user request (3) urgent anomaly analysis
---

# Observer — Agent Self-Evolution Observer

## Purpose

Observer watches the entire AI team's daily operations — execution quality and infrastructure stability — and surfaces actionable improvement suggestions. It never acts autonomously; it only observes, records, and recommends.

## Two data sources

### Source 1: Agent Session Data

Use `sessions_list` to pull all active sessions, then `sessions_history(sessionKey)` for details.

Focus on:
- Session ended with error (`isError`)
- Tool call failures or retries
- Execution time > 60 seconds
- Model fallback triggered

### Source 2: Gateway Logs

Scan local log files:
- `~/.hermes/logs/errors.log` — error log (primary source)
- `~/.hermes/logs/gateway.log` — normal requests (flag > 2000ms)
- `~/.hermes/logs/agent.log` — agent activity log

Use `exec` + `grep` to scan for these patterns:

| Pattern | Category | Severity |
|---------|----------|:--------:|
| `plugins.*fetch failed` | infrastructure | medium |
| `gateway.*fetch failed` | infrastructure | medium |
| `FailoverError.*timed out` | infrastructure | high |
| `no available token` | infrastructure | high |
| `Skipping skill path` | infrastructure | low |
| `candidate_failed` | infrastructure | medium |
| `embedded run failover` | infrastructure | medium |
| `Error code: 503` | infrastructure | high |
| `Error code: 429` | infrastructure | medium |
| `Error code: 500` | infrastructure | high |
| `Error code: 401` | infrastructure | high |
| `Falling back to default config` | infrastructure | high |
| `Reasoning-only response.*exhausting retries and fallback` | errors | medium |

Count occurrences per pattern. Extract model names from 503 errors to identify specific problematic models.

**Pitfall: 503 error format with nested JSON**

The error logs often contain nested JSON in the message field:
```
Error code: 503 - {'error': {'code': 'model_not_found', 'message': 'No available channel for model deepseek-v4-nothink-expert under group default'}}
```

When counting errors, use `grep -c` on the base pattern (`Error code`), then use `grep -A 1` or `grep -B 1` to extract context for model name extraction. The full error message may span multiple lines.

**Pitfall: grep -c exit code 1 with no matches**

When `grep -c` finds zero matches, it returns exit code 1 (POSIX standard). This will crash `subprocess.run(check=True)` in Python scripts. Two solutions:

1. **Terminal tool (recommended)**: Append `|| echo 0` to the grep command — the terminal tool captures stdout regardless of exit code. Example: `grep -c 'Error code: 503' errors.log || echo 0`
2. **execute_code with subprocess**: Use `subprocess.run(cmd, shell=True, capture_output=True, text=True)` WITHOUT `check=True`, then handle the return code, or pipe through `|| echo 0` in the shell command.

Do NOT use `subprocess.run(cmd, shell=True, check=True)` — it raises `CalledProcessError` on zero-matches, which means `r.stdout` is empty when you try to parse it.

**Pitfall: Context-dependent grep patterns**

The same grep keyword can match unrelated entries. Example: `"fallback"` matches both:
- in errors.log and gateway.log this matches both:
- Model failover fallback (worrying — model switching)
- Telegram IP fallback entries (normal — periodic IP refresh, 337 in gateway.log on 2026-05-17)

Always sample (`tail -5`) the match output to verify what the pattern actually captures before reporting counts.

---

## Execution flow (6 steps)

### Step 1: Collect session data

**Session Discovery**: See `../conversation-knowledge-flywheel/references/session-discovery-workflow.md` for the validated 5-step workflow.

For cron jobs (recommended):
```bash
# List session files from ~/.hermes/sessions/
# CRITICAL: Hermes Agent stores sessions as .json (single JSON object), not .jsonl
# Check both .json and .jsonl extensions
ls ~/.hermes/sessions/*.json 2>/dev/null
ls ~/.hermes/sessions/*.jsonl 2>/dev/null

# Parse session files to extract error status
# Store structured data in .learnings/observer/raw/YYYY-MM-DD-sessions.jsonl

# CRITICAL: If no sessions found for today, fallback to yesterday's sessions
# This handles cron jobs running before any sessions are created for the day
TODAY_DATE=$(date +%Y%m%d)
YESTERDAY_DATE=$(date -d "yesterday" +%Y%m%d)

TODAY_SESSIONS=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.json 2>/dev/null | wc -l)
TODAY_SESSIONS_JSONL=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.jsonl 2>/dev/null | wc -l)
TOTAL_TODAY=$((TODAY_SESSIONS + TODAY_SESSIONS_JSONL))

if [ "$TOTAL_TODAY" -eq 0 ]; then
    SESSIONS=$(ls ~/.hermes/sessions/${YESTERDAY_DATE}_*.json 2>/dev/null; ls ~/.hermes/sessions/${YESTERDAY_DATE}_*.jsonl 2>/dev/null)
    REPORT_DATE=$(date -d "yesterday" +%Y-%m-%d)
else
    SESSIONS=$(ls ~/.hermes/sessions/${TODAY_DATE}_*.json 2>/dev/null; ls ~/.hermes/sessions/${TODAY_DATE}_*.jsonl 2>/dev/null)
    REPORT_DATE=$(date +%Y-%m-%d)
fi
```

For interactive use:
```
sessions_list → get today's session list
→ sessions_history for each session
→ store structured data in .learnings/observer/raw/YYYY-MM-DD-sessions.jsonl
```

**Session File Format Detection**:
```python
import os, json

session_file = "/root/.hermes/sessions/session_20260519_105333_314e8b.json"

# Check extension first
if session_file.endswith('.jsonl'):
    # JSONL format: each line is a JSON object
    with open(session_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            # Process each line
elif session_file.endswith('.json'):
    # JSON format: single JSON object (Hermes Agent session)
    with open(session_file, 'r') as f:
        data = json.load(f)
        # Process single object
```

Focus on:
- Session ended with error (`isError`)
- Tool call failures or retries
- Execution time > 60 seconds
- Model fallback triggered

### Step 2: Scan gateway logs

```
exec: grep -c to count each anomaly pattern
exec: grep to extract context (2 lines before/after)
→ store in .learnings/observer/raw/YYYY-MM-DD-gateway.jsonl
```

**Important**: In Step 2, also analyze error concentration. For 429 errors especially, extract session IDs from log entries and identify which sessions contribute most errors. Example: on 2026-05-17, 82% of 429 errors came from a single long-running session.

```bash
# Extract session IDs from 429 errors to find concentration
grep 'Error code: 429' errors.log | grep -oP '(?<=\[)[^\]]+(?=\])' | sort | uniq -c | sort -rn
```

This concentration analysis turns "83 429 errors" from a flat number into "82% from one session" — a much more actionable insight.

**CRITICAL**: Always perform concentration analysis for 429 errors. See `references/429-concentration-analysis.md` for the full methodology.

### Step 3: Update .learnings/ ledger

Read `.learnings/observer/index.json`.

For each anomaly:
1. Check if key exists in `recurrenceMap`
2. Exists → update `lastSeen` and `count`
3. New → add entry
4. If root cause is clear → write markdown file to appropriate category directory

### Step 4: Evaluate promote candidates

Check `recurrenceMap`:
- Key with `count >= 7` and recurring within 7 days → flag as "suggest promote"
- Add to iteration plan's "needs human decision" section

### Step 5: Generate daily iteration plan

Use `references/plan-template.md` format, fill with real data.

**CRITICAL: When generating markdown plans, ensure all placeholders are properly interpolated.**

Common pitfall: Python f-strings with nested quotes can fail if not properly escaped:
```python
# WRONG: This will leave literal {error['type']} in the output
content = f"- **[{error['type']}]** {error['message']}"

# CORRECT: Use double quotes or escape properly
content = f"- **[{error['type']}]** {error['message']}"
```

Output path: `.learnings/observer/plans/YYYY-MM-DD-iteration-plan.md`

Required 6 sections:
1. Today's execution overview (session stats)
2. Infrastructure anomalies (gateway analysis)
3. Agent execution anomalies (session analysis)
4. What to change today (max 3-5 items, with rationale and expected effect)
5. What NOT to change today (with rationale)
6. Needs human decision (list explicitly)

### Step 6: Announce to observer channel

Generate a channel summary (≤ 20 lines) and send:
```
message(action=send, target={{OBSERVER_CHANNEL_ID}}, message=<summary>)
```

Format:
```
📊 **Observer Daily — YYYY-MM-DD**

**Infrastructure**: 🟢/🟡/🔴 one-line summary
**Agent execution**: 🟢/🟡/🔴 one-line summary

**Suggested changes today**:
1. suggestion 1
2. suggestion 2

**Needs decision**: yes/no (brief description)

*Full plan: .learnings/observer/plans/YYYY-MM-DD-iteration-plan.md*
```

**Note for cron jobs**: When running via cron, the final response is auto-delivered. Do NOT call send_message — just produce the summary as your final output.

### Step 7: 结构化待办生成 + 自动写入 todo-backlog.md

**目的**：将迭代计划中的「建议改进项」和「需人工决策项」自动转化为结构化待办，写入 `~/.hermes/todo-backlog.md`，形成闭环追踪。

#### 7.1 生成结构化待办数据

从迭代计划的「💡 Suggested Changes Today」和「🔑 Needs Human Decision」两个章节提取待办项，每个待办项包含：

| 字段 | 说明 |
|------|------|
| `title` | 待办标题（从建议项标题提取） |
| `type` | 类型：`prompt` / `skill` / `model` / `cron` / `config` / `decision` |
| `priority` | 优先级：`P0`（阻塞/紧急）/ `P1`（重要）/ `P2`（一般）/ `P3`（可选） |
| `status` | 状态：`open`（待执行）/ `pending_confirm`（待确认） |
| `source` | 来源：`observer-daily` |
| `date` | 发现日期 |
| `description` | 详细描述（从建议项的 suggested action 和 expected effect 合成） |
| `action_items` | 建议操作步骤（数组） |

#### 7.2 写入 todo-backlog.md

使用 `~/.hermes/scripts/write-todo-from-output.py` 脚本自动写入：

```bash
# 方式1：从迭代计划文件提取并写入
python3 ~/.hermes/scripts/write-todo-from-output.py \
  --output .learnings/observer/plans/YYYY-MM-DD-iteration-plan.md \
  --source observer-daily \
  --format detail

# 方式2：直接传入待办项（如果脚本解析失败）
python3 ~/.hermes/scripts/write-todo-from-output.py \
  --items "建议项1描述" "建议项2描述" \
  --source observer-daily \
  --priority P2 \
  --format detail
```

**写入规则**：
- 使用 `detail` 格式（### [状态] 标题），与现有 todo-backlog.md 结构一致
- 自动检测重复项（基于标题前 30 字符匹配），避免重复写入
- 为每个待办生成唯一 ID（`obs-XXX` 格式）
- 建议改进项 → 状态 `open`，优先级根据 severity 自动映射
- 需人工决策项 → 状态 `pending_confirm`，优先级 `P1`

#### 7.3 优先级映射规则

| 迭代计划中的标记 | todo 优先级 | 说明 |
|-----------------|------------|------|
| `risk level: high` / 含"紧急"/"阻塞" | P0 | 需要立即处理 |
| `risk level: medium` / 含"重要" | P1 | 需要尽快处理 |
| `risk level: low` / 无标记 | P2 | 常规处理 |
| 需人工决策项 | P1 | 需要总工确认 |

#### 7.4 验证

写入后确认：
1. `todo-backlog.md` 中新增了当日发现的待办项
2. 待办项 ID 唯一，无重复
3. 优先级和状态正确映射
4. 如有 `--dry-run` 参数，先预览再确认写入

**⚠️ Pitfall: write-todo-from-output.py produces fragmented items**

The script may extract too many granular items from iteration plans, creating 10+ fragmented entries instead of consolidated actionable items.

- **Example**: 2026-05-20 observer run produced 15 items from a single plan
- **Root cause**: Script extracts every bullet point as a separate item, including sub-points
- **Mitigation**: 
  1. Review extracted items before accepting — consolidate related items manually
  2. Use `--dry-run` first to preview output
  3. Consider editing the iteration plan to use more consolidated bullet points (group related actions under single items)
  4. After script runs, manually consolidate in `todo-backlog.md` if needed

**Alternative**: For observer runs, consider writing a custom summary section in the iteration plan specifically for todo extraction, with 3-5 consolidated items rather than relying on automatic extraction.

---

## .learnings/ directory structure

```
.learnings/
  observer/
    errors/          ← Agent execution failures / timeouts / tool call errors
    infrastructure/  ← Gateway / provider / plugin / command delivery errors
    corrections/     ← User corrections / preference updates
    insights/        ← Observed patterns / best practices
    promoted/        ← Learnings promoted to long-term rules
    plans/           ← Daily iteration plans (human-readable)
    raw/             ← Raw session / gateway structured summaries
    index.json       ← Recurrence counts / search index
```

See `references/index-schema.md` for the full schema.
See `references/plan-template.md` for the plan format.
See `references/error-patterns.md` for detailed error pattern reference.
See `references/session-file-format.md` for session file format detection.
See `references/session-file-format-handling.md` for **validated format handling** (both .json and .jsonl).
See `references/429-concentration-analysis.md` for 429 error concentration analysis.
See `references/yaml-config-validation.md` for YAML config validation.
See `references/log-staleness-pattern.md` for distinguishing historical vs current errors.

---

## Learning file template

Each learning is a markdown file:

```markdown
# Error: {{title}}

**Date:** {{DATE}}
**Type:** {{error_type}}
**Category:** errors / infrastructure / corrections / insights
**Severity:** high / medium / low
**Recurrence Count:** {{count}} (last 7 days)

## What Happened
{{description}}

## Context
- Agent: {{agent}} (if applicable)
- Sessions: {{session_ids}} (if applicable)
- Common Pattern: {{pattern}}

## Root Cause
{{root_cause}}

## Prevention
1. {{prevention_1}}
2. {{prevention_2}}

## Status
- [ ] Pending review
- [ ] Suggested (see iteration plan)
- [ ] Executed
- [ ] Promoted
```

---

## Three-level safety mechanism

| Level | Action | Requires confirmation |
|-------|--------|-----------------------|
| Level 1 Alert | Pattern detected → notify | ❌ automatic |
| Level 2 Suggest | Concrete proposal → wait for approval | ✅ required |
| Level 3 Execute | Modify config/skill/cron | ✅ human must confirm |

**Hard rule: Never autonomously modify any skill / cron / openclaw.json. Only observe, record, suggest.**

---

## Setup

1. Configure `{{OBSERVER_CHANNEL_ID}}` in your cron prompt with your actual observer channel ID
2. Use `~/.hermes/logs/` for log files (not `{{OPENCLAW_HOME}}`)
3. Create the `.learnings/observer/` directory structure (or let the skill create it on first run)
4. Add the cron job using `prompts/cron/observer-daily-0001.md` as a template
5. Ensure the cron job has read access to `~/.hermes/sessions/` and `~/.hermes/logs/`

## Common Issues & Solutions

### Issue: Session files not found
- **Cause 1**: Cron job running from wrong working directory
- **Solution 1**: Use absolute paths (`~/.hermes/sessions/`) or set `workdir` in cron config
- **Cause 2**: Session file format mismatch — Hermes Agent stores sessions as `.json` (single JSON object), but observer skill expects `.jsonl` format
- **Solution 2**: Update session detection logic to handle both `.json` and `.jsonl` formats (see `references/session-file-format.md`)
- **Cause 3**: Cron job runs before any sessions are created for the day
- **Solution 3**: Implement session date fallback to yesterday's sessions (see `references/session-file-format.md`)

### Issue: Telegram delivery failures (bot-to-bot)
- **Cause**: Observer cron job configured to deliver to a Telegram bot, but bots cannot send messages to other bots
- **Symptom**: `Forbidden: the bot can't send messages to the bot`
- **Solution**: Change delivery target to `local` or configure a user/group chat ID (see `references/session-file-format.md` for details)

### Issue: Log patterns not matching
- **Cause**: Log format changed or patterns too specific
- **Solution**: Check actual log content first, then adjust patterns

### Issue: 503 errors from model provider
- **Cause**: Model quota exhausted or provider service down
- **Solution**: Check `fallback_providers` config, add backup models

### Issue: Telegram delivery failures (bot-to-bot)
- **Cause**: Observer cron job configured to deliver to a Telegram bot, but bots cannot send messages to other bots
- **Symptom**: `Forbidden: the bot can't send messages to the bot`
- **Solution**: Change delivery target to a user or group chat ID, not a bot ID. Configure `telegram_chat_id` to a user's chat ID (e.g., `<YOUR_TELEGRAM_CHAT_ID>`) or a group chat ID.

### Issue: High session failure rate
- **Cause**: Multiple infrastructure issues compounding
- **Solution**: Address infrastructure issues first (503, 429, 500 errors)

### Issue: "Falling back to default config" messages
- **Cause**: YAML parsing failure in config.yaml (check line numbers in the error message)
- **Solution**: Run `hermes config validate`, fix the YAML syntax, restart. Until fixed, ALL custom config (fallback_providers, model settings, auxiliary providers) is ignored.

See `references/yaml-config-validation.md` for detailed YAML error patterns and fixes.

### Pitfall: Stale log errors vs current config state
**Critical**: Error logs may contain historical entries that no longer reflect current state.
- **Example**: 57 "Falling back to default config" entries found in errors.log, but YAML validation showed config.yaml is currently valid.
- **Root cause**: Logs accumulate historical errors; they don't auto-purge when issues are fixed.
- **Detection**: Always run live validation (`python -c "import yaml; yaml.safe_load(open('config.yaml'))"`) to verify current state, not just grep logs.
- **Reporting**: When reporting errors, distinguish between:
  - **Historical count**: Total occurrences in logs (may include stale entries)
  - **Current status**: Live validation result (what's actually broken NOW)
- **Action**: If live validation passes but logs show errors, note in report: "Errors found in logs are historical; current config is valid."

## Constraints

- Never modify skill / cron / openclaw.json without explicit human confirmation
- Never delete learning files (archive only)
- Raw logs in `.learnings/raw/` auto-purge after 7 days
- All git commits must use `[observer]` prefix
- P0 frozen layer (identity, authority, hard rules) is never touched

---

## Completion checklist

After each Observer run, confirm:
1. `.learnings/observer/plans/YYYY-MM-DD-iteration-plan.md` generated
2. `.learnings/observer/index.json` updated
3. `.learnings/observer/raw/YYYY-MM-DD-sessions.jsonl` written
4. `.learnings/observer/raw/YYYY-MM-DD-gateway.jsonl` written
5. Observer channel announced (or auto-delivered for cron jobs)
6. **待办已写入 todo-backlog.md**（Step 7 完成，检查新增条目）
7. Git commit made (if files changed) - use `[observer]` prefix

## Integration Testing Methodology

When testing Brain OS cron tasks (or any multi-task system), follow this sequence:

### Phase 1: Module Testing (Synthetic Data)
- Create test data manually (e.g., test todo entry)
- Test individual components in isolation
- Verify each component works with controlled input

### Phase 2: Integration Testing (Real Data)
- **Trigger all related cron tasks manually**: `hermes cron run <task_id>`
- **Wait for scheduler tick** (60s interval) or use `hermes cron tick`
- **Verify outputs sequentially**:
  1. Producer tasks → check output files exist and have content
  2. Kanban管理层 → check cards created, todo updated
  3. Consumer tasks → check reports generated, data read correctly
- **Check data flow end-to-end**: producer → todo → Kanban → todo → consumer → report

### Phase 3: 24-Hour Validation
- Wait for natural cron schedule to run
- Verify all tasks execute correctly with real production data
- Compare manual trigger results with scheduled execution results

### Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Nightly tasks produce empty output during day | They read "last 24 hours" data; empty output is expected during daytime manual trigger |
| Task triggered but no output | Check scheduler tick timing (60s interval), check task status in `hermes cron list` |
| Session files not found | Check all format patterns: `session_YYYYMMDD_*.json` and `YYYYMMDD_*.jsonl` |
| Delivery fails silently | Check `last_delivery_error` in cron status, verify channel configuration |

### Verification Commands

```bash
# Trigger task manually
hermes cron run <task_id>

# Check task status
hermes cron list
hermes cron status <task_id>

# Check output files
ls -la ~/.hermes/.learnings/observer/plans/
ls -la ~/.hermes/knowledge/09-personal-ops/01-每日简报/

# Check Kanban cards
hermes kanban list

# Check todo
cat ~/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md
```

See `references/session-file-formats.md` for session file format details.

## Output Format Requirements

- **All content must be in Chinese** (including titles, section headers, table content, descriptions)
- **Use emoji for status indicators**: 🟢 (健康), 🟡 (警告), 🔴 (严重)
- **Follow the plan template structure** from `references/plan-template.md`
- **Keep channel summary ≤ 20 lines** for readability

## Session Date Fallback Implementation

When running as a cron job, use this Python implementation for session date fallback:

```python
from datetime import datetime, timedelta
import os, json

today_date = datetime.now().strftime("%Y%m%d")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
sessions_dir = os.path.expanduser("~/.hermes/sessions/")

# CRITICAL: Hermes Agent stores sessions in multiple formats:
# 1. session_YYYYMMDD_HHMMSS_XXXXXX.json (current format)
# 2. YYYYMMDD_HHMMSS_XXXXXX.json (legacy format)
# 3. YYYYMMDD_*.jsonl (old JSONL format)
# Check all patterns to find today's sessions

today_sessions = [
    f for f in os.listdir(sessions_dir) 
    if (f.startswith(f"session_{today_date}") or 
        f.startswith(f"{today_date}_")) and 
       (f.endswith('.jsonl') or f.endswith('.json'))
]

if not today_sessions:
    # Fallback to yesterday's sessions
    today_sessions = [
        f for f in os.listdir(sessions_dir) 
        if (f.startswith(f"session_{yesterday_date}") or 
            f.startswith(f"{yesterday_date}_")) and 
           (f.endswith('.jsonl') or f.endswith('.json'))
    ]
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
else:
    report_date = datetime.now().strftime("%Y-%m-%d")
```

This handles all session file naming patterns used by Hermes Agent.

## Pitfalls & Edge Cases

### Session Date Fallback Logic
When running as a cron job early in the day before any sessions are created:
- If no sessions found for today, automatically fall back to yesterday's sessions
- **If neither today nor yesterday has sessions, fall back to the most recent available session data** (scan all session files, pick the latest date)
- Report date should reflect the actual data date, not the calendar date
- This prevents false negatives when cron runs before sessions are created
- **Implementation**: See `: See `references/session-date-fallback.md` for Python code template

### Pitfall: execute_code Import Isolation
When using `execute_code` for multiple Python calls during a session, **each script runs in isolation**. Imports must be repeated at the top of each script block:
```python
# WRONG - will fail on second call:
# First call: import os, json
# Second call: os.listdir() -> NameError: name 'os' is not defined

# CORRECT - in every call:
# First call: import os, json, re
# Second call: import os, json, re  (repeat imports)
```
This is a common mistake that caused `NameError` failures during the 2026-05-17 observer run. Always include all required imports at the top of each `execute_code` block.

### Pitfall: python syntax errors in execute_code
Python scripts passed to `execute_code` are compiled as-is before execution. Common avoidable errors:
- **Missing assignment operator**: `x = sorted(...)` not `x sorted(...)`
- **Bad variable names**: `in_daterange` is not valid Python; use `in_date_range`
- **String interpolation in f-strings**: In the `execute_code` context, nested quotes in f-strings (`f"{dict['key']}"`) cause syntax errors. Use dict.get('key') or intermediate variables.
- **Line breaks**: Multi-line list comprehensions need proper indentation.

When writing execute_code scripts, write the script to a .py file first using write_file, then run it with terminal — you get lint checks and can fix syntax errors before execution.

### Pitfall: Session file format mismatch
Session files may not be in the expected format. Multiple formats exist:

| Format | Extension | Structure |
|--------|-----------|-----------|
| **JSONL (expected)** | `.jsonl` | Each line is a JSON object |
| **JSON (actual)** | `.json` | Single JSON object (Hermes Agent session) |
| **Conversation** | `.jsonl` | Contains `role`, `content`, `timestamp` fields |

**Detection**: Before parsing, check the file extension and first line:
```python
import os, json

session_file = "/root/.hermes/sessions/session_20260519_105333_314e8b.json"

# Check extension first
if session_file.endswith('.json'):
    # Single JSON object format (Hermes Agent)
    with open(session_file, 'r') as f:
        data = json.load(f)
    # Extract stats from single object
    session_id = data.get('session_id')
    model = data.get('model')
    # ... parse as needed
elif session_file.endswith('.jsonl'):
    # JSONL format - check first line structure
    with open(session_file, 'r') as f:
        first_line = json.loads(f.readline())
    if 'type' not in first_line and 'role' in first_line:
        # Conversation format — cannot extract structured stats
        print("Session file is in conversation format, skipping structured analysis")
```

**Impact**: If format mismatch, report "N/A" for session statistics and note this in the plan.

**Known Issue (2026-05-19)**: Hermes Agent stores sessions as `.json` files (single JSON object), but observer skill expects `.jsonl` format. This causes observer to fail to find today's sessions and fall back to yesterday's data.

### Pitfall: grep -c output with newlines
When using `grep -c` via subprocess, output may contain trailing newlines or multiple lines:
```python
# WRONG — will fail if output is "83\n"
count = int(result.stdout.strip())

# CORRECT — handle potential multiline output
output = result.stdout.strip().split('\n')[0]
count = int(output) if output.isdigit() else 0
```

**Alternative**: Use `head -1` in the shell command: `grep -c 'pattern' file | head -1`

### Gateway Log Pattern Matching
- Error patterns may span multiple lines in logs
- Use `grep -A 1` or `grep -B 1` to extract context for multi-line errors
- For 503 errors with nested JSON, extract model names from the error message
- For 429 errors with the format `Error code: 429 - {'error': {...}}`, the model name appears inside the message field — use `grep -oP` to extract it

### Pitfall: YAML Config Validation

When "Falling back to default config" appears in logs:
1. **Immediate action**: Run YAML validation
   ```bash
   python -c "import yaml; yaml.safe_load(open('/root/.hermes/config.yaml'))" && echo "Valid" || echo "Invalid"
   ```
2. **Report severity**: Always report as `high` severity infrastructure issue
3. **Impact**: ALL custom config (fallback_providers, model settings, auxiliary providers) is ignored until fixed

See `references/yaml-config-validation.md` for detailed YAML error patterns and fixes.

### Index Update Logic
- When updating `index.json`, preserve existing entries and only update `lastSeen` and `count`
- Promote candidates are flagged when `count >= 7` AND `lastSeen` within 7 days
- Do not delete entries; archive instead if needed
- **⚠️ Pitfall: Schema migration** — Existing `index.json` entries may be missing required fields (`title`, `status`, `promoteCandidates`). Before processing, validate and add missing fields to prevent `KeyError`:
  ```python
  for key, entry in index_data["recurrenceMap"].items():
      if "title" not in entry:
          entry["title"] = error_titles.get(key, key)
      if "status" not in entry:
          entry["status"] = "open"
  if "promoteCandidates" not in index_data:
      index_data["promoteCandidates"] = []
  ```