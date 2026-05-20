---
name: skill-architecture-docs
description: >
  技能体系架构文档编写规范。Use when: documenting skill systems, designing producer-consumer architectures, defining skill roles, writing architecture docs for skill collections.
tags: [documentation, architecture, skill-design]
related_skills: []
---

# 技能体系架构文档编写规范

## 核心原则

### 1. 生产者 vs 消费者 区分

**生产者（Producer）**：真实可运行的技能，执行写入操作
- 有具体的技能名（如 `chronicle-agent`、`observer`）
- 触发方式明确（定时/手动/事件触发）
- 输出到特定存储位置（如 `knowledge/00-raw/transcripts/`）

**消费者（Consumer）**：不是技能，是 Agent 使用知识的抽象方式
- 描述 Agent 如何从知识存储中读取信息
- 对应的是 Agent 的内置能力（如 `memory`、`session_search`、`todo`）
- 不是独立可运行的技能

**文档编写规则**：
- ✅ 生产者列表：列出真实技能名 + 触发方式 + 输出位置
- ✅ 消费者说明：作为概念分类描述，标注"不是独立技能"
- ❌ 不要将消费者写成技能列表

### 2. 技能定位声明

每个技能体系文档必须明确声明：

```
Brain OS **不是独立系统**，而是一套**可组合的技能集合**。
```

避免用户误以为是独立运行的系统。

### 3. 数据流图规范

```
┌──────────────────────────────────────────────────────────────────────┐
│                         技能体系数据流                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌──────────────────────────────────────────┐   │
│  │   用户对话   │───►│  chronicle-agent (对话归档)              │   │
│  └─────────────┘    │  → 存储到 knowledge/00-raw/transcripts/   │   │
│                     └────────────────┬─────────────────────────┘   │
│                                      │                              │
│                                      ▼                              │
│                     ┌──────────────────────────────────────────┐   │
│                     │  conversation-knowledge-flywheel         │   │
│                     │  (对话模式挖掘)                            │   │
│                     │  → 提取可复用模式 → knowledge/03/         │   │
│                     └────────────────┬─────────────────────────┘   │
│                                      │                              │
│                                      ▼                              │
│                     ┌──────────────────────────────────────────┐   │
│                     │  knowledge-flywheel-amplifier            │   │
│                     │  (跨源知识聚合)                            │   │
│                     │  → 合并文章/对话/笔记 → knowledge/04/     │   │
│                     └──────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 4. 技能清单表格

| 技能 | 定位 | 触发方式 |
|------|------|----------|
| `chronicle-agent` | 对话记录归档 | 夜间定时 |
| `observer` | Agent 自检 | 每次任务完成后 |

**必须包含的列**：
- 技能名（代码格式）
- 定位（一句话说明做什么）
- 触发方式（定时/手动/事件）

### 5. 目录结构规范

```
knowledge/
├── 00-raw/                    # Layer 0: 原始数据
│   └── transcripts/           # 对话原始记录
│
├── 01-entities/               # Layer 1: 实体提取
│   ├── people/                # 人物信息
│   └── companies/             # 公司信息
│
├── 02-concepts/               # Layer 2: 概念体系
│   └── <domain>/              # 自定义领域
│
├── 03-comparisons/            # Layer 2: 对比分析
├── 04-queries/                # Layer 2: 查询模板
├── 05-summaries/              # Layer 2: 总结归档
│
├── 06-context/                # Layer 3: 上下文管理
│   └── todo-tracking/         # 待办跟踪
│
├── 07-skills/                 # Layer 3: 技能库
│   └── <skill-name>/          # 自定义技能
│
├── 08-references/             # Layer 3: 参考资料
│
└── 09-personal-ops/           # 个人运营（个人数据，gitignore 排除）
```

### 6. 夜间批处理流程

```
23:00 ──► 用户结束当日对话
              │
              ▼
02:00 ──► article-notes-integration 抓取文章
              │
              ▼
03:00 ──► conversation-knowledge-flywheel 挖掘模式
              │
              ▼
04:00 ──► knowledge-flywheel-amplifier 聚合知识
              │
              ▼
06:00 ──► kanban-sync.py 同步到 kanban
              │
              ▼
09:00 ──► observer 自检，检查夜间流水线状态
```

## 常见错误

| 错误 | 正确做法 |
|------|----------|
| 将消费者写成技能列表 | 消费者是概念分类，不是独立技能（除非是 Brain OS 的 3 个消费者任务） |
| 技能名与实际不符 | 使用真实的技能名（如 `article-notes-integration` 而非 `nightly-article-integration`） |
| 时间与实际 cron 不符 | 核对实际 cron 配置时间 |
| 未声明定位 | 明确声明"不是独立系统，是可组合技能集合" |
| 遗漏 PII 排除说明 | 个人数据目录需标注 gitignore 排除 |
| **Kanban 被描述为"大脑中枢"** | Kanban 是可视化界面，**todo-backlog.md 才是统一任务入口** |
| **概念未验证就声称灵感来源** | 核实术语是否官方（如 OpenClaw 没有 "git-backed brain" 官方术语） |
| **目录命名冲突** | 避免同名目录在不同层级出现（如 `personal-ops/` 在 02-concepts 和 09- 同时存在） |

## Brain OS 特定规范

### 统一任务入口

Brain OS 的核心枢纽是 **`todo-backlog.md`**，不是 Kanban：

- **生产者写入** todo-backlog.md
- **消费者读取** todo-backlog.md
- **Kanban 双向同步** todo-backlog.md（可视化界面，非调度中心）

架构图应体现：
```
生产者（8 个）──→ todo-backlog.md ──→ 消费者（3 个）
                     ↓
              Kanban 双向同步
```

### 消费者定义

Brain OS 的消费者是 **3 个真实任务**（不是抽象概念）：

| 消费者 | 输入 | 作用 |
|--------|------|------|
| 每日早报 | `todo-backlog.md`（高优先级） | 生成今日待办简报 |
| 每周计划 | `todo-backlog.md`（中优先级） | 生成周计划 |
| 月度总结 | `todo-backlog.md`（低优先级） | 生成月报 |

### 概念验证原则

在文档中声称"灵感来源于 X 项目"时：

1. **核实术语是否官方** — 搜索官方文档、GitHub、Issue 确认术语存在
2. **使用准确描述** — 如 OpenClaw 的"git 驱动持久化设计"而非"git-backed brain"
3. **注明来源** — 如是社区实现，明确标注"社区/第三方实现"

## 检查清单

文档完成后检查：

- [ ] 技能名与实际技能一致
- [ ] 生产者/消费者区分清晰
- [ ] 触发时间与实际 cron 配置一致
- [ ] 定位声明明确（非独立系统）
- [ ] 目录结构规范完整
- [ ] 夜间流程时间合理
- [ ] 个人数据排除说明
- [ ] **todo-backlog.md 是统一入口（非 Kanban）**
- [ ] **概念术语已验证（非臆造）**
- [ ] **目录命名无冲突**