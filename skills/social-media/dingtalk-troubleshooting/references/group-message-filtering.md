# DingTalk 群消息过滤规则

## 问题描述

员工在钉钉群发送消息，但 AI 没有收到或没有回复。

## 根本原因

DingTalk 适配器（`gateway/platforms/dingtalk.py`）有两层过滤：

### 1. `allowed_chats` 硬过滤

```yaml
platforms:
  dingtalk:
    extra:
      allowed_chats:
        - cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=
```

**行为**：如果 `allowed_chats` 非空，只有列表中的群才会接收消息。不在列表中的群消息被**静默忽略**。

**代码位置**：`gateway/platforms/dingtalk.py` 第 368-380 行

### 2. `require_mention` 触发规则

```yaml
platforms:
  dingtalk:
    extra:
      require_mention: true  # 或 false
```

**行为**：
- `require_mention: true` → 群消息必须 @assistant 才能触发响应
- `require_mention: false` → 所有群消息都接收（无需@）

**代码位置**：`gateway/platforms/dingtalk.py` 第 477-484 行

```python
def _should_process_message(self, message, text, is_group, chat_id):
    if not is_group:
        return True  # DM 不受限制
    
    allowed = self._dingtalk_allowed_chats()
    if allowed and chat_id not in allowed:
        return False  # 群不在允许列表中 → 忽略
    
    if not self._dingtalk_require_mention():
        return True  # 不需要@ → 直接接收
    
    if self._message_mentions_bot(message):  # is_in_at_list
        return True  # @了 bot → 接收
    
    return False  # 没@ → 忽略
```

### 3. `is_in_at_list` 属性

钉钉 Stream API 在消息对象中设置 `is_in_at_list` 属性，当 bot 被 @ 时。

## 过滤流程

```
员工发送消息
    ↓
检查 is_group?
    ↓ 是
检查 chat_id 在 allowed_chats 中?
    ↓ 否 → 静默忽略（无日志）
    ↓ 是
检查 require_mention?
    ↓ 否 → 接收
    ↓ 是
检查 is_in_at_list?
    ↓ 否 → 静默忽略（无日志）
    ↓ 是 → 接收
```

## 配置建议

### 场景 1：只接收特定群，无需@

```yaml
platforms:
  dingtalk:
    extra:
      allowed_chats:
        - <group-chat-id>
      require_mention: false
```

### 场景 2：只接收特定群，需要@

```yaml
platforms:
  dingtalk:
    extra:
      allowed_chats:
        - <group-chat-id>
      require_mention: true
```

### 场景 3：接收所有群，无需@

```yaml
platforms:
  dingtalk:
    extra:
      # allowed_chats 不设置 = 所有群
      require_mention: false
```

## 常见问题

### Q: 员工发消息我没收到，日志里也没有记录

**原因**：消息被过滤掉了，没有触发 `inbound message` 日志。

**检查**：
```bash
grep -A 5 "allowed_chats" ~/.hermes/profiles/dingtalk-worker/config.yaml
grep "require_mention" ~/.hermes/profiles/dingtalk-worker/config.yaml
```

### Q: 为什么 emoji 消息收不到？

**原因**：`_on_message` 函数过滤空消息（第 624-626 行）：

```python
if not text and not media_urls:
    logger.debug("[%s] Empty message, skipping", self.name)
    return
```

**解决**：要求员工发送文本消息（不是 emoji）。

### Q: 如何捕获员工的 DingTalk User ID？

**步骤**：
1. 要求员工在群中发送**文本消息**
2. 查看日志：`grep "inbound message" ~/.hermes/profiles/dingtalk-worker/logs/gateway.log`
3. 提取 `sender_id` 或 `user_id`
4. 填入 `employee_mapping.yaml`

## 调试命令

```bash
# 检查配置
grep -A 10 "dingtalk:" ~/.hermes/profiles/dingtalk-worker/config.yaml

# 查看实时日志
tail -f ~/.hermes/profiles/dingtalk-worker/logs/gateway.log | grep -E "inbound message|sender_id|user_id"

# 检查消息过滤日志
grep "Empty message, skipping" ~/.hermes/profiles/dingtalk-worker/logs/gateway.log
```