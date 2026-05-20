# DingTalk Webhook 加签 (Signature) 修复

## 问题描述

`send_message` tool 使用 DingTalk Webhook 发送消息时，遇到签名验证失败：

```
DingTalk API error: 错误描述:机器人发送签名不匹配
```

## 根本原因

`_send_dingtalk` 函数（`send_message_tool.py` 第 1501-1559 行）错误地实现了 webhook 加签：

| 错误做法 | 正确做法 |
|----------|----------|
| 将 `timestamp` 和 `sign` 作为 **HTTP 头** 发送 | 将 `timestamp` 和 `sign` 作为 **URL 查询参数** 附加 |

## 钉钉 Webhook 加签格式

**正确的 URL 格式：**
```
https://oapi.dingtalk.com/robot/send?access_token=xxx&timestamp=1234567890&sign=ABCDEF...
```

**错误的格式（会被拒绝）：**
```
https://oapi.dingtalk.com/robot/send?access_token=xxx
Headers: {"timestamp": "1234567890", "sign": "ABCDEF..."}
```

## 签名生成代码

```python
import time
import hmac
import hashlib
import base64
from urllib.parse import urlparse, urlunparse, parse_qs

webhook_sign = "SEC1b0d5cc6ad778ce2ae0b97c683f649e20c98e45a7220bcb20801b557664d17a3"
timestamp = str(int(time.time() * 1000))
sign_string = f"{timestamp}\n{webhook_sign}"
sign = base64.b64encode(
    hmac.new(webhook_sign.encode("utf-8"), sign_string.encode("utf-8"), hashlib.sha256).digest()
).decode("utf-8")

# 附加到 URL 作为查询参数（不是 headers！）
parsed = urlparse(webhook_url)
query = parse_qs(parsed.query, keep_blank_values=True)
query["timestamp"] = [timestamp]
query["sign"] = [sign]
new_query = "&".join(f"{k}={v[0]}" for k, v in query.items())
webhook_url = urlunparse(parsed._replace(query=new_query))
```

## 修复位置

`/root/.hermes/hermes-agent/tools/send_message_tool.py` (lines 1501-1559)

## 验证方法

```bash
# 创建测试任务
hermes kanban create --assignee dingtalk-worker --title "测试 Webhook 加签" --body "验证 send_message 能否成功发送钉钉消息"

# 查看 gateway 日志
journalctl -u hermes-dingtalk-worker -f | grep -E "(signature|send|error)"
```

**预期成功：**
```
INFO gateway: send_message called with targets="dingtalk:cidxxx"
DEBUG dingtalk: Webhook URL: https://oapi.dingtalk.com/robot/send?access_token=xxx&timestamp=1234567890&sign=ABCDEF...
INFO dingtalk: Response: {"errcode": 0, "errmsg": "ok"}
```

**预期失败：**
```
ERROR dingtalk: DingTalk API error: 错误描述:机器人发送签名不匹配
```

## 相关配置

```bash
# dingtalk-worker/.env
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=b4bdef6803c8a0887d14585bc0e68b9b69b0661c14ce1df747eb71aa68d66442
DINGTALK_WEBHOOK_SIGN=SEC1b0d5cc6ad778ce2ae0b97c683f649e20c98e45a7220bcb20801b557664d17a3
```
