# Gateway 重启循环故障排查

## 问题现象

Gateway 服务频繁重启，systemd 显示 `Restart counter is at N`，日志中反复出现：
```
Received SIGTERM as a planned --replace takeover — exiting cleanly
```

## 根因分析

**多 Gateway 进程互相 `--replace` 导致无限重启循环**

当两个 Gateway 进程同时运行（如 `default` 和 `dingtalk-worker`），且都使用 `--replace` 参数时：
1. 新 Gateway 启动时发送信号终止旧 Gateway
2. systemd 配置 `Restart=always`，被终止的 Gateway 自动重启
3. 重启的 Gateway 又 `--replace` 另一个 → 无限循环

**额外问题**：systemd 的 `TimeoutStopSec` 小于 Gateway 的 `drain_timeout`
- Gateway 的 `drain_timeout=180s`（等待未完成的任务完成）
- systemd 的 `TimeoutStopSec=90s`（发送 SIGTERM 后等待时间）
- 结果：drain 未完成就被 SIGKILL，导致任务丢失

## 修复步骤

### 1. 停止所有 Gateway 进程

```bash
# 停止所有 hermes gateway 进程
pkill -f "hermes.*gateway"

# 或者逐个停止
hermes gateway stop
hermes --profile dingtalk-worker gateway stop

# 如果上述无效，强制 kill
kill -9 $(ps aux | grep "hermes.*gateway" | grep -v grep | awk '{print $2}')
```

### 2. 修复 systemd 配置

```bash
# 修改 TimeoutStopSec: 90 → 300
# 确保 TimeoutStopSec >= drain_timeout + 30s (drain_timeout 默认 180s)

# 主 Gateway
sed -i 's/TimeoutStopSec=90/TimeoutStopSec=300/' /etc/systemd/system/hermes-gateway.service

# dingtalk-worker Gateway
sed -i 's/TimeoutStopSec=90/TimeoutStopSec=300/' /etc/systemd/system/hermes-dingtalk-worker.service

# 重载 systemd
systemctl daemon-reload

# 重启 Gateway
systemctl restart hermes-gateway
systemctl restart hermes-dingtalk-worker
```

### 3. 验证修复

```bash
# 检查进程
ps aux | grep "hermes.*gateway" | grep -v grep
# 应该只有 2 个进程：default 和 dingtalk-worker

# 检查状态
systemctl status hermes-gateway
systemctl status hermes-dingtalk-worker

# 检查日志
tail -50 ~/.hermes/logs/gateway.log
tail -50 ~/.hermes/profiles/dingtalk-worker/logs/gateway.log
```

## 预防措施

### 1. 避免多 Gateway 互相干扰

- `default` Gateway 负责主实例（所有平台 + kanban dispatcher）
- `dingtalk-worker` Gateway 仅负责钉钉通道 + kanban 通知
- 两个 Gateway 使用不同的 `--replace` 上下文，不会互相 kill

### 2. systemd 配置规范

```ini
[Service]
# TimeoutStopSec 必须 >= drain_timeout + 30s
# drain_timeout 默认 180s，所以 TimeoutStopSec 至少 210s
TimeoutStopSec=300

# Restart 策略
Restart=always
RestartSec=5
# 避免频繁重启
RestartMaxDelaySec=300
RestartSteps=5
```

### 3. 检查当前 Gateway 进程

```bash
# 列出所有 Gateway 进程
ps aux | grep "hermes.*gateway" | grep -v grep

# 检查 systemd 服务状态
systemctl list-units | grep hermes-gateway
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `/etc/systemd/system/hermes-gateway.service` | 主 Gateway systemd 服务 |
| `/etc/systemd/system/hermes-dingtalk-worker.service` | dingtalk-worker Gateway systemd 服务 |
| `~/.hermes/logs/gateway.log` | 主 Gateway 日志 |
| `~/.hermes/profiles/dingtalk-worker/logs/gateway.log` | dingtalk-worker Gateway 日志 |

## 相关技能

- `dingtalk-troubleshooting` - DingTalk 专用故障排查
- `hermes-agent` - Hermes Agent 通用操作指南
