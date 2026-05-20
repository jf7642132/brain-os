---
title: Cross-Source Patterns Library
created: 2026-05-20
updated: 2026-05-20
type: reference
---
# Cross-Source Patterns Library

Validated patterns for merging article-derived and conversation-derived signals.

---

## Pattern 1: 战略→执行衔接 (Strategy → Execution Transition)

**Trigger**: User shifts from strategic planning to execution ("如何落地", "怎么开始做") + existing strategy documents found

**Signal chain**:
```
对话: 执行需求 → 知识库: 战略文档 → 工具: Kanban → 输出: 任务图
```

**Steps**:
1. Search for strategy docs (tags: `strategy`, `project`)
2. Extract priorities and implementation plans from strategy
3. Use Kanban to decompose strategy into executable tasks
4. Create "strategy → task" mapping
5. Output: executable task map + strategy alignment notes

**Example**: 外贸数字化看板规划 → 四大板块 + T0-T9 任务图草案

**Validation**: 2026-05-19 — Brain OS 项目完成，全链路集成测试通过

---

## Pattern 2: 系统故障→技能沉淀 (System Bug → Skill)

**Trigger**: System-level bug fix completed

**Steps**:
1. Document problem symptoms + root cause
2. Document fix + verification steps
3. Create skill file with "故障特征" and "修复命令"
4. Update related docs' "Known Issues" section

**Example**: `_pipe_stdin` 死锁修复 → `hermes-agent-pipe-fix` 技能

**Validation**: 2026-05-19 — 3个技能修复（cron-kanban-integration、telegram-channel-troubleshooting、observer）

---

## Pattern 3: 结构重构→路径适配 (Structure Refactor → Path Adaptation)

**Trigger**: Directory structure major change (e.g., wiki → knowledge migration)

**Signal chain**:
```
系统维护: 目录重构 → 技能路径失效 → Cron 任务路径更新 → 验证完整性
```

**Steps**:
1. Identify all skills referencing old paths
2. Batch update skill SKILL.md files
3. Update cron task templates
4. Verify with grep for orphaned references
5. Test cron execution to catch silent failures

**Example**: wiki → knowledge migration (823 files) → path updates across skills and cron

---

## Pattern 4: 连锁反应模式 (Chain Reaction Pattern)

**Trigger**: Single fix triggers multiple downstream changes

**Signal chain**:
```
bug 修复 → 发现路径不一致 → 触发目录迁移 → 触发 cron 更新 → 触发技能更新
```

**Steps**:
1. Document the initial trigger
2. Track all downstream effects
3. Create "变更影响评估" checklist for future fixes
4. Update skills with chain reaction awareness

**Example**: `_pipe_stdin` fix → path discovery → wiki → knowledge migration

---

## Pattern 5: 技能路径漂移检测 (Skill Path Drift Detection)

**Trigger**: Multiple skills in same time period show similar path/config errors

**Signal chain**:
```
技能A路径错误 → 技能B路径错误 → 技能C路径错误 → 系统性问题识别
```

**Steps**:
1. Collect error reports from multiple skills
2. Identify common pattern (e.g., all reference wrong path prefix)
3. Document as systemic issue, not isolated bugs
4. Create health check mechanism to prevent recurrence

**Example**: 2026-05-19 — 3个技能（cron-kanban-integration、telegram-channel-troubleshooting、observer）均存在路径/配置错误

**Detection heuristics**:
- ≥2 skills with similar error type in same day → systemic issue
- Path errors involving `03-知识库` → migration incomplete
- Config errors involving `TODO_PATH` or channel IDs → environment drift

---

## Pattern 6: 管道健康度交叉验证 (Pipeline Health Cross-Validation)

**Trigger**: One pipeline component shows normal operation while dependent component shows failure

**Signal chain**:
```
上游正常 (数据生成) → 下游停滞 (数据整合) → 识别断点 → 修复触发机制
```

**Steps**:
1. Verify upstream pipeline health (e.g., TradeRisk预警生成正常)
2. Check downstream pipeline status (e.g., 文章整合停滞)
3. Identify break point (e.g., 整合触发条件、标签缺失)
4. Document as pipeline health issue, not data quality issue

**Example**: 2026-05-19 — TradeRisk预警生成正常，但外贸风险预警日报积压30+天未整合

**Detection heuristics**:
- Upstream cron runs successfully + downstream has stale data → trigger mechanism failure
- Data present but not indexed → labeling/tagging issue
- Multiple days of same data type unprocessed → pipeline break

---

## Pattern 7: 跨日状态追踪 (Cross-Day State Tracking)

**Trigger**: Need to track project/state evolution across multiple days

**Signal chain**:
```
Day N: 状态A → Day N+1: 状态B → 识别转变 → 更新知识图谱
```

**Steps**:
1. Read past 1-2 days' digests for context
2. Track project state transitions (in_progress → completed, open → resolved)
3. Identify infrastructure health trends (告警数量变化)
4. Update topic maps and open questions accordingly

**Example**: Brain OS 项目从 "测试中" → "完成" (跨日追踪)

**Use cases**:
- Project completion detection
- Infrastructure health trend analysis
- Work rhythm pattern detection

---

## Usage

When performing cross-source amplification:

1. Check if current signals match any pattern above
2. If match found, follow the pattern's steps
3. Document new pattern instances in the amplifier report
4. If new pattern emerges, propose addition to this library

**Pattern validation**: Each pattern should be validated by ≥2 independent occurrences before being considered "validated".