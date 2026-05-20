---
name: cron-delivery-channel-switch
description: Guide for switching cron task delivery channels (WeChat → Telegram), understanding origin routing, and fixing Telegram home channel misconfiguration.
version: 1.1.0
---

# Cron Task Delivery Channel Switch

## Problem

Cron tasks configured with `deliver: origin` (WeChat) hit iLink API rate limits (`ret=-2 rate limited`), causing delivery failures.

## Solution: Switch to Telegram

### Diagnosis

1. Check for rate limit errors in cron task status:
```bash
hermes cron list
# Look for last_delivery_error containing "rate limited"
```

2. Verify which tasks are using WeChat:
```python
import json
with open('/root/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)
for task in data['jobs']:
    if task.get('deliver') == 'origin' and task.get('origin', {}).get('platform') == 'weixin':
        print(f"{task['id']}: {task['name']} - {task['last_delivery_error']}")
```

### Fix: Use `hermes cron edit` CLI (Preferred)

```bash
# Switch a single task's delivery channel
hermes cron edit <job_id> --deliver "local,telegram"

# Example: Switch daily morning briefing from WeChat to Telegram
hermes cron edit a750c4ebaa8d --deliver "local,telegram"
```

**Note**: The `--deliver` flag accepts comma-separated targets. `local` keeps output saved locally, `telegram` adds Telegram delivery.

### Verification

```bash
# Check the changes took effect
hermes cron list

# Verify gateway picks up changes (gateway reads jobs.json on startup)
# Gateway should auto-reload cron ticker, but restart to be sure
hermes gateway restart
```

### Telegram Chat ID Setup

If you don't have a Telegram chat ID:
1. Start the Telegram bot in a private chat with your bot
2. Send a message
3. The chat ID appears in gateway logs: `[Telegram] Connected to Telegram`
4. Or use: `curl http://127.0.0.1:8642/api/telegram/chat-id` (if API server enabled)

### Pitfall: Multiple Tasks Hitting Rate Limit Simultaneously

Even after switching channels, avoid scheduling multiple tasks at the same time:
- Spread out task times (e.g., 01:00, 01:30, 02:00 instead of all at 01:00)
- Use `hermes cron edit <id>` to adjust schedule expressions

### Pitfall: Origin Field Not Cleared

If `origin` is not cleared, the task may still attempt WeChat delivery:
- Always set `task['origin'] = None` when switching channels
- Verify with: `grep -A5 '"origin"' ~/.hermes/cron/jobs.json`

## `origin` Delivery Mechanism

`origin` is **not a specific platform** — it's a **dynamic routing strategy**:

| Scenario | Behavior |
|----------|----------|
| Task has `origin` info | Deliver to the chat where the task was created (where you ran `/cron add`) |
| Task has no `origin` info | Fall back to each platform's home channel in order (Telegram → WeChat → DingTalk) |

**Source**: `cron/scheduler.py` lines 267-289

```python
if deliver_value == "origin":
    if origin:
        return {"platform": origin["platform"], "chat_id": origin["chat_id"], ...}
    # No origin — try each platform's home channel as fallback
    for platform_name in _iter_home_target_platforms():
        chat_id = _get_home_target_chat_id(platform_name)
        if chat_id:
            return {"platform": platform_name, "chat_id": chat_id, ...}
    return None
```

### Pitfall: Telegram Home Channel Misconfiguration

**Symptom**: Telegram shows "Forbidden: the bot can't send messages to the bot"

**Root Cause**: `TELEGRAM_HOME_CHANNEL` is set to the **bot's own ID** instead of the user's personal ID.

**Example of the bug**:
```
TELEGRAM_HOME_CHANNEL=<YOUR_TELEGRAM_CHAT_ID>  # This is the BOT's ID, not user's!
```

**Fix**:
```bash
# Find your actual Telegram user ID:
# 1. Send a message to the bot in Telegram
# 2. Check gateway logs: grep "Connected" ~/.hermes/logs/gateway.log
# 3. Or check send_message tool output for chat_id

# Correct configuration:
TELEGRAM_HOME_CHANNEL=<YOUR_CHAT_ID>  # Your personal Telegram ID
```

**Verification**:
```bash
# Test by sending a message
hermes send telegram "Test message"

# Or via send_message tool — should succeed without "Forbidden" error
```

**Why this matters for `origin`**: When a cron task has `deliver=origin` but no `origin` info, it falls back to home channels. If Telegram home channel is misconfigured, it fails and falls through to WeChat.

## Related

- `webhook-subscriptions` — For event-driven automation
- `send_message` — For sending messages via connected platforms

---

## ⚠️ Config Modification Pitfalls

### `hermes config set` List Serialization Bug

**Problem**: `hermes config set` stores list values as YAML strings instead of proper lists.

```bash
# This produces WRONG output:
hermes config set fallback_providers '["deepseek"]'
# Result: fallback_providers: '[deepseek]'  (string, not list!)

hermes config set fallback_providers '[deepseek]'
# Result: fallback_providers: '[deepseek]'  (still a string!)
```

**Correct approach**: Use `ruamel.yaml` to edit config.yaml directly while preserving key order:

```python
from ruamel.yaml import YAML
yaml = YAML()
yaml.preserve_quotes = True

with open('/root/.hermes/config.yaml', 'r') as f:
    config = yaml.load(f)

# Modify the config
config['fallback_providers'] = [
    {'provider': 'deepseek', 'model': 'deepseek-v4-flash', ...}
]

with open('/root/.hermes/config.yaml', 'w') as f:
    yaml.dump(config, f)
```

**Why `ruamel.yaml`?**: Standard `yaml.dump()` alphabetizes keys, destroying the original config structure. `ruamel.yaml` preserves order and comments.

### `origin` Delivery for Cron Tasks

**Problem**: `deliver: origin` is meaningless for cron tasks — they have no source chat window.

**Behavior**:
- If `origin` exists → deliver to that chat
- If `origin` is None → fall back to home channels (Telegram → WeChat → DingTalk)

**Fix**: Use explicit platform delivery for cron tasks:
```bash
hermes cron edit <job_id> --deliver "local,weixin:your_user_id"
```

### WeChat Rate Limiting

**Symptom**: `iLink sendmessage rate limited: ret=-2`

**Cause**: Multiple cron tasks sending to WeChat simultaneously.

**Fix**: Stagger task times or merge reports into single scheduled task.