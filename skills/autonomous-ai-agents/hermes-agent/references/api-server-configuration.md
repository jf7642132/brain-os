# API Server 配置与故障排查

## API Server 概述

API Server 是 Hermes Gateway 的内置 HTTP 服务，用于：
- Web UI 连接（WebSocket + SSE 流式输出）
- 外部系统集成
- 远程 API 调用

**默认端口**: 8642
**默认绑定**: 127.0.0.1 (仅本地访问)

## 启用 API Server

### 方法 1: 环境变量（推荐）

在 `~/.hermes/.env` 中添加：
```bash
API_SERVER_ENABLED=true
```

### 方法 2: 配置文件

在 `~/.hermes/config.yaml` 中添加：
```yaml
platforms:
  api_server:
    enabled: true
    port: 8642
    host: 127.0.0.1
    # 可选：设置 API key 用于认证
    # key: "your-secret-key"
    # 可选：CORS 配置
    # cors_origins: "*"
```

## 重启 Gateway

修改配置后需要重启 Gateway：

```bash
# 方法 1: systemctl（如果可用）
systemctl --user restart hermes-gateway

# 方法 2: 直接进程管理（如果 systemctl --user 不可用）
pkill -f "hermes.*gateway"
hermes gateway run --replace &
```

## 验证 API Server

### 1. 检查端口监听
```bash
ss -tlnp | grep 8642
```
应该显示：
```
LISTEN 0      128          127.0.0.1:8642         0.0.0.0:*    users:(("hermes",pid=XXXX,fd=XX))
```

### 2. 检查 Gateway 日志
```bash
grep "api_server" ~/.hermes/logs/gateway.log | tail -5
```
应该看到：
```
2026-05-17 18:57:54,037 WARNING gateway.platforms.api_server: [Api_Server] ⚠️  No API key configured
2026-05-17 18:57:54,038 INFO gateway.platforms.api_server: [Api_Server] API server listening on http://127.0.0.1:8642 (model: hermes-agent)
2026-05-17 18:57:54,043 INFO gateway.run: ✓ api_server connected
```

### 3. 测试 API 端点
```bash
curl http://127.0.0.1:8642/api/health
```
应该返回 JSON 响应。

### 4. 检查 Web UI 状态
打开 Web UI，状态应该显示"已连接"而不是"未连接"。

## 常用 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 发送消息 |
| `/api/chat/stream` | POST | 流式聊天（SSE） |
| `/api/sessions` | GET | 列出会话 |
| `/api/sessions/{id}` | GET | 获取会话详情 |
| `/api/cron` | GET | 列出 cron 作业 |

## 常见问题

### Q: API Server 启动失败

**症状**: Gateway 日志显示 `✗ api_server failed`

**排查**:
1. 检查端口是否被占用：`ss -tlnp | grep 8642`
2. 检查环境变量：`grep API_SERVER_ENABLED ~/.hermes/.env`
3. 检查配置文件：`grep -A5 "api_server" ~/.hermes/config.yaml`

**解决**:
```bash
# 如果端口被占用，先清理
pkill -f "hermes.*gateway"
sleep 2

# 确保环境变量设置正确
echo "API_SERVER_ENABLED=true" >> ~/.hermes/.env

# 重启
hermes gateway run --replace &
```

### Q: Web UI 显示"未连接"

**根本原因**: API Server 未启用或未正确配置

**解决**:
1. 在 `.env` 中设置 `API_SERVER_ENABLED=true`
2. 重启 Gateway
3. 验证端口监听和日志

### Q: 多个 Gateway 实例端口冲突

**症状**: 第二个 Gateway 启动失败，提示端口已占用

**解决**:
1. 主 Gateway 启用 API Server（`API_SERVER_ENABLED=true`）
2. 从 Gateway 禁用 API Server（不设置或设为 `false`）
3. 或为每个 Gateway 配置不同端口

### Q: 需要外部访问 API Server

**解决**:
```yaml
# config.yaml
platforms:
  api_server:
    enabled: true
    host: 0.0.0.0  # 监听所有接口
    port: 8642
    # 强烈建议设置 API key
    key: "your-secret-key"
```

然后配置防火墙允许访问：
```bash
# 如果使用 iptables
iptables -A INPUT -p tcp --dport 8642 -j ACCEPT

# 如果使用 firewalld
firewall-cmd --permanent --add-port=8642/tcp
firewall-cmd --reload
```

## 安全建议

1. **设置 API key**: 生产环境必须设置 `API_SERVER_KEY` 或 `platforms.api_server.key`
2. **限制绑定地址**: 默认 `127.0.0.1` 仅允许本地访问，不要随意改为 `0.0.0.0`
3. **配置 CORS**: 如果 Web UI 在不同域名，配置 `cors_origins`
4. **使用 HTTPS**: 如果通过公网访问，建议前置 Nginx 反向代理并启用 HTTPS

## 相关文档

- [Hermes Gateway 文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
- [API Server 配置](https://hermes-agent.nousresearch.com/docs/user-guide/configuration/)