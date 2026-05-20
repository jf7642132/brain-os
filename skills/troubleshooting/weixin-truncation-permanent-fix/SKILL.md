---
name: weixin-truncation-permanent-fix
description: 永久修复微信通道 "Response truncated due to output length limit" 输出截断问题
author: Hermes Agent
category: troubleshooting
tags: weixin, gateway, truncation, bugfix
---

# 微信输出截断永久修复指南

## 问题现象
微信通道消息被截断，显示 `Response truncated due to output length limit`

## 重要补充：异步任务超时错误
**现象**：日志中出现 `Timeout context manager should be used inside a task` 错误
**原因**：cronjob 定时任务在异步上下文中调用微信发送 API 时，缺少 `asyncio.create_task()` 包装
**影响**：仅影响 cronjob 触发的推送消息，正常对话流程不受影响
**状态**：这是 Hermes 框架层面的 bug，微信通道本身的分段和重试机制正常
**参考**：见 `references/cronjob-async-timeout-error.md`

## 根因分析
1. **venv 源码未同步**：主源码修改了，但 venv/lib 中的代码还是旧版本，gateway 实际运行的是 venv 代码
2. **阈值设置过高**：旧版本 `MAX_MESSAGE_LENGTH = 4000`，远高于微信实际限制（约 1400 字符）
3. **分段算法缺陷**：超长块只做简单截断，不递归拆分，导致超长消息漏出

## 修复步骤

### 1. 确认 gateway 使用哪个代码文件
```bash
ps aux | grep gateway
# 查看运行路径，确认是 venv 还是主源码
```

### 2. 找到所有 weixin.py 文件
```bash
find /root/.hermes -name "weixin.py"
# 通常有两个位置：
# /root/.hermes/opt/hermes-gateway/hermes/provider/weixin.py (主源码)
# /root/.hermes/venv/lib/python3.12/site-packages/hermes/provider/weixin.py (运行时)
```

### 3. 修改 venv 中的 MAX_MESSAGE_LENGTH
- 原值：`MAX_MESSAGE_LENGTH = 4000`
- 新值：`MAX_MESSAGE_LENGTH = 1000`
- 说明：留出 400 字符协议开销安全余量

### 4. 替换 _pack_markdown_blocks_for_weixin 函数
将简单截断算法替换为三级拆分算法：
```python
def _pack_markdown_blocks_for_weixin(blocks: list[str], max_len: int) -> list[str]:
    """三级拆分算法，彻底解决超长消息问题"""
    messages = []
    current = ""
    
    for block in blocks:
        if len(block) > max_len:
            if current:
                messages.append(current)
                current = ""
            
            lines = block.splitlines()
            for line in lines:
                if len(line) > max_len:
                    # 单行仍超长，按字符硬切
                    chunks = [line[i:i+max_len] for i in range(0, len(line), max_len)]
                    messages.extend(chunks)
                else:
                    if current and len(current) + 1 + len(line) <= max_len:
                        current += "\n" + line
                    else:
                        if current:
                            messages.append(current)
                        current = line
        else:
            if current and len(current) + 2 + len(block) <= max_len:
                current += "\n\n" + block
            else:
                if current:
                    messages.append(current)
                current = block
    
    if current:
        messages.append(current)
    
    return messages
```

### 5. 先 doctor 检查再重启
```bash
hermes doctor
# 检查通过后再重启
systemctl restart hermes-gateway
```

## 验证方法
发送一条超过 2000 字符的长消息，观察是否自动拆分为多条消息发送，无截断提示

## 注意事项
- ⚠️ 修改代码必须同时修改主源码和 venv 源码，保持一致
- ⚠️ 重启 gateway 前必须先运行 hermes doctor，这是硬性流程
- ⚠️ 升级 hermes 版本后需要重新检查和应用此修复
- ⚠️ **异步任务超时错误**：cronjob 推送消息可能遇到 `Timeout context manager should be used inside a task`，这是框架 bug，不影响正常对话。详见 `references/cronjob-async-timeout-error.md`
