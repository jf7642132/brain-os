# Brain OS Architecture — Skill System on Hermes Agent

## Overview

**Brain OS is a skill system inspired by OpenClaw's git-backed brain design.** It is NOT an independent system, but a composable collection of skills built on top of Hermes Agent's cron scheduler and skill system.

| Layer | Official Hermes Feature | Brain OS Customization |
|-------|------------------------|------------------------|
| Infrastructure | Gateway, Cron, Skills, Memory | Multi-instance setup (main + dingtalk-worker) |
| Nightly Pipeline | Cron scheduling | 3-stage knowledge pipeline (02:00→03:00→04:00) |
| Personal Ops | Cron + Skills | Daily brief, weekly plan, monthly summary, reminders |
| System Ops | Cron + Observer skill | Chronicle (史官), auto-commit, lint/audit |

**Inspiration**: [OpenClaw](https://github.com/openclaw/openclaw) — git-backed brain design where agent knowledge, memory, and config are stored in a git repository, synced on startup, and auto-committed nightly.

## Architecture Layers

```
Layer 1: 基础设施层 (Hermes Agent 原生)
├── Gateway (消息通道：微信/钉钉/Telegram)
├── Cron Scheduler (定时任务调度)
├── Skills System (技能系统)
└── Memory System (持久记忆)

Layer 2: 夜间知识流水线 (Nightly Pipeline)
├── 02:00 文章整合 → 提取核心要点，建立交叉引用
├── 03:00 对话挖掘 → 从对话中提取可沉淀知识
└── 04:00 知识放大器 → 跨源主题关联，发现弱信号，合成新洞察

Layer 3: 个人运营层 (Personal Ops)
├── 07:00 每日早报 → 待办列表 + 优先级建议
├── 15:00 待办提醒 → 高优先级事项提醒
├── 20:30 晚间待办提醒 → 未完成事项收尾
├── 06:00 每周计划 → 回顾上周 + 规划本周
└── 09:00 月度总结 → 回顾本月 + 沉淀模式 + 规划下月

Layer 4: 系统运维层 (System Ops)
├── 每 2h 史官记录 → 扫描聊天记录，提取实质性内容
├── 整点 自动提交巡检 → 检查 git 状态，自动提交
├── 00:30 每日观察者自检 → AI 团队健康监控
├── 01:00 周一知识库 Lint → 自动化格式/断链检查
└── 01:30 周一知识库审计 → LLM 人工深度审计
```

## Critical Architecture Gap: No Consumption Layer

**Problem**: All pipeline outputs are archived but never consumed.

| Output | Where It Goes | Who Consumes It? |
|--------|---------------|------------------|
| Nightly pipeline (文章/对话/知识) | `04-知识库/` | ❌ No one |
| Chronicle records (史官) | `03-个人运营/05-频道历史/` (149 files) | ❌ No one |
| Observer self-check | `03-个人运营/observer/` | ❌ No one |
| Monthly summary | `03-个人运营/04-回顾反思/` | ❌ No one (empty directory) |
| Weekly plan | `03-个人运营/02-计划日程/` | ❌ No one |

**Impact**: The system produces knowledge but has no mechanism to feed it back into daily operations.

## Recommended Solution: Consumption Layer

Add a **daily consumption step** to the morning brief (每日早报):

1. **Read nightly pipeline outputs** from previous night
   - `04-知识库/01-阅读消化/` — 文章整合结果
   - `04-知识库/02-工作整理/` — 对话挖掘结果
   - `04-知识库/03-整合报告/` — 知识放大器洞察

2. **Read Chronicle records** from today's window
   - `03-个人运营/05-频道历史/YYYY-MM-DD-*.md`
   - Extract decisions, pending items, technical discussions

3. **Read Observer suggestions**
   - `03-个人运营/observer/observer-YYYY-MM-DD.md`
   - Extract system health recommendations

4. **Integrate into daily brief**:
   - "昨日夜间流水线产出：X 个新洞察"
   - "史官记录中的待办事项：Y 项"
   - "观察者建议：Z 项系统改进"

This closes the loop: **produce → archive → consume → act**.

## Official vs Custom

| Resource | Official Link | Status |
|----------|---------------|--------|
| Hermes Agent | https://hermes-agent.nousresearch.com/ | ✅ Official |
| Cron docs | https://hermes-agent.nousresearch.com/docs/user-guide/features/cron | ✅ Official |
| Brain OS | ❌ No official link | Custom skill system |

## Key Files

| File | Purpose |
|------|---------|
| `~/.hermes/cron/jobs.json` | All cron task definitions |
| `~/.hermes/knowledge/03-个人运营/03-待办跟进/todo-backlog.md` | Central todo list |
| `~/.hermes/knowledge/03-个人运营/05-频道历史/` | Chronicle records (149 files) |
| `~/.hermes/knowledge/05-系统配置/提示词/cron/` | Cron task prompts |
| `~/.hermes/scripts/kanban-sync.py` | Generic Kanban integration |
| `~/.hermes/scripts/lint-to-kanban.py` | Lint-specific Kanban integration |

## Related Skills

- `brain-os` — Brain OS skill system documentation
- `cron-kanban-integration` — Kanban integration for cron tasks
- `llm-wiki` — Knowledge base management
- `observer` — AI team health monitoring

---

*Last updated: 2026-05-19 — Updated positioning: skill system (not independent system), OpenClaw inspiration.*