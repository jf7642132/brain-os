---
name: 修复输出截断问题
description: 修复 "Response truncated due to output length limit" 输出截断问题的永久解决方法
---

# 修复输出截断问题

## 问题现象
WeChat/DingTalk 等消息通道出现 `⚠️ Response truncated due to output length limit` 错误，消息被截断无法完整发送。

## 根本原因
Gateway 会话上下文累积过长，超过了平台消息长度限制，仅调整发送分段大小无法根治，总会再次占满。

## 永久修复步骤

1. **先运行 doctor 清理会话**
   ```bash
   hermes doctor
   ```
   这会清理所有过期会话和累积的上下文垃圾。

2. **重启 gateway 服务**
   ```bash
   systemctl restart hermes-gateway
   ```

3. **验证修复**
   发送长消息测试，确认不再出现截断。

## 预防措施
每次重启 gateway 前都应该先运行 `hermes doctor` 清理会话，这是避免输出截断问题复发的关键习惯。
