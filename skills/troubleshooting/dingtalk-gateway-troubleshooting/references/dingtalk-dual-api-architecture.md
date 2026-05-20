# DingTalk Dual-API Architecture

## 核心发现

dingtalk-worker 使用 **两套不同的 DingTalk API**：

| 功能 | API | 配置 | 状态 |
|------|-----|------|------|
| **接收消息** | Stream Mode (Robot SDK) | `DINGTALK_CLIENT_ID` + `DINGTALK_CLIENT_SECRET` | ✅ 工作 |
| **回复消息** | Session Webhook (从 incoming message 获取) | 从 Stream API 自动获取 | ✅ 工作 |
| **主动推送** | Webhook API | `DINGTALK_WEBHOOK_URL` + `DINGTALK_WEBHOOK_SIGN` | ⚠️ 需要加签修复 |

## 为什么需要两套 API？

### Stream Mode（WebSocket）
- 基于 WebSocket，实时消息接收
- 需要持久连接
- 用于接收用户消息和@提及

### Webhook API（HTTP）
- 基于 HTTP，主动消息发送
- 不需要持久连接
- 用于定时通知、kanban 提醒等主动推送

## 架构关系图

```
DingTalk Server
    │
    ├─ Stream Mode (WebSocket) ──► Gateway (接收消息)
    │                                   │
    │                                   ├─ Session Webhook (回复特定消息)
    │                                   │
    │                                   └─ send_message tool (主动推送)
    │                                           │
    │                                           └─ Webhook API (HTTP POST)
    │                                                   │
    │                                                   └─ 需要加签 (URL 参数)
    │
    └─ Webhook API (HTTP) ◄── send_message tool
```

## 配置说明

### Stream Mode 凭证（用于接收）

`/root/.hermes/profiles/dingtalk-worker/.env`:
```
DINGTALK_CLIENT_ID=dingnwbbcakq2zgjnesj
DINGTALK_CLIENT_SECRET=ROhMSzzHak3DfB_Z62QL9gy8lL9-hjIDQtZG8XMExHwvGMLi99Sd0Muli7CmLI9F
```

### Webhook 凭证（用于发送）

`/root/.hermes/profiles/dingtalk-worker/.env`:
```
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=b4bdef6803c8a0887d14585bc0e68b9b69b0661c14ce1df747eb71aa68d66442
DINGTALK_WEBHOOK_SIGN=SEC1b0d5cc6ad778ce2ae0b97c683f649e20c98e45a7220bcb20801b557664d17a3
```

## 关键约束

### Stream Mode 单连接限制
- DingTalk Stream API 只允许**一个活跃连接**
- 多个 gateway 实例不能共享同一个 Stream Mode 连接
- 解决方案：创建独立的 dingtalk-worker profile，主实例禁用 DingTalk

### 会话 Webhook 限制
- `session_webhook` 是从 incoming message 中获取的
- 只能用于回复收到消息的会话
- 不能用于向任意 chat_id 发送消息

### Webhook API 限制
- 需要单独配置 `DINGTALK_WEBHOOK_URL`
- 加签需要正确的 URL 参数格式（不是 HTTP 头）
- 适用于主动推送场景

## 最佳实践

1. **使用 Stream Mode 进行实时交互**
   - @提及、回复等交互场景
   - 需要持久连接

2. **使用 Webhook API 进行主动推送**
   - 定时通知、kanban 提醒
   - 不需要持久连接

3. **不要共享 Stream Mode 连接**
   - 多个 gateway 实例会导致冲突
   - 使用独立 profile 隔离

4. **Webhook 加签正确实现**
   - 使用 URL 参数（不是 HTTP 头）
   - timestamp 和 sign 必须都在 URL 中

## 排查命令

```bash
# 检查 Stream Mode 连接状态
tail -f ~/.hermes/profiles/dingtalk-worker/logs/gateway.log | grep "Connected via Stream Mode"

# 检查 Webhook 发送状态
journalctl -u hermes-dingtalk-worker -f | grep -E "(signature|send|error)"

# 检查配置
cat ~/.hermes/profiles/dingtalk-worker/.env | grep DINGTALK
```

## 常见问题

### Q: 为什么 gateway 能接收消息但不能发送？
A: 接收使用 Stream Mode（已配置），发送使用 Webhook API（需要额外配置加签）

### Q: 为什么两个 gateway 实例不能同时连接 DingTalk？
A: DingTalk Stream API 只允许一个活跃连接，会互相冲突

### Q: 为什么 send_message 需要 Webhook URL？
A: send_message 使用 Webhook API 主动推送，不是通过 Stream Mode 的 session_webhook
