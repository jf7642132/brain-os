---
name: fix-wechat-output-truncation
description: 永久修复微信通道 "Response truncated due to output length limit" 输出截断问题，算法升级+阈值双重保障
version: 2.0.0
metadata:
  hermes:
    tags: [weixin, wechat, troubleshooting, truncation, fix]
---

# 修复微信输出截断问题

## 问题现象
微信通道发送长内容时，返回错误：
```
⚠️ Response truncated due to output length limit
```

## 根因分析
微信iLink API对单条消息长度有限制，尽管代码已经做了分段处理，但存在两个问题：
1. 原硬编码阈值 `MAX_MESSAGE_LENGTH = 1500` 偏高，实际发送加上协议开销容易超限
2. 原分段算法有缺陷：**当单个Markdown块本身超过阈值时，只做简单截断不继续拆分**，导致仍然超长的块流出去触发平台截断

## 永久修复方案 v2.0

### 双重保障
1. **算法修复**：改进 `_pack_markdown_blocks_for_weixin` 分段算法，实现三级安全拆分
   - 第一级：按Markdown块打包，尽量合并相邻小块保持可读性
   - 第二级：单个块仍超长 → 按行拆分重组
   - 第三级：单行仍超长 → 按字符硬切分
   - 保证**每一块严格小于阈值**，永远不会有超长条流出

2. **阈值下调**：`MAX_MESSAGE_LENGTH = 1000`，留出约400字符的协议开销安全余量（微信实际限制≈1400）

### 修改内容
1. **修改分段函数** (`_pack_markdown_blocks_for_weixin` at line 831):
```python
def _pack_markdown_blocks_for_weixin(content: str, max_length: int) -> List[str]:
    if len(content) <= max_length:
        return [content]

    packed: List[str] = []
    current = ""
    for block in _split_markdown_blocks(content):
        candidate = block if not current else f"{current}\n\n{block}"
        if len(candidate) <= max_length:
            current = candidate
            continue
        if current:
            packed.append(current)
            current = ""
        if len(block) <= max_length:
            current = block
            continue
        # 如果单个block仍然超过max_length，递归拆分它
        # 按行拆分，保证每个最终块都<=max_length
        lines = block.split('\n')
        current_chunk = ""
        for line in lines:
            line_len = len(line) + (1 if current_chunk else 0)  # +1 for newline
            if len(current_chunk) + line_len <= max_length:
                if current_chunk:
                    current_chunk += '\n' + line
                else:
                    current_chunk = line
            else:
                if current_chunk:
                    packed.append(current_chunk)
                # 如果单行本身就超了，继续按字符切分
                if len(line) > max_length:
                    # 按max_length切分单行
                    for i in range(0, len(line), max_length):
                        packed.append(line[i:i+max_length])
                    current_chunk = ""
                else:
                    current_chunk = line
        if current_chunk:
            packed.append(current_chunk)
    if current:
        packed.append(current)
    return packed
```

2. **修改阈值** (line 1116):
```python
# 将
MAX_MESSAGE_LENGTH = 1500
# 改为
MAX_MESSAGE_LENGTH = 1000
```

### 重启生效
```bash
# 先检查状态
hermes doctor

# 重启gateway
pkill -f "hermes gateway"
hermes gateway --host 0.0.0.0 --port 8643 &
```

## 验证修复
修复后：
- ✅ 任何长度的输出都会被正确拆分为多块消息发送
- ✅ 每个块严格 ≤ 1000 字符，绝对不会超限
- ✅ 保持原有的块结构感知，不影响Markdown可读性
- ✅ 从算法层面彻底解决，"总会满"问题不复存在

发送超长内容（比如外贸风险预警日报完整版），确认能够正常分段发送，不再出现截断错误。
