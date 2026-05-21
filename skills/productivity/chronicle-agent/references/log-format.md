# Chronicle Agent Log Format

## Output Structure

```
# Chronicle Agent 扫描报告

**扫描时间**: YYYY-MM-DD HH:MM  
**窗口**: YYYY-MM-DD HH:MM - YYYY-MM-DD HH:MM

---

## 1. [Platform] · [Topic] (HH:MM-HH:MM)

**会话**: [Platform] / [Model]
**用户**: [User name if available]

**事件**:
- ...

**技术分析**:
- ...

**决策与解决**:
- ✅ ...

---

## 2. [Platform] · [Topic] (HH:MM-HH:MM)

...
```

## Event Types

### Decisions (决策)
- User explicitly states a choice: "我们决定用 X 方案", "改成 Y 配置", "选择这个方案"

### Task Assignments (任务分配)
- User assigns work: "帮我部署 X", "创建一个 Y", "需要完成 Z"

### Technical Discussions (技术讨论)
- Problem troubleshooting, error analysis, architecture discussions, code reviews

### Important Conclusions (重要结论)
- Investigation results, fix solutions, deployment outcomes, performance analysis

### Commitment Changes (承诺变更)
- Plan adjustments, priority updates, schedule changes

## Filtering Rules

### Keep
- ✅ Substantive content with clear purpose
- ✅ Technical discussions with depth
- ✅ Explicit decisions or assignments

### Filter Out
- ❌ Greetings ("你好", "hello", "hi")
- ❌ Short acknowledgments ("好的", "收到", "明白了")
- ❌ System prompts (`[IMPORTANT: ...]`)
- ❌ Context compaction markers (`[CONTEXT COMPACTION — REFERENCE ONLY]`)
- ❌ Cron session messages (automated tasks)

## Output Path

```
<KNOWLEDGE_DIR>/03-个人运营/05-频道历史/YYYY-MM-DD-HH.md
```

## Git Commit

After writing, commit with:
```bash
cd <KNOWLEDGE_DIR>
git add -A
git commit -m "auto: Chronicle Agent scan YYYY-MM-DD HH:MM"
```

Note: commit from the knowledge directory, not the hermes root.

## Empty Window Handling

When no substantive content is found, write a minimal log file with clear status message and commit it. Use the exact template below:

```
# Chronicle Agent 扫描报告
**扫描时间**: YYYY-MM-DD HH:MM
**窗口**: YYYY-MM-DD HH:MM - YYYY-MM-DD HH:MM

---

## 无实质性内容

本窗口内所有会话均为系统自动任务（cron sessions），未检测到用户发起的实质性内容（决策、任务分配、技术讨论、重要结论、承诺变更）。

涉及的会话类型：
- cron 任务会话（自动执行的定时任务）
- 系统提示消息（[IMPORTANT: You are running as a scheduled cron job...]）

---

*本报告由 Chronicle Agent (史官) 自动生成*
```

This ensures consistent reporting even when no substantive content is found.

## Silent Protocol

If no substantive content found in window, output exactly `[SILENT]` (nothing else) and nothing more. Never combine [SILENT] with content.
