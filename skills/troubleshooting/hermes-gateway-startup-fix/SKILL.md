---
name: hermes-gateway-startup-fix
category: troubleshooting
description: Diagnose and fix Hermes Gateway startup failures (systemd, missing modules, YAML errors, platform authentication)
---

# Hermes Gateway Startup Fix

Diagnose and fix common startup failures when adding new messaging platforms to Hermes Gateway.

## Common Issues & Solutions

### 1. ModuleNotFoundError: No module named 'yaml'
**Symptom**: Gateway fails immediately on startup with:
```
ModuleNotFoundError: No module named 'yaml'
```

**Root Cause**: systemd service file is using **system Python** instead of **virtual environment Python**, but `pyyaml` is only installed in the virtual environment.

**Solution 1 (Direct fix)**:
1. Check the service file:
```bash
cat /etc/systemd/system/hermes-gateway.service
```

2. Fix ExecStart and WorkingDirectory:
```ini
# WRONG:
ExecStart=/root/.local/share/uv/python/cpython-3.11.15-linux-x86_64-gnu/bin/python3.11 ...
WorkingDirectory=/root/.hermes/hermes-agent/venv/src/hermes-agent

# CORRECT:
ExecStart=/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
WorkingDirectory=/root/.hermes
```

3. Apply changes:
```bash
sed -i 's|^ExecStart=.*|ExecStart=/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace|' /etc/systemd/system/hermes-gateway.service
sed -i 's|^WorkingDirectory=.*|WorkingDirectory=/root/.hermes|' /etc/systemd/system/hermes-gateway.service
systemctl daemon-reload
```

4. Verify yaml works in virtualenv:
```bash
/root/.hermes/hermes-agent/venv/bin/python -c "import yaml; print('OK')"
```

**Solution 2 (If Solution 1 still fails - uv virtualenv issue)**:
Even if ExecStart points to the correct Python, systemd may still not find the modules due to uv's symlink setup. Use a bash script to activate the environment first:

1. Create a startup script `/root/.hermes/gateway-start.sh`:
```bash
cat > /root/.hermes/gateway-start.sh << 'EOF'
#!/bin/bash
cd /root/.hermes
source /root/.hermes/hermes-agent/venv/bin/activate
exec python -m hermes_cli.main gateway run --replace
EOF
chmod +x /root/.hermes/gateway-start.sh
```

2. Update systemd service:
```bash
sed -i 's|^ExecStart=.*|ExecStart=/bin/bash /root/.hermes/gateway-start.sh|' /etc/systemd/system/hermes-gateway.service
systemctl daemon-reload
```

This ensures the virtual environment is fully activated before starting.

### 2. Missing platform configuration
**Symptom**: Added platform to `platform_toolsets` but forgot to declare it in `platforms:` section.

**Root Cause**: Hermes gateway expects every platform in `platform_toolsets` to have an entry in `platforms:`, even if it's `null` (disabled).

**Solution**: Edit `~/.hermes/config.yaml`:
```yaml
platforms:
  weixin: null
  dingtalk: null
  telegram: null  # ← Add this line for any new platform
```

### 3. Telegram: InvalidToken error
**Symptom**:
```
telegram.error.InvalidToken: The token `...` was rejected by the server.
```

**Causes**:
- Token is incorrect/copied wrong
- Bot token format is wrong (should look like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ef1`)

**Solutions**:
- **Disable Telegram temporarily**: Set `telegram: null` in `platforms:` to let gateway start with other platforms
- **Fix token**: Get correct token from @BotFather in Telegram

### 4. YAML syntax errors after editing
**Symptom**: Gateway fails to load config

**Diagnosis**:
```python
#!/usr/bin/env python3
import yaml
with open('/root/.hermes/config.yaml') as f:
    config = yaml.safe_load(f)
print("✓ YAML OK")
```

**Common mistakes**:
- Missing space after `#` for comments
- Indentation wrong (use spaces not tabs, match existing indentation
- Forgetting colon after key

### 5. Manual test startup (bypass systemd)
**Always test manually first** to see real-time errors:
```bash
# Stop systemd service first
systemctl stop hermes-gateway

# Manual test
cd /root/.hermes
/root/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
```

This shows full error output immediately without journalctl.

## Quick Diagnostic Checklist

1. ❌ Does manual test above work? → If yes, problem is with systemd config. If no, the error message tells you the real issue.
2. ❌ Is YAML syntax valid? → Test with Python yaml import.
3. ❌ Is every platform in `platform_toolsets` also in `platforms:`?
4. ❌ Is ExecStart pointing to virtualenv Python?
5. ❌ Are API keys/bot tokens valid? (Test with manual test shows this clearly)

## Expected Result After Fix

```
Starting Hermes Gateway...
Session storage: /root/.hermes/sessions
Connecting to weixin...
✓ weixin connected
1 hook(s) loaded
Gateway running with 1 platform(s)
Channel directory built: 1 target(s)
Press Ctrl+C to stop
Cron ticker started (interval=60s)
```

Gateway is now running successfully.

## Gateway 重启循环故障

**症状**：Gateway 频繁重启，systemd 显示 `Restart counter is at N`，日志反复出现 `Received SIGTERM as a planned --replace takeover`。

**根因**：多 Gateway 进程（如 `default` 和 `dingtalk-worker`）互相 `--replace` 导致无限重启循环。systemd 的 `TimeoutStopSec` 小于 Gateway 的 `drain_timeout`，导致 drain 未完成就被 SIGKILL。

**修复**：
1. Kill 所有 Gateway 进程：`pkill -f "hermes.*gateway"`
2. 修复 TimeoutStopSec：`sed -i 's/TimeoutStopSec=90/TimeoutStopSec=300/' /etc/systemd/system/hermes-gateway.service`（同样修复 dingtalk-worker）
3. `systemctl daemon-reload && systemctl restart hermes-gateway`

详见：`references/gateway-restart-loop-fix.md`（在 `hermes-agent` 技能目录下）
