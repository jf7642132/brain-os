# Task Dispatch Workflow for dingtalk-worker

## Overview

This document describes the workflow for using a dedicated dingtalk-worker profile to dispatch tasks to team members via DingTalk.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Kanban (user)                        │
│  Creates tasks with assignee=dingtalk-worker                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Dispatcher (embedded)                       │
│  Scans ready tasks → spawns dingtalk-worker for each            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     dingtalk-worker Agent                        │
│  1. Reads task description                                       │
│  2. Extracts employee name (e.g., "请员工A完成XXX")              │
│  3. Looks up employee_mapping.yaml for DingTalk User ID         │
│  4. Sends DingTalk message @employee                             │
│  5. Adds kanban comment with notification record                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DingTalk Group Chat                          │
│  @Employee receives task notification                            │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Checklist

### 1. dingtalk-worker Profile Config (`~/.hermes/profiles/dingtalk-worker/config.yaml`)

```yaml
toolsets:
- hermes-cli
- hermes-dingtalk  # REQUIRED for sending messages

platforms:
  dingtalk:
    enabled: true
    extra:
      allowed_chats:
        - <group-chat-id>  # REQUIRED: whitelist the target group

memory:
  memory_enabled: false
  user_profile_enabled: false
```

### 2. Employee Mapping File (`/root/.hermes/profiles/dingtalk-worker/employee_mapping.yaml`)

```yaml
# 员工名字 → DingTalk User ID 映射
# User ID format: $:LWCP_v1:$... (extracted from gateway logs)

员工A: $:LWCP_v1:$VqWUaB7Bw9Guqgnj1pPqOw==
员工B: $:LWCP_v1:$XXXXXXXXXXXXXXXXXXXXXXXX
员工C: $:LWCP_v1:$XXXXXXXXXXXXXXXXXXXXXXXX
员工D: $:LWCP_v1:$XXXXXXXXXXXXXXXXXXXXXXXX
```

### 3. Main Instance Config (`~/.hermes/config.yaml`)

```yaml
platforms:
  dingtalk:
    enabled: false  # DISABLED to prevent dual connection conflict
```

## Capturing Employee User IDs

### Why Text Messages Are Required

The DingTalk adapter filters out messages with no text content:
```python
# gateway/platforms/dingtalk.py, lines 624-626
if not text and not media_urls:
    logger.debug("[%s] Empty message, skipping", self.name)
    return
```

Emoji-only messages have no text and no media URLs, so they are silently dropped.

### Steps

1. Ask each employee to send a **text message** in the target group (e.g., "测试" or "收到")
2. Check gateway logs:
   ```bash
   grep "inbound message" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log | tail -5
   ```
3. Extract User ID from log line:
   ```
   2026-05-15 12:39:00,302 INFO gateway.run: inbound message: platform=dingtalk user=赵九峰 chat=cidTdsKxdz5WTNV/6BgTCrsrw== msg='帮我分析辛醇的出口市场'
   ```
   The `user` field shows the display name. The actual User ID is in the `sender_id` field which appears in the raw message.

4. For the actual User ID format (`$:LWCP_v1:$...`), check the `build_source` output or use:
   ```bash
   grep "sender_id" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log | tail -5
   ```

### Alternative: Use the User ID from `notify-subscribe`

If you've already subscribed to notifications for a task, the User ID is stored in the subscription record:
```bash
hermes kanban notify-list
```

## Task Description Format

To make it easy for dingtalk-worker to extract employee names, use a consistent format:

```markdown
请员工A完成以下工作：
1. 检查ERP系统数据同步状态
2. 生成日报并发送给总工

截止时间：2026-05-20
```

The agent will:
1. Parse the task description
2. Identify "员工A" as the target employee
3. Look up the DingTalk User ID from `employee_mapping.yaml`
4. Send a message with the task details

## Sending @Mentions

The `hermes_dingtalk_send` tool supports the `mentioned_list` parameter:

```python
# Tool signature
async def send(
    text: str,
    chat_id: str,
    mentioned_list: Optional[list[str]] = None,  # DingTalk User IDs
    msg_type: str = "text",
    ...
) -> SendResult
```

**Important:** `mentioned_list` requires DingTalk User IDs in the format `$:LWCP_v1:$...`, NOT nicknames or display names.

Example:
```python
await send(
    text="@员工A 请完成以下工作：...",
    chat_id="cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=",
    mentioned_list=["$:LWCP_v1:$VqWUaB7Bw9Guqgnj1pPqOw=="]
)
```

## Session Webhook Limitation

### The Problem

The `_session_webhooks` dict is populated ONLY when a message is received from a chat. If no message has been received from a chat, there's no session_webhook, and sending to that chat will fail with:

```
WARNING gateway.platforms.dingtalk: [Dingtalk] No valid session_webhook for chat_id=...
```

### The Solution

Before the worker needs to send messages to a group, have someone in that group send a text message first. This establishes the session_webhook.

```bash
# After someone sends a message, verify the webhook is recorded
grep "session_webhook" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log | tail -5
```

## Troubleshooting

### Symptom: "No valid session_webhook" warning

**Cause:** No message has been received from the target chat yet.

**Fix:** Have someone in the target group send a text message.

### Symptom: Employee doesn't receive @mention

**Cause 1:** Employee User ID not in `employee_mapping.yaml`

**Fix:** Capture the User ID and add to mapping file.

**Cause 2:** `allowed_chats` doesn't include the target group

**Fix:** Add the group chat ID to `allowed_chats` in config.yaml.

**Cause 3:** DingTalk API rate limit

**Fix:** Wait and retry. Check DingTalk developer console for rate limit status.

### Symptom: Task not dispatched

**Cause:** Dispatcher not running or task not in "ready" status

**Fix:**
```bash
# Check dispatcher status
grep "kanban dispatcher" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log

# Check task status
hermes kanban list --status ready
```

## Best Practices

1. **Use consistent task description format** — Makes employee name extraction reliable
2. **Keep `employee_mapping.yaml` updated** — User IDs can change if employees leave/join
3. **Monitor gateway logs** — Catch issues early with `tail -f`
4. **Test with a single employee first** — Before rolling out to the whole team
5. **Document the workflow** — Share this guide with team members so they understand how to interact with the bot