# Brain OS

> 一套基于 OpenClaw git-backed brain 设计、结合 Hermes Kanban 任务调度的技能体系

## 这是什么

Brain OS **不是独立系统**，而是一套**可组合的技能集合**，灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计。

**核心创新**：将 Hermes 的 **Kanban 任务调度** 作为大脑中枢，通过 **生产者-消费者架构** 实现知识的自动生产、管理和进化。

## 设计理念

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Brain OS 生产者-消费者架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                      ┌─────────────────────────┐                            │
│                      │    Kanban 任务调度       │                            │
│                      │    (Hermes 核心)         │                            │
│                      │                         │                            │
│                      │  ┌───────────────────┐  │                            │
│                      │  │  同步脚本          │  │                            │
│                      │  │  kanban-sync.py    │  │                            │
│                      │  │  管理和进化任务流   │  │                            │
│                      │  └─────────┬─────────┘  │                            │
│                      └────────────┼────────────┘                            │
│                                   │                                         │
│              ┌────────────────────┼────────────────────┐                   │
│              │                    │                    │                   │
│              ▼                    ▼                    ▼                   │
│     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐          │
│     │   生产者       │   │   生产者       │   │   生产者       │          │
│     │   (8 个)       │   │                │   │                │          │
│     │                │   │                │   │                │          │
│     │ • 史官记录     │   │ • 观察者自检   │   │ • 知识库审计   │          │
│     │ • 夜间流水线   │   │ • 自动提交巡检 │   │ • 夜间文章抓取 │          │
│     │ • 对话知识挖掘 │   │                │   │                │          │
│     └───────┬────────┘   └───────┬────────┘   └───────┬────────┘          │
│             │                    │                    │                   │
│             └────────────────────┼────────────────────┘                   │
│                                  ▼                                         │
│                      ┌─────────────────────────┐                           │
│                      │    知识存储层           │                           │
│                      │    knowledge/           │                           │
│                      │                         │                           │
│                      │  Layer 0: 原始数据      │                           │
│                      │  Layer 1: 实体提取      │                           │
│                      │  Layer 2: 概念体系      │                           │
│                      │  Layer 3: 上下文管理    │                           │
│                      └───────────┬─────────────┘                           │
│                                  │                                         │
│              ┌────────────────────┼────────────────────┐                   │
│              │                    │                    │                   │
│              ▼                    ▼                    ▼                   │
│     ┌────────────────┐   ┌────────────────┐   ┌────────────────┐          │
│     │   消费者       │   │   消费者       │   │   消费者       │          │
│     │   (5 个)       │   │                │   │                │          │
│     │                │   │                │   │                │          │
│     │ • 知识检索     │   │ • 任务执行     │   │ • 决策支持     │          │
│     │ • 技能调用     │   │ • 上下文管理   │   │                │          │
│     └────────────────┘   └────────────────┘   └────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. Kanban 任务调度（大脑中枢）

Kanban 是 Brain OS 的**调度中心**，所有知识操作都是 kanban 上的可追踪任务：

| 任务 | 触发时间 | 作用 |
|------|----------|------|
| `article-notes-integration` | 02:00 | 文章整合 |
| `conversation-knowledge-flywheel` | 03:00 | 对话知识挖掘 |
| `knowledge-flywheel-amplifier` | 04:00 | 知识聚合 |
| `daily-observer` | 09:00 | Agent 自检，发现错误并记录经验 |

### 2. 同步脚本（kanban-sync.py）

同步脚本是 **Kanban 与知识存储之间的桥梁**，负责：

- **读取 kanban 任务状态** — 从 `todo-backlog.md` 解析待办事项
- **执行知识同步** — 将生产者的输出写入 knowledge 目录
- **更新任务状态** — 同步完成后标记 kanban 任务为"已完成"

```bash
# 预览变更
python kanban-sync.py --dry-run

# 同步并提交
python kanban-sync.py --commit
```

### 3. 生产者（8 个）

| 生产者 | 输出 | 存储位置 |
|--------|------|----------|
| 史官记录 (chronicle-agent) | 对话归档 | `knowledge/00-raw/transcripts/` |
| 观察者自检 (observer) | 错误记录/经验 | `knowledge/05-summaries/` |
| 知识库审计 | 知识质量报告 | `knowledge/05-summaries/` |
| 自动提交巡检 | Git 状态报告 | `knowledge/05-summaries/` |
| 夜间流水线 | 整合后的知识 | `knowledge/04-queries/` |
| 夜间文章抓取 (article-notes-integration) | 外部文章笔记 | `knowledge/00-raw/articles/` |
| 对话知识挖掘 (conversation-knowledge-flywheel) | 可复用模式 | `knowledge/03-comparisons/` |
| 跨源知识聚合 (knowledge-flywheel-amplifier) | 统一知识图谱 | `knowledge/04-queries/` |

### 4. 消费者（5 个）

| 消费者 | 输入 | 作用 |
|--------|------|------|
| 知识检索 | `knowledge/04-queries/` | 快速检索知识 |
| 任务执行 | `knowledge/06-context/todo-tracking/` | 执行待办任务 |
| 决策支持 | `knowledge/02-concepts/` | 基于知识做决策 |
| 技能调用 | `knowledge/07-skills/` | 调用自定义技能 |
| 上下文管理 | `knowledge/06-context/` | 管理对话上下文 |

## 运行逻辑

### 夜间批处理流程

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

### 实时交互流程

```
用户提问 ──► Agent 接收
              │
              ▼
        消费者检索知识 (knowledge/04-queries/)
              │
              ▼
        基于知识生成回答
              │
              ▼
        史官记录对话 (knowledge/00-raw/transcripts/)
              │
              ▼
        夜间批处理时自动挖掘和聚合
```

## 目录结构

### knowledge/ 目录规范

```
knowledge/
├── 00-raw/                    # Layer 0: 原始数据
│   ├── transcripts/           # 对话原始记录
│   └── articles/              # 外部文章笔记
│
├── 01-entities/               # Layer 1: 实体提取
│   ├── people/                # 人物信息
│   ├── companies/             # 公司信息
│   └── projects/              # 项目信息
│
├── 02-concepts/               # Layer 2: 概念体系
│   ├── ai-ops/                # AI 运维概念
│   ├── personal-ops/          # 个人运营概念
│   └── <your-domain>/         # 自定义领域
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
└── 09-personal-ops/           # 个人运营（不公开）
```

## 技能清单

Brain OS 依赖以下 Hermes 内置技能（无需额外安装）：

| 技能 | 定位 | 触发方式 |
|------|------|----------|
| `chronicle-agent` | 对话记录归档 | 夜间定时 |
| `observer` | Agent 自检 | 每次任务完成后 |
| `llm-wiki` | 知识结构化 | 手动/定时 |
| `article-notes-integration` | 外部文章整合 | 夜间定时 (02:00) |
| `conversation-knowledge-flywheel` | 对话模式挖掘 | 夜间定时 (03:00) |
| `knowledge-flywheel-amplifier` | 跨源知识聚合 | 夜间定时 (04:00) |

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_TODO_PATH` | 待办追踪路径 | `$HERMES_KNOWLEDGE/06-context/todo-tracking/todo-backlog.md` |
| `BRAINO_GIT_REPO` | Git 仓库路径 | `$HERMES_ROOT/brain-os` |

### 导入定时任务

```bash
# 复制任务模板
cp ~/.hermes/skills/brain-os/templates/jobs-template.json ~/.hermes/brain-os-jobs.json

# 编辑配置（根据需要调整 schedule）
vim ~/.hermes/brain-os-jobs.json

# 导入到 hermes cron
hermes cron import ~/.hermes/brain-os-jobs.json

# 查看已导入任务
hermes cron list
```

## 使用

### 同步 kanban 到 git

```bash
# 预览变更
python ~/.hermes/skills/brain-os/references/kanban-sync.py --dry-run

# 同步并提交
python ~/.hermes/skills/brain-os/references/kanban-sync.py --commit
```

### 手动运行技能

```bash
# 文章整合
hermes skills run article-notes-integration

# 对话模式挖掘
hermes skills run conversation-knowledge-flywheel

# Agent 自检
hermes skills run observer
```

### 查看 kanban 状态

```bash
# 列出所有任务
hermes kanban list

# 运行指定任务
hermes kanban run <task-name>

# 查看任务状态
hermes kanban status
```

## 与 OpenClaw 的区别

| 特性 | OpenClaw | Brain OS |
|------|----------|----------|
| Git 存储 | ✅ | ✅ |
| **Kanban 调度** | ❌ | ✅ **核心创新** |
| **生产者-消费者架构** | ❌ | ✅ **核心创新** |
| **同步脚本连接两端** | ❌ | ✅ **核心创新** |
| 夜间批处理 | ❌ | ✅ |

Brain OS 在 OpenClaw 的 git-backed brain 基础上，增加了：

1. **Kanban 作为大脑中枢** — 所有知识操作都是可追踪的任务
2. **生产者-消费者架构** — 明确分工，知识自动生产和消费
3. **同步脚本连接两端** — kanban-sync.py 实现任务状态与知识存储的同步

## 快速安装

```bash
# 克隆技能到技能目录
git clone https://github.com/jf7642132/brain-os.git ~/.hermes/skills/brain-os

# 验证安装
hermes skills list | grep brain-os

# 查看技能详情
hermes skills view brain-os

# 导入定时任务
hermes cron import ~/.hermes/skills/brain-os/templates/jobs-template.json
```

## 架构设计

详见 [references/brain-os-architecture.md](references/brain-os-architecture.md)

## 开源许可

MIT License

## 致谢

灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计。