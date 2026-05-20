# DingTalk Group Message Filtering

## 问题描述

Gateway 连接成功但无法接收某些用户或群组的消息：
- 日志中只显示特定用户的 `inbound message`
- 其他用户的消息被静默忽略
- 没有任何错误信息

## 根本原因

`config.yaml` 中有两个过滤机制：

### 1. `allowed_chats`（群组硬过滤）

```yaml
platforms:
  dingtalk:
    extra:
      allowed_chats:
        - cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=
```

- 不在列表中的群组消息被**静默忽略**
- 私聊（DM）不受 `allowed_chats` 限制

### 2. `require_mention`（触发条件）

```yaml
platforms:
  dingtalk:
    extra:
      require_mention: true  # 群组消息需要@bot 才能触发
```

- `true`: 只有@机器人的消息被处理
- `false`: `allowed_chats` 中的所有群组消息都被处理

## `_should_process_message` 逻辑

`gateway/platforms/dingtalk.py`:

```python
def _should_process_message(message, text, is_group, chat_id):
    if not is_group:
        return True  # DMs always allowed
    
    allowed = self._dingtalk_allowed_chats()
    if allowed and chat_id not in allowed:
        return False  # Group not in allowed_chats → IGNORE
    
    if not self._dingtalk_require_mention():
        return True  # No mention required → ACCEPT
    
    if self._message_mentions_bot(message):  # is_in_at_list
        return True  # @mentioned → ACCEPT
    
    return False  # Not @mentioned → IGNORE
```

## 诊断命令

```bash
# 检查 config.yaml 中的过滤设置
grep -A10 "dingtalk:" ~/.hermes/profiles/dingtalk-worker/config.yaml

# 检查 gateway 日志中的过滤消息
tail -100 ~/.hermes/profiles/dingtalk-worker/logs/gateway.log | grep -E "(Dropping|Empty message|skipping)"

# 验证 allowed_chats 与实际群组 chat_id 是否匹配
cat ~/.hermes/profiles/dingtalk-worker/employee_mapping.yaml
```

## 解决方案

### 方案 1：添加所有相关群组 chat_id 到 `allowed_chats`

```yaml
platforms:
  dingtalk:
    extra:
      allowed_chats:
        - cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=  # 数智化工作群
        - cidxxx...  # 其他群
```

### 方案 2：设置 `require_mention: false` 接收所有群组消息

```yaml
platforms:
  dingtalk:
    extra:
      require_mention: false  # 接收 allowed_chats 中的所有消息
```

### 方案 3：让用户@机器人（如果 `require_mention: true`）

```
@assistant 我是员工A
@assistant 测试消息
```

## 验证方法

```bash
# 配置变更后重启
systemctl restart hermes-dingtalk-worker

# 监控日志
journalctl -u hermes-dingtalk-worker -f | grep "inbound message"

# 从不同用户/群组发送测试消息
# 检查是否出现在日志中
```

## 重要发现

### Emoji 消息被跳过

`gateway/platforms/dingtalk.py` 第 624-626 行：

```python
if not text and not media_urls:
    logger.debug("[%s] Empty message, skipping", self.name)
    return
```

- **纯 Emoji 消息** 既没有文本也没有媒体 URL
- 被判定为"空消息"直接跳过
- 不会触发 `inbound message` 日志
- 无法捕获发送者的 User ID

**解决方案：** 让员工发送**文本消息**（不是 emoji）来捕获 User ID。

## 配置示例

`/root/.hermes/profiles/dingtalk-worker/config.yaml` (第 265-272 行)：

```yaml
platforms:
  dingtalk:
    enabled: true
    extra:
      # 明确指定要监听的群 ID
      allowed_chats:
        - cidc906Hc41Ys3Ftk+3piCsBi7KdaRaSYa5vvhlubaR15M=
      # 群消息是否需要@assistant 才能触发（false = 所有群消息都接收）
      require_mention: false
```
