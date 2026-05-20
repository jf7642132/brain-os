# Telegram Delivery Troubleshooting

## Common Error: Bot Can't Send Messages to Bot

**Error Message**: `Forbidden: the bot can't send messages to the bot`

**Cause**: The cron task's `deliver` is set to `telegram` with `telegram_chat_id` pointing to a bot account, but Telegram bots cannot send messages to other bots.

**Solution**: Change delivery mode to `local` (output stays in workspace) or use a user/group chat ID.

### Fix Steps

1. Edit `~/.hermes/cron/jobs.json`:
```json
{
  "deliver": "local",
  "telegram_chat_id": null,
  "delivery_mode": null
}
```

2. Or use a user/group chat ID:
```json
{
  "deliver": "telegram",
  "telegram_chat_id": "<YOUR_TELEGRAM_CHAT_ID>",  // User chat ID, not bot
  "delivery_mode": "telegram"
}
```

### Verification

```bash
# Check task configuration
hermes cron status <task_id>

# Look for:
# deliver: local (or telegram with valid chat_id)
# telegram_chat_id: null (or valid user/group ID)
```

### When to Use Each Mode

| Mode | Use Case |
|------|----------|
| `local` | Internal tasks, debugging, tasks that produce files |
| `telegram` (user) | Notifications to user's personal chat |
| `telegram` (group) | Notifications to team/group channels |
| `weixin` | WeChat notifications (use with caution, rate limits apply) |

## WeChat Rate Limiting

**Error Message**: `iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited`

**Cause**: WeChat iLink API has rate limits. Multiple tasks sending at similar times can trigger limits.

**Solution**: 
1. Stagger task schedules to avoid concurrent delivery
2. Switch to Telegram for high-frequency notifications
3. Use `local` delivery for non-urgent tasks
