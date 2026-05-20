---
name: weixin-troubleshooting
description: Diagnose and fix WeChat (微信) messaging issues in Hermes — authentication, authorization, and connectivity problems.
version: 1.0.0
metadata:
  hermes:
    tags: [wechat, weixin, messaging, troubleshooting, authorization]
---

# WeChat (微信) Troubleshooting Guide

Use this guide when WeChat messaging isn't working — messages not sending, unauthorized user errors, or connection issues.

## Common Symptoms & Fixes

### 1. "Unauthorized user" Error

**Symptom:** Gateway logs show:
```
WARNING gateway.run: Unauthorized user: <YOUR_WEIXIN_CHAT_ID>
```

**Cause:** User ID not in the allowlist (`WEIXIN_ALLOWED_USERS`)

**Fix:**
1. Find your WeChat user ID from the error message or logs
2. Edit `~/.hermes/.env`:
   ```bash
   # Add your user ID (comma-separated if multiple)
   WEIXIN_ALLOWED_USERS=your_user_id,another_user_id
   
   # Or allow all users (less secure)
   WEIXIN_ALLOW_ALL_USERS=true
   ```
3. Restart the gateway:
   ```bash
   systemctl --user restart hermes-gateway
   # Or manually: kill $(cat ~/.hermes/gateway.pid) && hermes gateway
   ```

### 2. Weixin Channel Empty in Directory

**Symptom:** `channel_directory.json` shows:
```json
"weixin": []
```

**Cause:** WeChat account configured but not activated in channel directory

**Fix:**
1. Check account exists:
   ```bash
   ls ~/.hermes/weixin/accounts/
   ```
2. Verify gateway state:
   ```bash
   cat ~/.hermes/gateway_state.json
   ```
3. Restart gateway to rebuild channel directory

### 3. Weixin Not Connected

**Symptom:** Gateway logs show:
```
INFO gateway.platforms.weixin: [Weixin] Disconnected
```

**Fix:**
1. Check account configuration:
   ```bash
   cat ~/.hermes/weixin/accounts/your_account.json
   ```
2. Verify token is valid (not expired)
3. Check base_url is correct: `https://ilinkai.weixin.qq.com`
4. Restart gateway

## Diagnostic Commands

### Check WeChat Account Status
```bash
ls -la ~/.hermes/weixin/accounts/
cat ~/.hermes/weixin/accounts/ACCOUNT_ID@im.bot.json
```

### Check Gateway State
```bash
cat ~/.hermes/gateway_state.json
```

### Check Channel Directory
```bash
cat ~/.hermes/channel_directory.json
```

### View Recent Weixin Logs
```bash
grep weixin ~/.hermes/logs/gateway.log | tail -30
```

### Check Environment Variables
```bash
grep WEIXIN ~/.hermes/.env
```

### Check if Gateway is Running
```bash
ps aux | grep gateway
cat ~/.hermes/gateway.pid
```

## Configuration Reference

### `.env` Settings for WeChat
```bash
# WeChat DM policy: "allowlist" or "all"
WEIXIN_DM_POLICY=allowlist

# Allow all users (bypass allowlist check)
WEIXIN_ALLOW_ALL_USERS=false

# Comma-separated list of allowed user IDs
WEIXIN_ALLOWED_USERS=zhjf466789763

# Group chat allowed users (comma-separated)
WEIXIN_GROUP_ALLOWED_USERS=
```

### Account Configuration Structure
```json
{
  "token": "21350e...b213",
  "base_url": "https://ilinkai.weixin.qq.com",
  "user_id": "<YOUR_WEIXIN_CHAT_ID>",
  "saved_at": "2026-04-11T12:35:59Z"
}
```

## Troubleshooting Workflow

1. **Is gateway running?** → `ps aux | grep gateway`
2. **Is weixin connected?** → Check `gateway_state.json` for `"state": "connected"`
3. **Check logs for errors** → `grep weixin ~/.hermes/logs/gateway.log | tail -20`
4. **Verify user authorization** → Check `WEIXIN_ALLOWED_USERS` in `.env`
5. **Restart gateway** → `systemctl --user restart hermes-gateway`

### 4. iLink API Rate Limiting (Multiple Scheduled Tasks)

**Symptom**: Gateway logs show:
```
ERROR gateway.platforms.weixin: [Weixin] send failed to=o9cq802K: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited
```
Cron jobs show `⚠ Delivery failed: delivery error: Weixin send failed: iLink sendmessage rate limited`

**Cause**: iLink API has rate limits. Multiple scheduled tasks triggering simultaneously (especially on Mondays at 01:00) exceed the limit.

**Important**: This is NOT caused by multiple gateway instances. Even if `gateway status` shows warnings about "PID already in use", verify with `ps aux | grep <PID>` — stale PIDs may have already exited.

**Fix**:
1. Check cron job schedules: `hermes cron list`
2. Identify overlapping times (e.g., multiple tasks at 01:00 on Mondays)
3. Stagger task times to spread out weixin deliveries:
   ```bash
   # Example: move one task from 01:00 to 01:30
   hermes cron update <job_id> --schedule "30 1 * * 1"
   ```
4. Or merge multiple reports into a single scheduled task

### 5. `origin` Delivery Invalid for Cron Tasks

**Symptom**: Cron tasks with `deliver: origin` fail silently or fall back to wrong channel.

**Root Cause**: `origin` is a dynamic routing strategy based on where `/cron add` was run. Cron tasks have no source chat context, so `origin` is meaningless.

**Behavior**:
- If `origin` exists → deliver to that chat
- If `origin` is None → fall back to home channels (Telegram → WeChat → DingTalk)

**Fix**: Use explicit platform delivery for cron tasks:
```bash
hermes cron edit <job_id> --deliver "local,weixin:your_user_id"
```

**Verification**:
```bash
hermes cron list
# Check that deliver field shows explicit target, not "origin"
```

### 4. iLink API Rate Limiting (Multiple Scheduled Tasks)

**Symptom:** Gateway logs show:
```
ERROR gateway.platforms.weixin: [Weixin] send failed to=o9cq802K: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited
```
Cron jobs show `⚠ Delivery failed: delivery error: Weixin send failed: iLink sendmessage rate limited`

**Cause:** iLink API has rate limits. Multiple scheduled tasks triggering simultaneously (especially on Mondays at 01:00) exceed the limit.

**Important:** This is NOT caused by multiple gateway instances. Even if `gateway status` shows warnings about "PID already in use", verify with `ps aux | grep <PID>` — stale PIDs may have already exited.

**Fix:**
1. Check cron job schedules: `hermes cron list`
2. Identify overlapping times (e.g., multiple tasks at 01:00 on Mondays)
3. Stagger task times to spread out weixin deliveries:
   ```bash
   # Example: move one task from 01:00 to 01:30
   hermes cron update <job_id> --schedule "30 1 * * 1"
   ```
4. Or merge multiple reports into a single scheduled task

## Security Notes

- Default policy is `allowlist` — only explicitly allowed users can send messages
- User IDs are in format: `oXXXXXXXXXXXXXXXXXXXXXXXX@im.wechat`
- Keep `WEIXIN_ALLOWED_USERS` updated when users change
- Consider `WEIXIN_DM_POLICY=allowlist` for production use

## Multi-Gateway Notes

When running multiple gateway profiles (e.g., `default` + `dingtalk-worker`):
- Check each profile's `.env` — commented-out `WEIXIN_*` vars mean that gateway won't load weixin
- `gateway status` warnings about "PID already in use" can be stale — always verify with `ps aux`
- Rate limiting is caused by cron job timing, NOT by gateway conflicts

## Related Skills

- `webhook-subscriptions` — For event-driven automation
- `send_message` — For sending messages via connected platforms