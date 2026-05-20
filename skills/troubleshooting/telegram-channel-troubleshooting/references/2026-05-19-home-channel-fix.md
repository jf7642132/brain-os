# Telegram Home Channel Fix — 2026-05-19 Session

## Problem

Telegram delivery failing with:
```
Telegram send failed: Forbidden: the bot can't send messages to the bot
```

## Root Cause Analysis

The `TELEGRAM_HOME_CHANNEL` was configured as `<YOUR_TELEGRAM_CHAT_ID>`, which is the **bot's own Telegram ID**, not the user's personal ID.

Telegram API does not allow a bot to send messages to itself.

## Configuration Before Fix

```bash
# ~/.hermes/.env
TELEGRAM_BOT_TOKEN=837760...a9WQ
TELEGRAM_ALLOWED_USERS=<YOUR_CHAT_ID>,<YOUR_TELEGRAM_CHAT_ID>
TELEGRAM_HOME_CHANNEL=<YOUR_TELEGRAM_CHAT_ID>  # BUG: This is the BOT's ID!
```

Note: `TELEGRAM_ALLOWED_USERS` correctly included `<YOUR_CHAT_ID>` (user's ID), but `TELEGRAM_HOME_CHANNEL` was wrong.

## Fix Applied

```bash
# 1. Update TELEGRAM_HOME_CHANNEL to user's personal ID
sed -i 's/TELEGRAM_HOME_CHANNEL=<YOUR_TELEGRAM_CHAT_ID>/TELEGRAM_HOME_CHANNEL=<YOUR_CHAT_ID>/' ~/.hermes/.env

# 2. Restart Gateway
hermes gateway restart

# 3. Verify with send_message tool
# Result: {"success": true, "platform": "telegram", "chat_id": "<YOUR_CHAT_ID>", "message_id": "3073"}
```

## Configuration After Fix

```bash
TELEGRAM_BOT_TOKEN=837760...a9WQ
TELEGRAM_ALLOWED_USERS=<YOUR_CHAT_ID>,<YOUR_TELEGRAM_CHAT_ID>
TELEGRAM_HOME_CHANNEL=<YOUR_CHAT_ID>  # FIXED: User's personal ID
```

## Impact on Cron Tasks

This fix also resolved cron task delivery issues:

| Task | Before | After |
|------|--------|-------|
| `a750c4ebaa8d` (每日早报) | `local,weixin:xxx` → rate limited | `local,telegram` → ✅ |
| `974794d13b7f` (午间待办) | `origin` → fell to WeChat (rate limited) | `telegram` → ✅ |
| `b62a532b3c2b` (周一Lint) | `origin` → fell to WeChat (rate limited) | `telegram` → ✅ |

## Key Insight: `origin` Fallback Order

When `deliver=origin` and no origin metadata exists:
1. Try Telegram home channel first
2. If Telegram fails, try WeChat home channel
3. If WeChat fails, try DingTalk home channel

**Fixing Telegram home channel is critical** because it's the first fallback target.

## Lessons Learned

1. **Always verify Telegram home channel** — it's easy to confuse bot ID with user ID
2. **Check `TELEGRAM_ALLOWED_USERS` vs `TELEGRAM_HOME_CHANNEL`** — they can have different values
3. **Test with `hermes send telegram "test"`** after any Telegram configuration change
4. **Cron `origin` delivery depends on home channel config** — fixing home channel fixes origin fallback

---

*Session: 2026-05-19 11:02 - 12:14*
*Fix applied by: Hermes Agent*
*Verified: send_message tool returned success with chat_id=<YOUR_CHAT_ID>*