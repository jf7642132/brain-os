# DingTalk Webhook 加签修复

## 问题描述

当使用带加签（signature）的 DingTalk Webhook 发送消息时，`send_message` 工具返回错误：

```
DingTalk API error: 错误描述:机器人发送签名不匹配;解决方案:请确认签名和生成签名的时间戳必须都放在调用的网址中
```

## 根本原因

`_send_dingtalk` 函数（`hermes-agent/tools/send_message_tool.py`）在处理带加签的 Webhook 时：

**错误做法**：将 `timestamp` 和 `sign` 作为 HTTP 头发送
```python
headers["timestamp"] = timestamp
headers["sign"] = sign
```

**正确做法**：将 `timestamp` 和 `sign` 作为 **URL 查询参数** 附加到 Webhook URL
```python
parsed = urlparse(webhook_url)
query = parse_qs(parsed.query, keep_blank_values=True)
query["timestamp"] = [timestamp]
query["sign"] = [sign]
new_query = "&".join(f"{k}={v[0]}" for k, v in query.items())
webhook_url = urlunparse(parsed._replace(query=new_query))
```

## 修复代码

文件：`hermes-agent/tools/send_message_tool.py`

```python
async def _send_dingtalk(extra, chat_id, message):
    """Send via DingTalk robot webhook.

    Supports webhook with 加签 (signature): set ``DINGTALK_WEBHOOK_SIGN`` or
    ``webhook_sign`` in extra to enable HMAC-SHA256 signing.
    IMPORTANT: timestamp and sign must be appended as URL query params, not headers.
    """
    try:
        import httpx
    except ImportError:
        return {"error": "httpx not installed"}
    
    webhook_url = extra.get("webhook_url") or os.getenv("DINGTALK_WEBHOOK_URL", "")
    if not webhook_url:
        return {"error": "DingTalk not configured."}

    # Prepare URL with 加签 (signature) query params if needed
    webhook_sign = extra.get("webhook_sign") or os.getenv("DINGTALK_WEBHOOK_SIGN", "")
    if webhook_sign:
        import time
        import hmac
        import hashlib
        import base64
        from urllib.parse import urlparse, urlunparse, parse_qs

        timestamp = str(int(time.time() * 1000))
        sign_string = f"{timestamp}\n{webhook_sign}"
        sign = base64.b64encode(
            hmac.new(webhook_sign.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).digest()
        ).decode("utf-8")

        # Append timestamp and sign as query parameters to the webhook URL
        parsed = urlparse(webhook_url)
        query = parse_qs(parsed.query, keep_blank_values=True)
        query["timestamp"] = [timestamp]
        query["sign"] = [sign]
        new_query = "&".join(f"{k}={v[0]}" for k, v in query.items())
        webhook_url = urlunparse(parsed._replace(query=new_query))

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            webhook_url,
            json={"msgtype": "text", "text": {"content": message}},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode", 0) != 0:
            return {"error": f"DingTalk API error: {data.get('errmsg', 'unknown')}"}
    
    return {"success": True, "platform": "dingtalk", "chat_id": chat_id}
```

## 配置步骤

1. 在 `.env` 中配置 Webhook URL 和加签：
   ```bash
   DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=xxx"
   DINGTALK_WEBHOOK_SIGN="SECxxx"
   ```

2. 重启 gateway：
   ```bash
   systemctl restart hermes-dingtalk-worker
   ```

3. 验证修复：
   ```bash
   # 创建测试任务
   hermes kanban create "测试 send_message" --assignee dingtalk-worker
   
   # 检查任务状态
   hermes kanban show <task-id>
   ```

## 验证结果

| 测试任务 | 状态 | 结果 |
|----------|------|------|
| 修复前 | done | ❌ 签名不匹配 |
| 修复后 | done | ✅ 加签修复验证通过 |

## 参考

- DingTalk 官方文档：[加签安全设置](https://open.dingtalk.com/document/orgapp/obtain-an-access-token-by-using-an-app-key-and-an-app-secret)
- 钉钉机器人 Webhook 要求：timestamp 和 sign 必须是 URL 查询参数，不是 HTTP 头
