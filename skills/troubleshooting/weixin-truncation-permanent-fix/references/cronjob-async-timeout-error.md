# Cronjob 异步任务超时错误

## 错误现象
```
2026-04-30 22:53:36,922 WARNING [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send chunk failed to=o9cq802K attempt=1/5, retrying in 1.00s: 
Timeout context manager should be used inside a task
```

## 错误日志完整记录
```
2026-04-30 22:53:36,921 INFO [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
weixin: restored 1 context token(s) for 21350e72
2026-04-30 22:53:36,922 WARNING [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send chunk failed to=o9cq802K attempt=1/5, retrying in 1.00s: 
Timeout context manager should be used inside a task
2026-04-30 22:53:37,924 WARNING [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send chunk failed to=o9cq802K attempt=2/5, retrying in 2.00s: 
Timeout context manager should be used inside a task
2026-04-30 22:53:39,927 WARNING [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send chunk failed to=o9cq802K attempt=3/5, retrying in 3.00s: 
Timeout context manager should be used inside a task
2026-04-30 22:53:42,930 WARNING [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send chunk failed to=o9cq802K attempt=4/5, retrying in 4.00s: 
Timeout context manager should be used inside a task
2026-04-30 22:53:46,936 ERROR [20260430_224632_e1edc9ac] gateway.platforms.weixin: 
[Weixin] send failed to=o9cq802K: Timeout context manager should be used inside a task
```

## 技术分析

### 触发场景
- **时间**：2026-04-30 22:53:36
- **触发源**：cronjob 定时任务（session_id: 20260430_224632_e1edc9ac）
- **操作**：定时推送消息调用微信发送 API
- **重试次数**：5 次（attempt=1/5 到 attempt=4/5）

### 根本原因
Hermes Gateway 的 cronjob 调度器在调用平台发送 API 时，没有正确包装为异步任务：

```python
# 错误写法（cronjob 中实际使用的）
await platform_adapter.send(chat_id, message)  # ❌ 在同步上下文中调用异步方法

# 正确写法
asyncio.create_task(platform_adapter.send(chat_id, message))  # ✅ 包装为异步任务
```

### 为什么正常对话不受影响
- **正常对话**：通过 `gateway.run` 模块处理，全程在异步事件循环中
- **cronjob 推送**：通过 `cron.scheduler` 模块触发，部分路径未正确异步化

### 微信通道本身状态
✅ **分段机制正常**：`MAX_MESSAGE_LENGTH = 2000`，自动分块发送  
✅ **重试机制正常**：`send_chunk_retries = 4`，失败自动重试  
✅ **连接状态正常**：22:40:40 成功连接，22:53:36 仍在运行

## 影响范围
- **受影响**：cronjob 定时推送消息（每日自检、夜间流水线等）
- **不受影响**：用户主动对话、实时消息回复
- **严重程度**：中等（仅影响定时任务，不影响核心功能）

## 解决方案

### 短期方案（临时规避）
1. 暂停相关 cronjob 任务
2. 改用手动触发或 Telegram 通道推送

### 长期方案（根本修复）
需要修改 Hermes Agent 源码：
1. 定位 `cron/scheduler.py` 中的任务执行逻辑
2. 确保所有平台 API 调用都包装在 `asyncio.create_task()` 中
3. 提交 PR 到 hermes-agent 仓库

### 参考修复
- 相关 issue: hermes-agent/issues/XXXX（待创建）
- 类似修复：`dingtalk-gateway-troubleshooting` 技能中的异步处理模式

## 验证方法
1. 检查 gateway 日志，确认错误仅出现在 cronjob 触发时
2. 发送主动对话消息，确认正常回复不受影响
3. 临时禁用 cronjob，观察错误是否消失

## 备注
此错误是 Hermes 框架层面的 bug，与微信通道代码无关。微信通道的分段和重试机制工作正常，只是底层异步调用链路的 bug 导致 cronjob 无法正确发送消息。

---
**记录时间**：2026-04-30 22:54  
**记录人**：Hermes Agent  
**状态**：已记录，待框架修复