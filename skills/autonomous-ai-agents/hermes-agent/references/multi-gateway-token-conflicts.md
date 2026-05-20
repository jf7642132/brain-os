# Multi-Gateway Token Conflicts

## Problem

When running multiple Hermes profiles (e.g., main instance + `dingtalk-worker`), each profile runs its own gateway process. Even if a profile has `platforms.telegram.enabled: false` in its config, the token may still be "reserved" by another process, causing errors:

```
[Telegram] Telegram bot token already in use (PID 2062450). Stop the other gateway first.
[Weixin] Weixin bot token already in use (PID 2062450). Stop the other gateway first.
```

## Architecture — Where Tokens Live

This is the key distinction most troubleshooting misses:

| Token type | Storage | Loading mechanism | Profile isolation |
|---|---|---|---|
| **Platform tokens** (Telegram BOT_TOKEN, Weixin TOKEN, etc.) | `.env` file | `get_env_path()` = `get_hermes_home() / ".env"` | ✅ Each profile has its own `.env` |
| **Model API keys** (OpenRouter, DeepSeek, etc.) | `auth.json` credential_pool | `_auth_file_path()` = `get_hermes_home() / "auth.json"` | ⚠️ Falls back to global `~/.hermes/auth.json` if profile has no local copy |

**Critical implication:**
- `hermes profile create --clone` copies the parent `.env` wholesale — including all platform tokens
- Platform adapters read tokens from env vars at startup, NOT from config.yaml
- So even `platforms.telegram.enabled: false` in config.yaml **does not prevent** the Telegram adapter from finding the token in `.env` and attempting to connect
- `auth.json` sharing is **intentional** — model credentials should be shared across profiles. Do not break this.

## Root Cause

The cloned `.env` file contains platform tokens (TELEGRAM_BOT_TOKEN, WEIXIN_TOKEN, etc.) that were inherited from the parent profile during `hermes profile create --clone`. The gateway's platform adapters discover these env vars independently of the config's `enabled` flag and attempt to claim the tokens.

When two gateway processes try to claim the same Telegram/Weixin bot token, the first one locks it and the second fails with "already in use".

## Diagnosis

### Step 1: Find all gateway processes

```bash
pgrep -fa "hermes.*gateway"
```

Output example:
```
2062450 .../python -m hermes_cli.main --profile dingtalk-worker gateway run --replace
2216845 .../python -m hermes_cli.main gateway run --replace
```

### Step 2: Check each process's env for unwanted tokens

```bash
# For dingtalk-worker
grep -E '^(TELEGRAM_BOT_TOKEN|WEIXIN_TOKEN|WECHAT)' ~/.hermes/profiles/dingtalk-worker/.env

# For main instance
grep -E '^(TELEGRAM_BOT_TOKEN|WEIXIN_TOKEN|WECHAT)' ~/.hermes/.env
```

### Step 3: Check logs for token conflicts

```bash
grep "already in use" ~/.hermes/logs/gateway.log
grep -E "Connecting to (telegram|weixin)" ~/.hermes/logs/gateway.log | tail -20
```

### Step 4: Check if auth.json exists in profile

```bash
ls -la ~/.hermes/profiles/dingtalk-worker/auth.json
# If this file doesn't exist — that's normal. The profile falls back to global auth.json.
```

## Solutions

### Correct Fix: Clean up cloned .env

The only reliable fix is to remove platform tokens from the profile's `.env` that the profile doesn't need:

```bash
# For a DingTalk-only worker:
sed -i 's/^WEIXIN_/#WEIXIN_/g' ~/.hermes/profiles/dingtalk-worker/.env
sed -i 's/^TELEGRAM_/#TELEGRAM_/g' ~/.hermes/profiles/dingtalk-worker/.env

# Restart
systemctl restart hermes-dingtalk-worker

# Verify
grep "already in use" /root/.hermes/profiles/dingtalk-worker/logs/gateway.log
# Should be empty — no more conflicts
```

If there are other platform tokens (discord, slack, etc.), check and comment those too:
```bash
grep -E '^[A-Z]+_(BOT_TOKEN|TOKEN|ACCOUNT_ID)=' ~/.hermes/profiles/dingtalk-worker/.env | grep -v '^#\|^HERMES\|^TAVILY\|GITHUB'
```

### Common Mistake: Only disabling in config.yaml

```yaml
platforms:
  telegram:
    enabled: false       # ← NOT sufficient
  weixin:
    enabled: false       # ← NOT sufficient
```

This doesn't work because the platform adapters detect token availability from env vars independently of the config's `enabled` flag. The config's `enabled` flag controls whether the adapter initializes fully, but the token reservation happens earlier.

### What NOT to do

- **Do NOT delete or isolate `auth.json`** — model API keys in credential_pool should be shared. Breaking this means the profile can't use your LLM providers.
- **Do NOT try to create separate auth.json per profile** — the credential pool fallback is by design. Model credentials belong at the global level.
- **Do NOT kill conflicting processes as the primary fix** — the conflict will return on restart because the `.env` still has the tokens.

## Prevention

When setting up a new profile, clean the cloned `.env` immediately after `hermes profile create --clone`:

```bash
# 1. Create profile
hermes profile create dingtalk-worker --clone

# 2. Clean platform tokens from cloned .env
sed -i 's/^TELEGRAM_/#TELEGRAM_/g' ~/.hermes/profiles/dingtalk-worker/.env
sed -i 's/^WEIXIN_/#WEIXIN_/g' ~/.hermes/profiles/dingtalk-worker/.env
sed -i 's/^WECHAT_/#WECHAT_/g' ~/.hermes/profiles/dingtalk-worker/.env

# 3. Disable unused platforms in config.yaml (belt and suspenders)
hermes --profile dingtalk-worker config set platforms.telegram.enabled false
hermes --profile dingtalk-worker config set platforms.weixin.enabled false

# 4. Start gateway
systemctl start hermes-dingtalk-worker

# 5. Verify
journalctl -u hermes-dingtalk-worker --no-pager -n 30 | grep -E "already in use|failed to connect|Connected"
```

## Related Issues

- `systemctl --user` may not work in containerized environments (see `hermes-agent` skill pitfall)
- The loading chain: `get_hermes_home()` → `get_env_path()` → `.env`. The profile's `HERMES_HOME` is set by systemd, so `.env` resolution is profile-correct. The problem is content of the cloned file, not the path resolution.