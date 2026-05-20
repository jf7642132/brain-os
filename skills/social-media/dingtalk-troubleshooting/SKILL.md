---
name: dingtalk-troubleshooting
description: Diagnose and fix DingTalk (钉钉) messaging issues in Hermes — Stream Mode connection problems, authentication, and connectivity issues.
version: 1.1.0
metadata:
  hermes:
    tags: [dingtalk, 钉钉，messaging, troubleshooting, stream-mode]
---

# DingTalk (钉钉) Troubleshooting Guide

Use this guide when DingTalk messaging isn't working — connection drops, reconnection loops, or messages not responding.

## Common Symptoms & Fixes

### 1. Stream Mode Connection Drops Immediately 🔴

**Symptom:** Gateway logs show:
```
INFO gateway.platforms.dingtalk: [Dingtalk] Connected via Stream Mode
INFO gateway.platforms.dingtalk: [Dingtalk] Reconnecting in 2s...
INFO gateway.platforms.dingtalk: [Dingtalk] Reconnecting in 5s...
INFO gateway.platforms.dingtalk: [Dingtalk] Reconnecting in 10s...
```

**Cause:** DingTalk Stream Mode WebSocket connection is being terminated by the server. Common reasons:

1. **DingTalk Enterprise IP Whitelist** - Enterprise version may require connection IP to be whitelisted
2. **App Disabled/Expired** - The DingTalk app may be deactivated or expired
3. **Network Restrictions** - Firewall or network blocking WebSocket connections
4. **Invalid Credentials** - Client ID/Secret may be revoked or incorrect

**Fix:**

1. **Check DingTalk App Status:**
   - Log in to [DingTalk Developer Console](https://open-dev.dingtalk.com/)
   - Verify app status is active
   - Confirm "Message Reception Mode" is set to "Stream Mode"
   - Check if app has been deactivated

2. **Verify Enterprise IP Whitelist:**
   - Contact your DingTalk admin
   - Check if your server IP needs to be added to the whitelist
   - Enterprise versions often require IP whitelisting for Stream Mode

3. **Test Network Connectivity:**
   ```bash
   # Test basic connectivity
   curl -v https://api.dingtalk.com/
   
   # Check if WebSocket ports are accessible
   telnet api.dingtalk.com 443
   ```

4. **Restart Gateway:**
   ```bash
   pkill -f "hermes gateway"
   hermes gateway run --replace
   ```

### 2. Messages Not Responding

**Symptom:** Gateway is connected but messages don't get responses

**Cause:** User not in allowlist or no session_webhook available

**Fix:**

1. **Check User Authorization:**
   ```bash
   grep DINGTALK ~/.hermes/.env
   ```

2. **Allow All Users (for testing):**
   ```bash
   # Add to ~/.hermes/.env
   DINGTALK_ALLOW_ALL_USERS=true
   ```

3. **Or Add Specific User IDs:**
   ```bash
   # Find your user ID from logs:
   grep "inbound message" ~/.hermes/logs/gateway.log | tail -5
   
   # Add to ~/.hermes/.env
   DINGTALK_ALLOWED_USERS=your-user-id,another-user-id
   ```

4. **Restart Gateway:**
   ```bash
   pkill -f "hermes gateway"
   hermes gateway run --replace
   ```

### 3. "401 Unauthorized" or "鉴权失败" Error 🔴

**Symptom:** Gateway logs show:
```
ERROR dingtalk_stream.client: open connection failed, error=401 Client Error: Unauthorized
response.text={"requestid":"...","code":"authFailed","message":"鉴权失败"}
```

**Cause:** Client ID or Client Secret is incorrect, truncated, or revoked.

**Fix:**

1. **Verify Secret Length:**
   ```bash
   # Check actual secret length (should be 60+ chars)
   grep "^DINGTALK_CLIENT_SECRET=" ~/.hermes/.env | wc -c
   # Expected: ~65+ characters (including newline)
   # If < 50, secret is truncated
   ```

2. **Check for Truncated/Masked Secret:**
   ```bash
   # Look for "***" or suspiciously short values
   grep "DINGTALK_CLIENT_SECRET" ~/.hermes/.env
   # Should show: DINGTALK_CLIENT_SECRET=aFKqQZ... (long string)
   # NOT: DINGTALK_CLIENT_SECRET=***
   ```

3. **Remove Duplicate Config:**
   ```bash
   # Check for duplicate DINGTALK entries
   grep -n "DINGTALK" ~/.hermes/.env
   # If multiple entries exist, keep only one set
   # Later entries override earlier ones
   ```

4. **Regenerate Secret (if truncated):**
   - Go to DingTalk Open Platform: https://open.dingtalk.com/
   - Find your app (Client ID: `dingocqnpb93zpzcccoe`)
   - Click "Update Secret" or "Reset Credentials"
   - Copy the FULL secret (do NOT truncate)
   - Update `.env`:
     ```bash
     # Edit ~/.hermes/.env
     # Replace: DINGTALK_CLIENT_SECRET=***
     # With: DINGTALK_CLIENT_SECRET=<full-new-secret>
     ```

5. **Restart Gateway:**
   ```bash
   pkill -f "hermes gateway"
   hermes gateway run --replace
   ```

### 4. "No session_webhook available" Error

**Symptom:** Response error shows:
```
SendResult(success=False, error="No session_webhook available. Reply must follow an incoming message.")
```

**Cause:** DingTalk session webhooks expire quickly. The bot can only reply to messages it has recently received.

**Fix:**
- Send a new message to the bot first
- Each incoming message provides a fresh session webhook for replies
- This is a normal DingTalk limitation

### 5. Reasoning Process Showing in Chat

**Symptom:** AI responses in DingTalk show "Thinking..." or reasoning content before the actual answer.

**Cause:** `show_reasoning: true` in `config.yaml` causes reasoning content to be included in chat responses.

**Fix:**
```yaml
# In ~/.hermes/config.yaml or profile's config.yaml
display:
  show_reasoning: false  # Hide reasoning process
```

Then restart the gateway:
```bash
systemctl restart hermes-dingtalk-worker
```

## Diagnostic Commands

### Check Gateway Status
```bash
# Is gateway running?
ps aux | grep "hermes gateway" | grep -v grep

# Check gateway logs
tail -50 ~/.hermes/logs/gateway.log

# Check for DingTalk-specific errors
grep -i "dingtalk\|Reconnecting" ~/.hermes/logs/gateway.log | tail -20
```

### Check DingTalk Configuration
```bash
# Check environment variables
grep DINGTALK ~/.hermes/.env

# Check config.yaml
grep -A 5 "dingtalk:" ~/.hermes/config.yaml
grep "show_reasoning" ~/.hermes/config.yaml
```

### Check DingTalk Dependencies
```bash
# Verify dingtalk-stream is installed
/root/.hermes/hermes-agent/venv/bin/pip show dingtalk-stream

# Should show:
# Name: dingtalk-stream
# Version: 0.24.3 (or higher)
```

### View Real-time Logs
```bash
# Watch logs as they happen
tail -f ~/.hermes/logs/gateway.log

# Filter for DingTalk messages
tail -f ~/.hermes/logs/gateway.log | grep dingtalk
```

## Configuration Reference

### `.env` Settings for DingTalk
```bash
# Required
DINGTALK_CLIENT_ID=your-app-key
DINGTALK_CLIENT_SECRET=your-app-secret

# Security: restrict who can interact with the bot
DINGTALK_ALLOWED_USERS=user-id-1,user-id-2

# Allow all users (bypass allowlist - use with caution)
DINGTALK_ALLOW_ALL_USERS=true

# Optional: specify home channel (NOT used by Stream API)
DINGTALK_HOME_CHANNEL=

# Webhook for send_message (required for proactive notifications)
DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=xxx"
DINGTALK_WEBHOOK_SIGN="SECxxx"  # 加签密钥
```

### `config.yaml` Settings
```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      client_id: "your-app-key"
      client_secret: "your-app-secret"
      # Chat whitelist - only these chats will receive messages
      allowed_chats:
        - cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=
      # Group messages require @mention to trigger response
      require_mention: false  # false = receive all group messages

# Hide reasoning output in chat responses
display:
  show_reasoning: false  # Set to false to hide reasoning process

# Group session settings
group_sessions_per_user: true  # Each user has separate context in groups
```

## Troubleshooting Workflow

1. **Is gateway running?** → `ps aux | grep gateway`
2. **Is dingtalk connected?** → Check logs for "Connected via Stream Mode"
3. **Check for reconnection loops** → `grep Reconnecting ~/.hermes/logs/gateway.log`
4. **Verify credentials** → Check `DINGTALK_CLIENT_ID` and `DINGTALK_CLIENT_SECRET` in `.env`
5. **Check user authorization** → Verify `DINGTALK_ALLOW_ALL_USERS=true` or add user IDs
6. **Test DingTalk app** → Log in to developer console and verify app status
7. **Restart gateway** → `pkill -f "hermes gateway" && hermes gateway run --replace`

## Advanced Debugging

### Enable Verbose Logging
```bash
# Edit config.yaml
logging:
  level: DEBUG
```

### Test DingTalk Stream Connection Directly
```python
import os
from dingtalk_stream import DingTalkStreamClient, Credential, ChatbotHandler

client_id = os.getenv("DINGTALK_CLIENT_ID")
client_secret = os.getenv("DINGTALK_CLIENT_SECRET")

credential = Credential(client_id, client_secret)
stream_client = DingTalkStreamClient(credential)

class TestHandler(ChatbotHandler):
    def process(self, message):
        print(f"Received: {message}")
        return dingtalk_stream.AckMessage.STATUS_OK, "OK"

stream_client.register_callback_handler(
    dingtalk_stream.ChatbotMessage.TOPIC, 
    TestHandler()
)

stream_client.start()  # This will show connection errors
```

## Security Notes

- Always set `DINGTALK_ALLOWED_USERS` or `DINGTALK_ALLOW_ALL_USERS`
- Without authorization settings, the gateway denies all users by default
- User IDs are alphanumeric strings configured by your DingTalk admin
- Keep `DINGTALK_CLIENT_SECRET` secure — never commit to Git
- Consider using `DINGTALK_ALLOW_ALL_USERS=true` only for personal use

## Related Skills

- `weixin-troubleshooting` — For WeChat messaging issues
- `webhook-subscriptions` — For event-driven automation
- `send_message` — For sending messages via connected platforms

## Reference Documents

- `references/webhook-signature-fix.md` — DingTalk Webhook 加签修复指南（timestamp/sign 必须作为 URL 查询参数）
- `references/group-message-filtering.md` — DingTalk 群消息过滤规则（allowed_chats、require_mention、is_in_at_list）
- `references/kanban-assignee-profiles.md` — Kanban assignee 配置规范（使用 profile 而非员工姓名）

## Capturing User IDs from Group Messages

When setting up DingTalk notifications (e.g., kanban task assignment), you need the DingTalk User ID for each team member.

### Required Condition
Team members must send a **text message** in the group. Emoji-only messages are silently dropped.

### Why Emoji-Only Messages Don't Work
The DingTalk adapter (`gateway/platforms/dingtalk.py`, lines 624-626) filters:
```python
if not text and not media_urls:
    logger.debug("[%s] Empty message, skipping", self.name)
    return
```
Emoji-only messages have no text content and no media URLs, so they are filtered out before any User ID can be captured.

### Check `require_mention` Configuration
If `require_mention: true` is set, messages without @assistant are also filtered. Check:
```bash
grep "require_mention" ~/.hermes/profiles/dingtalk-worker/config.yaml
```

Set to `false` to receive all group messages:
```yaml
platforms:
  dingtalk:
    extra:
      require_mention: false
```

### Steps to Capture User IDs
1. Ask the team member to send any text message in the group (even "1" or "你好" works)
2. Check the gateway logs for the inbound message record:
   ```bash
   grep "inbound message" ~/.hermes/profiles/dingtalk-worker/logs/gateway.log | tail -5
   ```
3. Extract the User ID from the log line — it appears as `sender_id=...` or `user_id=...`
4. Use the captured User ID for notification subscription:
   ```bash
   hermes kanban notify-subscribe <task-id> --platform dingtalk --chat-id <chat-id> --user-id <captured-user-id>
   ```

### Log Inspection
```bash
# Watch live for incoming messages
tail -f ~/.hermes/logs/gateway.log | grep -E "inbound message|sender_id|user_id"

# Or search recent logs
grep -B 2 -A 2 "sender_id\|user_id" ~/.hermes/logs/gateway.log | tail -20
```

## Running a Privacy-Isolated DingTalk Worker

When you need DingTalk to handle team notifications without exposing your personal memory/conversation history, create an independent Agent instance.

### Architecture
```
Main Instance (hermes-gateway)    DingTalk Worker (hermes-dingtalk-worker)
├── Memory: ON                      ├── Memory: OFF
├── All platforms enabled         ├── Only DingTalk enabled
├── Personal assistant            ├── Team task notifier
└── Has access to KB             └── No persistent state
```

### Setup

1. **Create the profile:**
   ```bash
   hermes profile create dingtalk-worker --clone
   ```

2. **Disable memory:**
   ```bash
   dingtalk-worker config set memory.memory_enabled false
   dingtalk-worker config set memory.user_profile_enabled false
   ```
3. **Disable all platforms except DingTalk:**
   ```bash
   dingtalk-worker config set platforms.weixin.enabled false
   dingtalk-worker config set platforms.telegram.enabled false
   dingtalk-worker config set platforms.api_server.enabled false
   ```

4. **Set tool permissions:**
   ```bash
   dingtalk-worker config set platform_toolsets.dingtalk "hermes-dingtalk"
   dingtalk-worker config set platform_toolsets.cli "kanban,terminal,file,web"
   ```

5. **Configure credentials in profile's .env:**
   The cloned profile has its own `/root/.hermes/profiles/dingtalk-worker/.env` — set `DINGTALK_CLIENT_ID` and `DINGTALK_CLIENT_SECRET` there.

6. **Disable DingTalk in main instance:**
   ```yaml
   # In ~/.hermes/config.yaml
   platforms:
     dingtalk:
       enabled: false  # Disable main instance's DingTalk
   ```
   Then restart main gateway.

7. **Start the worker gateway:**
   ```bash
   dingtalk-worker gateway run --replace
   ```

8. **Set up systemd service for auto-start:**
   Create `/etc/systemd/system/hermes-dingtalk-worker.service` with the worker profile's gateway command, then:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable hermes-dingtalk-worker
   sudo systemctl start hermes-dingtalk-worker
   ```

### Critical Constraints
- **Only one gateway can connect to a DingTalk bot at a time** — Stream API does not support multiple simultaneous connections. You must disable DingTalk in the main instance before starting the worker.
- The worker's config is at `/root/.hermes/profiles/dingtalk-worker/config.yaml`, not `~/.hermes/config.yaml`
- systemd services run as root, so path resolution works the same as interactive shell
- **Configure `require_mention: false`** to receive all group messages without requiring @mention:
  ```yaml
  platforms:
    dingtalk:
      extra:
        require_mention: false
  ```
- **Configure `show_reasoning: false`** to hide reasoning output in chat responses:
  ```yaml
  display:
    show_reasoning: false
  ```

## Common Pitfalls

1. **Stream Mode requires active WebSocket connection** — Unlike webhooks, Stream Mode maintains a persistent connection that can be dropped by network issues
2. **Enterprise versions may require IP whitelisting** — Check with your DingTalk admin
3. **Session webhooks expire quickly** — Reply must follow an incoming message
4. **App must be published/active** — Unpublished apps may have limited functionality
5. **Reconnection backoff is exponential** — 60s, so be patient
6. **DINGTALK_CLIENT_SECRET may be truncated/masked** — If secret shows as `***` or is too short (<50 chars), it may have been corrupted during file editing. Check with `grep DINGTALK_CLIENT_SECRET ~/.hermes/.env | wc -c` — should be ~65+ chars including key name. Regenerate secret from DingTalk console if needed.
7. **Duplicate DingTalk config in .env** — Multiple `DINGTALK_*` entries can cause one to override another. Clean up duplicates with:
   ```bash
   # Check for duplicates
   grep -n "DINGTALK" ~/.hermes/.env
   # Keep only one set of credentials, remove duplicates
   ```
8. **Gateway doesn't auto-load .env files** — The gateway loads `/root/.hermes/.env` only, NOT `.env.dingtalk`. If credentials are only in `.env.dingtalk`, they won't be loaded. Copy to main `.env` file.
9. **Emoji-only messages are silently dropped by DingTalk adapter** — The `_on_message` handler checks `if not text and not media_urls: return`, so pure emoji messages never reach the agent. Users must send text to be recognized.
10. **Two gateways cannot share the same bot token** — If you run a separate DingTalk worker profile, you MUST disable DingTalk in the main instance first. The second connection will fail or cause message routing issues.
11. **`allowed_chats` must be explicitly configured** — The DingTalk adapter (`gateway/platforms/dingtalk.py`, lines 368-380) implements a chat whitelist. If `allowed_chats` is set in `platforms.dingtalk.extra`, ONLY those chats will receive messages. If not set, all chats the bot is added to will work. **To ensure a specific group receives messages, add it to `allowed_chats` in config.yaml.**
12. **`DINGTALK_HOME_CHANNEL` in .env is NOT used by Stream API** — This environment variable is for other platforms (Telegram, Weixin) to specify a default chat for cron delivery. For DingTalk Stream Mode, it has no effect.
13. **Session webhook is recorded ONLY after receiving a message** — The `_session_webhooks` dict is populated when a message is received. If no message has been received from a chat, there's no session_webhook, and sending to that chat will fail with "No valid session_webhook" warning. **Solution: Have someone in the target group send a text message first to establish the session_webhook.**
14. **SOUL.md is injected as system prompt, not visible in session logs** — The SOUL.md content becomes part of the system prompt at runtime. Session logs show `session_meta → user → assistant → tool → tool_result → assistant` but NO "system" role entry.
15. **send_message target format must be `dingtalk:<ref>`** — Using `target: "platform"` will fail. Must use `target: "dingtalk:<chat_id>"` or `target: "dingtalk:<user_id>"`.
16. **DingTalk Webhook 加签要求 timestamp 和 sign 作为 URL 查询参数** — 不是 HTTP 头。错误配置会导致 "签名不匹配" 错误。修复方法见 `references/webhook-signature-fix.md`。
17. **`show_reasoning: true` 会导致推理过程显示在钉钉群** — 在 `config.yaml` 的 `display` 部分设置 `show_reasoning: false` 可隐藏推理过程。
18. **`require_mention: true` 会静默忽略未@的消息** — 如果员工发消息没收到回复，检查 `require_mention` 配置。设置为 `false` 可接收所有群消息。
19. **`employee_mapping.yaml` 中的员工姓名不应直接用作 kanban assignee** — 使用 profile 名称（如 `default`、`dingtalk-worker`），员工姓名仅用于 User ID 映射。

## Task Dispatch Workflow (dingtalk-worker)

When using a dedicated dingtalk-worker profile for task dispatch:

### Architecture
```
Main Kanban (user creates tasks)
    ↓ assignee = dingtalk-worker
Dispatcher spawns dingtalk-worker
    ↓ reads task description
dingtalk-worker extracts employee name
    ↓ looks up employee_mapping.yaml
dingtalk-worker sends DingTalk message @employee
```

### send_message Tool Usage

The dingtalk-worker uses the `send_message` tool from the `hermes-dingtalk` toolset:

```
# List available targets
send_message(action="list")

# Send to group chat
send_message(
    action="send",
    target="dingtalk:<chat_id>",
    message="@员工A 任务派发：..."
)

# Send to private chat
send_message(
    action="send",
    target="dingtalk:<user_id>",
    message="任务详情..."
)
```

**Pitfall**: `target: "platform"` is INVALID. Must be `target: "dingtalk:<ref>"`.

### Required Configuration

1. **Enable hermes-dingtalk toolset in dingtalk-worker:**
   ```yaml
   platform_toolsets:
     dingtalk: hermes-dingtalk
   ```

2. **Create employee mapping file** (`/root/.hermes/profiles/dingtalk-worker/employee_mapping.yaml`):
   ```yaml
   # 员工名字 → DingTalk User ID 映射
   员工A:
     user_id: "$:LWCP_v1:$VqWUaB7Bw9Guqgnj1pPqOw=="
     chat_id: "cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M="
   ```

3. **Configure allowed_chats for the target group:**
   ```yaml
   platforms:
     dingtalk:
       enabled: true
       extra:
         allowed_chats:
           - <group-chat-id>
   ```

4. **Restart gateway to apply changes:**
   ```bash
   systemctl restart hermes-dingtalk-worker
   ```

### Capturing Employee User IDs

Since Stream API only records session_webhook after receiving a message:

1. Ask each employee to send a **text message** (not emoji) in the target group
2. Check logs for inbound message:
   ```bash
   grep "inbound message" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log | tail -5
   ```
3. Extract user ID from log line (format: `$:LWCP_v1:$...`)
4. Fill in `employee_mapping.yaml`

### Sending @Mentions

The `send_message` tool supports @mentions by including the user ID in the message text with the `@` symbol. The DingTalk adapter will render it as an @mention.

**Important**: `mentioned_list` parameter requires DingTalk User IDs (the `$:LWCP_v1:$...` format), not nicknames.

## When to Contact DingTalk Support

- App appears active but still won't connect
- Enterprise features not working as expected
- Suspected platform-side issues or maintenance
- Need to request IP whitelist addition