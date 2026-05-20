# WebUI 多进程冲突排查指南

## 症状

- WebUI 启动后 HTTP 返回非 200（如 503、空响应）
- Agent Bridge 连接失败
- 端口 8648 已被占用但进程未显示

## 根因

旧 WebUI 进程未完全退出（可能残留 zombie 进程或子进程），新进程无法绑定端口。

## 完整排查流程

### 1. 检查所有相关进程

```bash
# WebUI 主进程
ps aux | grep "hermes-web-ui" | grep -v grep

# WebUI 内部进程（index.js）
ps aux | grep "index.js" | grep -v grep

# Agent Bridge 进程
ps aux | grep "agent-bridge" | grep -v grep
```

### 2. 检查端口占用

```bash
ss -tlnp | grep 8648
```

如果显示端口被占用但 ps 看不到进程，可能是僵尸进程或权限问题。

### 3. 强制清理

```bash
# 杀死所有 Hermes WebUI 相关进程
pkill -9 -f "hermes-web-ui"
pkill -9 -f "agent-bridge"

# 等待进程清理
sleep 2

# 验证端口已释放
ss -tlnp | grep 8648  # 应无输出
```

### 4. 正确启动

**手动启动**（测试用）：
```bash
node /root/.hermes/node/lib/node_modules/hermes-web-ui/bin/hermes-web-ui.mjs --port 8648
```

**systemd 服务**（生产用）：
```bash
systemctl restart hermes-web-ui
```

### 5. 验证启动成功

```bash
# HTTP 响应
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8648/  # 应返回 200

# 健康检查
curl -s http://127.0.0.1:8648/health | jq '.'
```

## 预防措施

1. **停止服务时等待完全退出**：
   ```bash
   systemctl stop hermes-web-ui
   sleep 3
   ss -tlnp | grep 8648  # 确认端口释放
   ```

2. **重启前检查状态**：
   ```bash
   # 不要依赖 systemctl status（可能卡住）
   ss -tlnp | grep 8648
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8648/
   ```

3. **避免手动启动与服务冲突**：
   - 使用 systemd 时，不要同时手动启动
   - 手动测试时，先 `systemctl stop hermes-web-ui`

## 启动命令变更历史

| 时间 | 命令 | 状态 |
|------|------|------|
| 2026-05-17 前 | `./node_modules/.bin/hermes-web-ui` | ❌ 已废弃（文件不存在） |
| 2026-05-17 后 | `node bin/hermes-web-ui.mjs --port 8648` | ✅ 正确 |

**注意**：npm 包安装后，启动脚本位于 `bin/hermes-web-ui.mjs`，不是 `bin/hermes-web-ui`。