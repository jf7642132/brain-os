---
name: hermes-web-ui-installation
description: 安装和配置 Hermes Web UI（官方npm包部署方式）
tags: []
related_skills: []
---

# Hermes Web UI 安装指南

## ⚠️ 部署方式：仅使用官方npm包

**自 2026-05-17 起，Hermes Web UI 仅支持官方npm包部署方式。源码构建方式已废弃，旧源码目录 `/root/hermes-web-ui/` 已删除。**

| 项目 | 官方npm包（唯一推荐） |
|------|----------------------|
| **安装命令** | `npm install -g hermes-web-ui` |
| **代码路径** | `/root/.hermes/node/lib/node_modules/hermes-web-ui/` |
| **启动命令** | `node .../hermes-web-ui/dist/server/index.js --port 8648` |
| **更新方式** | `npm update -g hermes-web-ui` |
| **数据目录** | `/root/.hermes-web-ui/`（.token + db + upload） |

---

## 安装步骤

### 1. 安装
```bash
npm config set registry https://registry.npmjs.org
npm install -g hermes-web-ui@latest
```

### 2. 确认安装
```bash
# 版本
cat /root/.hermes/node/lib/node_modules/hermes-web-ui/package.json | grep '"version"'

# CLI命令路径（入口脚本）
ls -la /root/.hermes/node/lib/node_modules/hermes-web-ui/bin/hermes-web-ui.mjs

# 启动脚本存在性验证
test -f /root/.hermes/node/lib/node_modules/hermes-web-ui/bin/hermes-web-ui.mjs && echo "OK" || echo "MISSING"
```

### 3. 配置 systemd 服务
创建 `/etc/systemd/system/hermes-web-ui.service`：

```ini
[Unit]
Description=Hermes Web UI (npm package)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.hermes
ExecStart=/root/.hermes/node/bin/node /root/.hermes/node/lib/node_modules/hermes-web-ui/bin/hermes-web-ui.mjs --port 8648
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=BIND_HOST=::
Environment=PORT=8648
```

**注意**：启动脚本为 `bin/hermes-web-ui.mjs`，不是 `dist/server/index.js`。旧版本文档可能有误。
[Install]
WantedBy=multi-user.target
```

### 4. 启用服务
```bash
systemctl daemon-reload
systemctl enable hermes-web-ui.service
systemctl start hermes-web-ui.service
```

### 5. 获取访问令牌
```bash
cat /root/.hermes-web-ui/.token
```

### 6. 更新
```bash
npm update -g hermes-web-ui && systemctl restart hermes-web-ui
```

---

## 验证

- 访问 http://<YOUR_SERVER_IP>:8648/
- HTTP响应：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8648/`
- 健康检查：`curl -s http://127.0.0.1:8648/health`
- 版本确认：`curl -s http://127.0.0.1:8648/health | jq '.webui_version'`

---

## ⚠️ 常见故障与排查

### 多进程冲突（多实例占用端口）

**症状**：WebUI 启动后端口未监听，或 Agent Bridge 连接失败，或 HTTP 返回非 200。

**根因**：旧 WebUI 进程未完全退出，新进程无法绑定端口。

**诊断**：
```bash
# 检查所有 Hermes WebUI 相关进程
ps aux | grep -E "hermes-web-ui|index.js" | grep -v grep

# 检查端口占用
ss -tlnp | grep 8648

# 检查 Agent Bridge 进程
ps aux | grep "agent-bridge" | grep -v grep
```

**修复**：
```bash
# 1. 杀死所有相关进程
pkill -f "hermes-web-ui"
pkill -f "agent-bridge"

# 2. 等待进程清理完成
sleep 2

# 3. 验证端口已释放
ss -tlnp | grep 8648  # 应该无输出

# 4. 使用正确命令启动
node /root/.hermes/node/lib/node_modules/hermes-web-ui/bin/hermes-web-ui.mjs --port 8648

# 5. 验证启动成功
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8648/  # 应返回 200
```

**注意**：systemd 服务模式下，使用 `systemctl restart hermes-web-ui` 而非手动启动。

### ⚠️ 认证与速率限制陷阱

Web UI 的认证令牌存储在 `~/.hermes-web-ui/.token`，而非 dist 目录下的 data 文件夹。速率限制锁定文件为 `~/.hermes-web-ui/.login-lock.json`。

**常见陷阱**：
- 多次使用错误 token 请求 API 会触发速率限制，即使后续使用正确 token 也会被拒绝
- 重启 Web UI 时旧进程未完全退出会导致端口冲突
- `systemctl status` 可能超时，不能作为主要诊断工具

**快速修复认证问题**：
```bash
echo '{}' > ~/.hermes-web-ui/.login-lock.json  # 清除速率限制
TOKEN=$(cat ~/.hermes-web-ui/.token)            # 获取当前 token
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8648/api/hermes/memory  # 验证
```

详见 [认证失败/速率限制修复](references/auth-rate-limit-fix.md)。

### `systemctl status` 超时（已知问题）
`systemctl status hermes-web-ui` 可能卡住/超时，**不要依赖它作为主要诊断工具**。改用以下命令：

```bash
# 1. 检查端口监听（最可靠）
ss -tlnp | grep 8648

# 2. 验证 HTTP 响应
curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:8648/

# 3. 检查进程
ps aux | grep "index.js" | grep -v grep
```

### 服务卡住恢复
如果服务进程存在但端口未监听，或 `systemctl status` 卡住：
```bash
systemctl stop hermes-web-ui
systemctl start hermes-web-ui
sleep 3
ss -tlnp | grep 8648
```

### 防火墙/网络问题
如果本地 `curl http://127.0.0.1:8648/` 返回 200 但远程无法访问：
- 检查服务器防火墙是否放行了 8648 端口
- 确认能路由到服务器 IP（如 `<YOUR_SERVER_IP>`）

### 数据完整性检查
```bash
# Token
cat /root/.hermes-web-ui/.token

# 数据库
ls -lh /root/.hermes-web-ui/hermes-web-ui.db

# 上传文件
ls /root/.hermes-web-ui/upload/
```

### Web UI 显示"未连接" / API 返回 "Unauthorized" 或 "Too many login attempts"

**症状**：Web UI 界面显示未连接，API 请求返回 `{"error":"Unauthorized"}` 或 `{"error":"Too many login attempts, please try again later"}`，即使服务进程在运行且端口正常监听。

**根因**：Web UI 内置速率限制机制（`~/.hermes-web-ui/.login-lock.json`）因多次认证失败触发 IP 锁定，或 `.token` 文件与运行实例不匹配。

**诊断**：
```bash
# 1. 检查速率限制状态
cat ~/.hermes-web-ui/.login-lock.json

# 2. 检查当前 token
cat ~/.hermes-web-ui/.token

# 3. 验证 API 是否真的拒绝
TOKEN=$(cat ~/.hermes-web-ui/.token)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8648/api/hermes/memory
```

**修复**：
```bash
# 1. 清除速率限制（重置所有 IP 锁定）
echo '{}' > ~/.hermes-web-ui/.login-lock.json

# 2. 杀死所有旧 Web UI 进程（防止多实例冲突）
pkill -f "hermes-web-ui"
pkill -f "index.js.*8648"
sleep 2

# 3. 验证端口已释放
ss -tlnp | grep 8648  # 应无输出

# 4. 重启 Web UI
cd /root/.hermes/node/lib/node_modules/hermes-web-ui
/root/.hermes/node/bin/node dist/server/index.js --port 8648 &

# 5. 验证修复
sleep 3
TOKEN=$(cat ~/.hermes-web-ui/.token)
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8648/api/hermes/memory
```

**注意**：速率限制文件路径为 `~/.hermes-web-ui/.login-lock.json`（不是 dist/data 目录下的）。Web UI 的 `dataDir` 配置指向 `__dirname/../data`（即 dist 同级目录），但速率限制和 token 文件实际存储在 `~/.hermes-web-ui/`。

---

## 参考资料
- [访问令牌](references/access-token.md) - 令牌位置、使用方式和重置方法
- [服务故障排查](references/troubleshooting.md) - 服务无法启动/无法访问的诊断流程和恢复步骤
- [迁移到官方npm包](references/migration-to-npm-package.md) - 从源码构建迁移到官方npm包的完整指南（历史参考）
- [认证失败/速率限制修复](references/auth-rate-limit-fix.md) - Web UI 显示"未连接"、API 返回 Unauthorized 或 Too many login attempts 的修复指南