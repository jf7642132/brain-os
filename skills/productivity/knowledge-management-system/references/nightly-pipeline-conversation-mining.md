# Nightly Pipeline: Conversation Mining

## Overview

The nightly pipeline runs at 03:00 daily and includes a "对话挖掘" (Conversation Mining) stage that extracts crystallizable knowledge from the previous 24 hours of conversation records.

## Pipeline Stages

| Time | Stage | Output |
|------|-------|--------|
| 02:00 | 文章整合 | Article integration report |
| 03:00 | 对话挖掘 | Conversation mining report |
| 04:00 | 知识放大器 | Knowledge amplifier report |

## Conversation Mining Process

### Step 1: Data Collection

1. Query `state.db` for sessions in the 24-hour window
2. Filter for non-cron sources: `cli`, `telegram`, `weixin`, `api_server`
3. Extract user messages and assistant non-tool-call responses

### Step 2: Content Extraction

Extract crystallizable knowledge:
- **Conclusions**: Decisions, findings, summaries
- **Decisions**: Configuration changes, approach selections
- **User Preferences**: Style, format, workflow preferences
- **Problem Solutions**: Bug fixes, workarounds, debugging paths

### Step 3: Output

Write to nightly digest:
```
<KNOWLEDGE_DIR>/04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-YYYY-MM-DD.md
```

### Step 4: Knowledge Graph Update

Update knowledge graph with new nodes:
- New projects
- New skills created/updated
- New patterns discovered

## Session Statistics (2026-05-14 Example)

| Metric | Value |
|--------|-------|
| Total sessions | 96 |
| Cron sessions | 45 |
| API server sessions | 51 |
| Effective user interactions | 4 |

## Key Outputs from 2026-05-14

1. **工作汇报**: 董事长调研数字化汇报材料
   - 汇报文档 + 2 种风格 PPT (pitch-deck, weekly-report)
   - Location: `03-个人运营/05-运营日志/汇报材料/`

2. **系统迁移**: wiki → knowledge 目录重构
   - 823 个文件迁移
   - Git 初始化

3. **技能更新**: cron 任务提示词批量更新

## Integration with Chronicle Agent

The conversation mining stage is similar to Chronicle Agent but:
- **Scope**: 24 hours (vs 2 hours for Chronicle)
- **Output**: Nightly digest section (vs standalone log file)
- **Focus**: Crystallizable knowledge (vs chronological log)

## References

- `chronicle-agent` skill for session extraction patterns
- `sqlite-message-extraction.md` for SQLite query patterns
- `directory-structure-migration.md` for path mappings