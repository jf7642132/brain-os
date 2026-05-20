# 多通道配置修改范围 — 不要误禁用其他通道

## Problem

When a user asks to change a messaging channel (e.g., "change to telegram"), there's a risk of incorrectly disabling other channels that the user still needs.

## Example Incident (2026-05-19)

**User request**: "所有发送通道都改成 telegram 吧"

**Incorrect action taken**: Disabled Weixin and Dingtalk channels on the main instance by commenting out their configuration in `.env`.

**User correction**: "主实例其他通道我都要用的，不要禁用"

**Root cause**: Assumed the user wanted to switch to Telegram-only mode, when they actually wanted Telegram as an additional channel while keeping Weixin and Dingtalk.

## Correct Approach

When modifying channel configuration:

1. **Clarify intent first** if ambiguous:
   - "是要只用 Telegram，还是把 Telegram 作为新增通道？"
   - "需要禁用 Weixin 和 Dingtalk 吗？"

2. **Only modify the target channel** unless explicitly told otherwise:
   - Fix Telegram home channel → only change `TELEGRAM_HOME_CHANNEL`
   - Switch cron delivery → only change `--deliver` flag
   - Do NOT comment out other channels' configuration

3. **Main instance typically keeps all channels**:
   - Different channels serve different purposes (personal vs work vs notifications)
   - Disabling channels should be an explicit user decision

## Configuration Locations

| Channel | Config File | Key Variables |
|---------|-------------|---------------|
| Telegram | `~/.hermes/.env` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_HOME_CHANNEL`, `TELEGRAM_ALLOWED_USERS` |
| Weixin | `~/.hermes/.env` | `WEIXIN_TOKEN`, `WEIXIN_HOME_CHANNEL`, `WEIXIN_ALLOWED_USERS` |
| Dingtalk | `~/.hermes/.env` | `DINGTALK_CLIENT_ID`, `DINGTALK_CLIENT_SECRET`, `DINGTALK_HOME_CHANNEL` |

## Verification

After any channel configuration change:

```bash
# Check all channel configurations
grep -E "^(TELEGRAM|WEIXIN|DINGTALK)_" ~/.hermes/.env | grep -v "^#"

# Verify gateway picks up changes
hermes gateway restart

# Test each channel
hermes send telegram "Test"
hermes send weixin "Test"
hermes send dingtalk "Test"
```

## Related

- `references/cron-delivery-channel-switch.md` — Cron task delivery channel switching
- `hermes-agent` SKILL.md — Gateway platform configuration