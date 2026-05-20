---
name: telegram-channel-troubleshooting
description: Diagnose and fix Telegram messaging issues in Hermes — home channel misconfiguration, bot ID vs user ID confusion, and rate limit handling.
tags: [telegram, messaging, troubleshooting, home-channel, bot-configuration]
---

# Telegram Channel Troubleshooting

## Problem: "Forbidden: the bot can't send messages to the bot"

### Symptom

When using `send_message` tool or `hermes send telegram` command:
```
Telegram send failed: Forbidden: the bot can't send messages to the bot
```

### Root Cause

`TELEGRAM_HOME_CHANNEL` in `.env` is set to the **bot's own Telegram ID** instead of the **user's personal Telegram ID**.

The bot cannot send messages to itself — this is a Telegram API restriction.

### Diagnosis

1. Check current configuration:
```bash
grep TELEGRAM_HOME_CHANNEL ~/.hermes/.env
```

2. Common bug pattern:
```
TELEGRAM_HOME_CHANNEL=<YOUR_TELEGRAM_CHAT_ID>  # This is the BOT's ID!
```

3. Find your actual Telegram user ID:
```bash
# Option 1: Send a message to the bot, then check gateway logs
grep "Connected" ~/.hermes/logs/gateway.log

# Option 2: Use send_message tool and check the chat_id in output
# (The tool will show the resolved chat_id)

# Option 3: Check cron delivery error messages for chat_id hints
```

### Fix

```bash
# 1. Update .env with your personal Telegram ID
sed -i 's/TELEGRAM_HOME_CHANNEL=<bot-id>/TELEGRAM_HOME_CHANNEL=<your-personal-id>/' ~/.hermes/.env

# Example (2026-05-19 fix):
sed -i 's/TELEGRAM_HOME_CHANNEL=<YOUR_TELEGRAM_CHAT_ID>/TELEGRAM_HOME_CHANNEL=<YOUR_CHAT_ID>/' ~/.hermes/.env

# 2. Restart Gateway to pick up changes
hermes gateway restart

# 3. Verify
hermes send telegram "Test message - channel fix verified"
```

### Verification

After fix, `send_message` tool should return:
```json
{"success": true, "platform": "telegram", "chat_id": "<YOUR_CHAT_ID>", "message_id": "..."}
```

Not the "Forbidden" error.

## `origin` Delivery and Home Channel Fallback

### How `origin` Works

`origin` is **not a specific platform** — it's a **dynamic routing strategy**:

| Scenario | Behavior |
|----------|----------|
| Task has `origin` info | Deliver to the chat where the task was created |
| Task has no `origin` info | Fall back to home channels in order: **Telegram → WeChat → DingTalk** |

### Why Telegram Misconfiguration Breaks `origin`

When a cron task has `deliver=origin` but no `origin` metadata:
1. System tries Telegram home channel first
2. If Telegram home channel is misconfigured (bot ID), delivery fails
3. Falls through to WeChat home channel
4. If WeChat is also rate-limited or unavailable, delivery fails entirely

### Fix for Cron Tasks with `deliver=origin`

```bash
# Option 1: Fix Telegram home channel (recommended)
# See "Fix" section above

# Option 2: Explicitly set delivery to telegram
hermes cron edit <job_id> --deliver "telegram"

# Option 3: Set origin metadata on the task
# (Advanced — requires direct database edit)
```

## Related Issues

| Issue | Solution |
|-------|----------|
| Bot ID in TELEGRAM_HOME_CHANNEL | Replace with user's personal ID |
| Cron tasks failing with `deliver=origin` | Fix home channel OR set explicit `--deliver telegram` |
| Multiple rate-limited channels | Spread out task schedules, fix each channel |

## Prevention

1. **Never use bot's own ID** as `TELEGRAM_HOME_CHANNEL`
2. **Always verify** after configuration changes with `hermes send telegram "test"`
3. **Check cron delivery errors** — they often reveal home channel issues
4. **Document your Telegram user ID** in a safe place for future reference

---

*Created: 2026-05-19 — Based on production fix applied to resolve Telegram delivery failures.*