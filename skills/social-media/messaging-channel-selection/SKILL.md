---
name: messaging-channel-selection
description: Compare and configure messaging platforms (WeChat, DingTalk, Feishu, Telegram) for optimal message delivery without truncation.
version: 1.0.0
metadata:
  hermes:
    tags: [messaging, channels, wechat, dingtalk, feishu, telegram, truncation]
---

# Messaging Channel Selection & Optimization Guide

Use this guide when users experience message truncation, need better messaging channels, or want to compare platform options.

## Common Problem: Message Truncation

**Symptom**: Long messages get cut off mid-sentence, poor reading experience.

**Root Cause**: Platform message length limits + inadequate auto-segmentation.

## Platform Comparison

| Platform | Max Length | Auto-Segment | China Access | Notes |
|----------|-----------|--------------|--------------|-------|
| **WeChat** | ~2000-4000? | Manual (1500/3000) | ✅ Native | Most convenient but truncates badly |
| **DingTalk** | **20,000** | ✅ Yes | ✅ Native | Best for long content |
| **Feishu** | **8,000** | ✅ Yes (4000/chunk) | ✅ Native | Good balance |
| **Telegram** | 40,960 | ✅ Yes | ❌ Needs VPN | Best overall but blocked in China |
| **Discord** | 2,000 | ✅ Yes | ❌ Needs VPN | Good for tech discussions |
| **Email** | Unlimited | N/A | ✅ Native | Slow but no limits |

## Recommended Strategies

### Strategy A: Hybrid Approach (Most Practical)
```
WeChat  → Short, quick conversations
DingTalk/Feishu → Long content, technical discussions
```
- Keep WeChat for convenience
- Use DingTalk/Feishu as primary channel for serious work

### Strategy B: Single Channel Migration
```
If WeChat truncation is unacceptable → Migrate to DingTalk (20k limit)
```

### Strategy C: WeChat Optimization
```
1. Enable human-like delays: HUMANIZE_MESSAGES=true
2. Modify gateway code for better auto-segmentation
3. Set分段长度 to 2000 chars with auto-continuation markers
```

## Platform Setup

### DingTalk Configuration
**Requirements:**
- DingTalk developer account
- Enterprise app or robot bot

**Steps:**
1. Go to [DingTalk Developer Portal](https://open.dingtalk.com)
2. Create enterprise application
3. Get `DINGTALK_CLIENT_ID` and `DINGTALK_CLIENT_ID`
4. Add to `~/.hermes/.env`:
   ```bash
   DINGTALK_CLIENT_ID=your_client_id
   DINGTALK_CLIENT_SECRET=your_client_secret
   ```
5. Enable in `config.yaml`:
   ```yaml
   platforms:
     dingtalk:
       enabled: true
   ```
6. Restart gateway

**Tech Details:**
- Uses `dingtalk-stream` SDK (WebSocket long connection)
- Max message: 20,000 characters
- Auto-segments via `truncate_message()` method

### Feishu Configuration
**Requirements:**
- Feishu developer account
- Self-built application

**Steps:**
1. Go to [Feishu Developer Portal](https://open.feishu.cn)
2. Create self-built app
3. Get `APP_ID` and `APP_SECRET`
4. Add to `~/.hermes/.env`:
   ```bash
   FEISHU_APP_ID=your_app_id
   FEISHU_APP_SECRET=your_app_secret
   FEISHU_ALLOWED_USERS=your_user_id
   ```
5. Enable in `config.yaml`:
   ```yaml
   platforms:
     feishu:
       enabled: true
   ```
6. Restart gateway

**Tech Details:**
- Supports WebSocket + Webhook modes
- Max message: 8,000 characters
- Auto-segments to 4,000 chars by default

### Telegram Configuration
**Requirements:**
- Telegram account
- Bot from @BotFather
- Chat ID

**Steps:**
1. Create bot via @BotFather
2. Get your Chat ID
3. Add to `~/.hermes/.env`:
   ```bash
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_HOME_CHANNEL=your_chat_id
   ```
4. Enable in `config.yaml`:
   ```yaml
   platforms:
     telegram:
       enabled: true
   ```
5. Restart gateway

## Diagnostic Commands

### Check Available Platforms
```bash
ls ~/.hermes/hermes-agent/gateway/platforms/
# Shows: weixin.py, dingtalk.py, feishu.py, telegram.py, etc.
```

### Check Current Channel Directory
```bash
cat ~/.hermes/channel_directory.json
```

### Check Platform Status
```bash
cat ~/.hermes/gateway_state.json
```

### View Platform Logs
```bash
grep -E "dingtalk|feishu|weixin" ~/.hermes/logs/gateway.log | tail -30
```

## Troubleshooting

### Platform Not Connecting
1. Check dependencies: `pip list | grep -E "dingtalk|lark|telegram"`
2. Verify env vars: `grep PLATFORM ~/.hermes/.env`
3. Check config.yaml: `grep -A5 platforms ~/.hermes/config.yaml`
4. Restart gateway: `systemctl --user restart hermes-gateway`

### Message Still Truncating
1. Check platform's MAX_MESSAGE_LENGTH in source code
2. Verify auto-segmentation is enabled
3. Consider switching to platform with higher limit
4. Modify gateway code for custom segmentation logic

### WeChat-Specific Issues
- Check allowlist: `WEIXIN_ALLOWED_USERS` in `.env`
- Verify user ID format: `oXXXXXXXX@im.wechat`
- Check gateway state: `gateway_state.json` should show `"state": "connected"`

## Optimization Tips

### For Long-Form Content
- **Best**: DingTalk (20k chars)
- **Good**: Feishu (8k chars)
- **Acceptable**: Telegram (40k chars, but needs VPN)

### For Quick Chat
- **Best**: WeChat (native, no setup)
- **Good**: Any platform for short messages

### For Technical Discussions
- **Best**: Feishu/DingTalk (Markdown support, auto-formatting)
- **Good**: Discord (if accessible)

### For Maximum Flexibility
- **Setup**: Multiple channels (WeChat + DingTalk)
- **Use Case**: WeChat for quick, DingTalk for serious work

## When to Create New Channel

Consider adding a new channel when:
- Current platform has persistent truncation issues
- User needs platform-specific features (e.g., file sharing)
- Access restrictions block current platform
- Multiple channels improve workflow segmentation

## Related Skills

- `weixin-troubleshooting` - WeChat-specific issues
- `knowledge-management-system` - Content organization across channels
- `webhook-subscriptions` - Event-driven automation

---

## Example Decision Tree

```
User complains about truncation?
├─ Can use VPN? → Yes → Telegram (best experience)
│                → No → Continue
├─ Need enterprise features? → Yes → DingTalk (20k limit)
│                            → No → Continue
├─ Want balance of convenience/limits? → Feishu (8k limit)
└─ Must use WeChat only? → Optimize segmentation logic
```
