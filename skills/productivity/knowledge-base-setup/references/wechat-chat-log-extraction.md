# WeChat Chat Log Knowledge Extraction

## Overview

Extract knowledge (bugs, solutions, best practices) from WeChat chat logs and populate a knowledge base.

## When to Use

- ERP/CRM system运维团队通过微信群沟通故障处理
- 需要从历史聊天记录中整理出常见问题和解决方案
- 建立运维知识库、FAQ、故障案例库

## Workflow

### Step 1: Export Chat Logs

**Recommended Tools** (all open-source, local processing, no data upload):

| Tool | GitHub | Pre-built | Notes |
|------|--------|:---------:|-------|
| WeChatMsg-2025 | LC044/WeChatMsg | ❌ (源码运行) | 功能最全，支持AI聊天 |
| wx-dump-4j | xuchengsheng/wx-dump-4j | ✅ | 有预编译包，Web界面 |
| wechatDataBackup | git-jiadong/wechatDataBackup | ✅ | 一键导出，简单 |

**Security**: All tools process data locally. No cloud upload. Code is open-source and auditable.

### Step 2: Local Filtering (Critical Security Step)

Before sending any data to AI, filter locally to extract only relevant content:

**Keywords for Problems/Bugs:**
```
bug, BUG, buggy
报错, 错误, 异常
故障, 问题, 无法, 不能, 失败
```

**Keywords for Solutions:**
```
解决, 修复, 搞定, 处理, OK, 好的, 已解决
```

**Python Filtering Script:**
```python
import pandas as pd

df = pd.read_csv('wechat_export.csv')
df['content_lower'] = df['content'].str.lower()

problem_keywords = ['bug', '报错', '错误', '异常', '故障', '问题', '无法']
solution_keywords = ['解决', '修复', '搞定', '处理', 'OK', '好的', '已解决']

problems = df[df['content_lower'].str.contains('|'.join(problem_keywords), na=False)]
solutions = df[df['content_lower'].str.contains('|'.join(solution_keywords), na=False)]

problems.to_csv('erp_problems.csv', index=False)
solutions.to_csv('erp_solutions.csv', index=False)
```

### Step 3: Send Filtered Data to AI

Send only the filtered CSV files to the AI for analysis.

### Step 4: AI Analysis & Knowledge Base Generation

AI will:
1. **Classify problems** by module/severity/type
2. **Extract bugs** (system defects, functional anomalies)
3. **Extract solutions** (handling process, workarounds)
4. **Generate structured knowledge base**

**Output Structure:**
```
knowledge/ERP系统运维/
├── 01-常见问题FAQ.md          # Q&A format, searchable
├── 02-故障案例库.md           # Detailed case studies with root cause
├── 03-操作手册补充.md          # Missing steps from official docs
├── 04-开发测试问题追踪.md      # Development/testing issues
└── 05-解决方案索引.md          # Quick reference by symptom
```

### Step 5: Review & Refine

- User reviews AI-generated content
- Add context that AI missed (business rules, internal conventions)
- Link to official documentation
- Set up periodic refresh (e.g., monthly)

## Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| **Sensitive data exposure** | Filter locally before sending to AI; only share problem/solution fragments |
| **Incomplete context** | AI may miss business context; user must review and add |
| **Outdated solutions** | Chat logs may contain old workarounds; verify against current system |
| **Duplicate entries** | Same issue discussed multiple times; dedupe during analysis |
| **Tool compatibility** | WeChat version changes may break export tools; check tool compatibility |

## Security Checklist

- [ ] Use open-source tool (code auditable)
- [ ] Process data locally (no cloud upload)
- [ ] Filter before sending to AI (only share relevant fragments)
- [ ] Remove sensitive info (customer data, financial info, credentials)
- [ ] Verify AI output before publishing to knowledge base

## Related Skills

- `knowledge-base-setup` — Knowledge base structure and templates
- `kanban-orchestrator` — Task decomposition for knowledge base population