# 每日简报（驾驶舱）生成模式

## 触发条件

- 每日 07:00 cron 任务（消费者任务 `a750c4eb` 每日早报）
- 用户手动请求生成今日简报

## 数据来源（多源聚合）

| 数据源 | 路径 | 用途 |
|--------|------|------|
| 待办列表 | `06-context/todo-tracking/todo-backlog.md` | 活跃待办、阻塞项、优先级排序 |
| Git 提交历史 | `git log --since=昨天 00:00 --until=今天 00:00` | 昨日完成工作、commit 内容 |
| 夜间摘要 | `04-queries/daily/nightly-digest-YYYY-MM-DD.md` | 管道任务状态、弱信号、文章断流等 |
| Lint 报告 | `99-system/lint-reports/lint-report-YYYY-MM-DD.md` | 知识库健康度、断链、frontmatter |
| 昨日简报 | `09-personal-ops/01-daily-brief/YYYY-MM-DD.md` | 昨日状态基准、未完成项延续 |
| 集成报告 | `99-system/integration-reports/YYYY-MM-DD/` | 各管道任务执行结果 |

## 生成步骤

### Step 1: 读取待办列表（强化）

```
1. 读取完整 todo-backlog.md
2. 按优先级排序：阻塞 > 高 > 中 > 低
3. 筛选今日需跟进项（状态：待执行/待确认/进行中）
4. 识别阻塞项，优先提醒
5. 在日报中明确标注待办来源和 Kanban 卡片 ID
6. 如发现待办已解决但未更新状态 → 记录为脏数据
```

### Step 2: 获取昨日完成工作

```bash
git log --oneline --since="昨天 00:00" --until="今天 00:00" --all
```

- 按功能分组（P0 修复、P1 修复、P2 修复、自动提交、测试等）
- 关联 commit hash 到具体任务
- 区分"人工决策"和"自动执行"

### Step 3: 读取夜间摘要和 Lint 报告

- 检查管道任务状态（文章断流天数、对话挖掘结果数）
- 检查弱信号（文章断流、纯工程日、消费层缺位）
- 检查知识库健康度（frontmatter、断链、大页面）

### Step 4: 生成优先级建议

| 优先级 | 标准 |
|--------|------|
| P0 | 阻塞项、需今日决策、影响系统运行 |
| P1 | 今日应处理、高影响 |
| P2 | 本周处理、中影响 |
| P3 | 待办、低影响 |

### Step 5: 系统健康度汇总

| 指标 | 检查方式 |
|------|----------|
| Gateway | 是否正常启动、有无重启记录 |
| 知识库 | Lint 报告结果 |
| 各通道 | 钉钉/Telegram 错误计数 |
| 技能绑定 | 当前绑定率 |
| 文章管道 | 断流天数 |
| 夜间流水线 | 自动提交次数 |

### Step 6: 写入并 git 提交

```
输出路径: 09-personal-ops/01-daily-brief/YYYY-MM-DD.md
提交信息: auto: 驾驶舱简报 YYYY-MM-DD - 待办概览 + 昨日工作 + 优先级建议
```

## 输出模板

```markdown
---
title: YYYY MM DD
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: note
tags: [09-personal-ops, 01-daily-brief]
---

# 驾驶舱简报 | YYYY-MM-DD (周X)

> **生成时间**: HH:MM | **来源**: todo-backlog.md + git 记录 + nightly digest

---

## 📊 待办概览
| 优先级 | Open | In Progress | Resolved | 总计 |

## 🚨 今日优先跟进
### P0 - 阻塞项
### P1 - 高优先级
### P2 - 中优先级

## ✅ 昨日完成工作
| ID | 完成内容 | 处理方式 | Git Commit |

## 📋 今日优先级建议

## 🧹 待办清理建议

## 📈 系统健康度

## 📌 数据来源
```

## Pitfalls

### 1. 自动提取的待办描述被截断

**问题**：夜间知识放大器等生产者任务自动提取的待办项，描述字段可能被截断（如 M001、M002 的描述在 todo-backlog.md 中不完整）。

**症状**：日报中待办描述以"未进"、"预计完成时间"等截断文本出现。

**修复**：
1. 在生成日报前，检查待办描述是否完整
2. 如不完整，标注为"⚠️ 描述被截断，需核实"
3. 反馈给生产者任务 prompt，要求完整描述

### 2. 多源数据时间不一致

**问题**：不同数据源的"昨天"定义可能不同（git log 按提交时间、nightly digest 按运行时间、lint 报告按生成时间）。

**修复**：统一使用 `TZ="Asia/Shanghai" date` 获取标准时间，所有数据源以此为准。

### 3. 脏数据检测遗漏

**问题**：待办已解决但状态未更新为 `resolved`，导致日报中显示为 open。

**检测**：
```bash
# 对比 Kanban 状态和 todo 状态
hermes kanban list --status resolved | grep -o '`t_[a-f0-9]*`' | sort
grep "resolved" todo-backlog.md | grep -o '`t_[a-f0-9]*`' | sort
# 差异即为脏数据
```

### 4. 昨日简报不存在

**问题**：第一天运行或简报丢失时，无法对比昨日状态。

**修复**：如昨日简报不存在，从 git log 和 nightly digest 中重建昨日工作摘要。

## 相关技能

- `brain-os` — 核心架构和数据流
- `brain-os-project-management` — 项目管理规范
- `daily-timesheet` — 工时统计（不同用途）
- `cron-kanban-integration` — cron 与 Kanban 集成
