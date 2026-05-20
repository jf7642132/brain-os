# Web UI 模型与推理配置参考

## Web UI 模型配置独立于 CLI

Web UI 使用的模型由 Web UI 后端决定，**不是** `config.yaml` 的 `model.default`。

```
CLI (hermes chat) ──→ 读取 config.yaml model.default
Web UI ──→ Web UI 后端自有模型配置
```

## 推理配置影响范围

| 配置项 | CLI | Web UI |
|--------|-----|--------|
| `display.show_reasoning` | ✅ 生效 | ❌ 不生效 |
| `delegation.reasoning_effort` | ✅ 生效 | ❌ 不生效 |
| `model.default` | ✅ 生效 | ❌ 不生效 |

**要关闭 Web UI 推理**，需要：
1. 检查 Web UI 后端是否有独立的推理配置（环境变量或配置文件）
2. 或在 Web UI 前端 UI 中寻找推理开关
3. 或在 API 调用层强制传入 `reasoning_effort: "none"`

`reasoning_effort` 可选值：`none`, `minimal`, `low`, `medium`, `high`, `xhigh`

## Web UI 显示"未连接"排查

### 症状
Web UI 界面显示"未连接"状态，但 API Server 实际已运行。

### 根本原因
API Server 未启动或未正确配置，Web UI 无法与 Gateway 建立 WebSocket 连接。

### 排查步骤

**1. 检查 API Server 是否启用**
```bash
grep "API_SERVER_ENABLED" ~/.hermes/.env
# 必须设置为 true
```

**2. 检查 API Server 端口**
```bash
ss -tlnp | grep 8642
# 应该显示 LISTEN 状态
```

**3. 检查 Gateway 日志**
```bash
grep "api_server" ~/.hermes/logs/gateway.log | tail -10
# 应该看到 "✓ api_server connected"
```

**4. 测试 API 端点**
```bash
curl http://127.0.0.1:8642/api/health
# 应该返回 JSON 响应
```

### 解决方案

在 `~/.hermes/.env` 中添加：
```bash
API_SERVER_ENABLED=true
```

然后重启 Gateway：
```bash
systemctl --user restart hermes-gateway
# 或如果 systemctl --user 不可用：
pkill -f "hermes.*gateway"
hermes gateway run --replace &
```

### 验证

1. Gateway 日志显示 `✓ api_server connected`
2. `curl http://127.0.0.1:8642/api/health` 返回 200
3. Web UI 状态从"未连接"变为"已连接"

## Web UI 流式输出

Web UI 使用 SSE (Server-Sent Events) 实现流式输出。

### 相关配置
- `display.streaming: true` — 启用流式输出（CLI 配置，Web UI 可能忽略）
- SSE 端点：`/api/chat/stream`

### 已知问题
- 旧版本 hermes-agent 存在流式输出 bug（#25676, #25723, #25583）
- 建议升级到最新版本

### 调试方法
1. 浏览器 DevTools → Network 标签 → 查找 SSE 连接
2. 查看是否有 404/500 错误或连接中断
3. 检查 `/api/chat/stream` 端点响应

## 双 Gateway 架构注意事项

当运行多个 Gateway 实例（如主 Gateway + dingtalk-worker）时：

1. **API Server 端口冲突**：每个 Gateway 实例会尝试绑定相同的 API Server 端口
2. **解决方案**：
   - 主 Gateway 启用 API Server（`API_SERVER_ENABLED=true`）
   - 从 Gateway 禁用 API Server（不设置或设为 `false`）
   - 或为每个 Gateway 配置不同的端口

3. **平台 Token 冲突**：Telegram/Weixin 等平台的 bot token 在同一时间只能被一个 Gateway 使用
   - 主 Gateway 连接所有平台
   - 从 Gateway 只连接需要的平台（如 dingtalk），并注释掉其他平台的 token

## 相关文档

- [Hermes Gateway 文档](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/)
- [API Server 配置](https://hermes-agent.nousresearch.com/docs/user-guide/configuration/)