# Brain OS

> 一套基于 OpenClaw git-backed brain 设计的 Hermes 技能体系，实现 Agent 的 git 驱动知识管理。

## 这是什么

Brain OS **不是独立系统**，而是一套**可组合的技能集合**，灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计。

核心思想：**Agent 的知识库、记忆、配置全部存储在 git 仓库中**，版本可控、可回溯、多 Agent 共享。

## 运行逻辑

Brain OS 的工作流由 7 个 Hermes 内置技能协同完成，形成一个**数据闭环**：

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Brain OS 运行逻辑                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐                                                     │
│  │   用户对话   │ ← 你在 Telegram/微信/Discord 等渠道与 Agent 对话      │
│  └──────┬──────┘                                                     │
│         │                                                            │
│         ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  1. chronicle-agent (对话归档)                               │    │
│  │     作用：将对话记录归档到 knowledge/00-raw/transcripts/      │    │
│  │     触发：夜间定时任务                                       │    │
│  └────────────────────────┬────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  2. conversation-knowledge-flywheel (模式挖掘)               │    │
│  │     作用：从对话中提取可复用的模式、技巧、经验                 │    │
│  │     输出：knowledge/03-comparisons/、knowledge/05-summaries/ │    │
│  │     触发：夜间定时任务                                       │    │
│  └────────────────────────┬────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  3. knowledge-flywheel-amplifier (跨源聚合)                  │    │
│  │     作用：合并对话、文章、笔记等多源知识                      │    │
│  │     输出：knowledge/04-queries/ 统一知识图谱                  │    │
│  │     触发：夜间定时任务                                       │    │
│  └────────────────────────┬────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  4. llm-wiki (知识结构化)                                    │    │
│  │     作用：将知识组织成可检索的结构化格式                      │    │
│  │     输出：knowledge/02-concepts/ 领域知识体系                 │    │
│  │     触发：手动/定时                                          │    │
│  └────────────────────────┬────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  5. cron-git-state-monitoring (Git 同步)                     │    │
│  │     作用：定时提交知识变更到 git 仓库                         │    │
│  │     输出：Git 仓库（版本历史 + 多 Agent 共享）                │    │
│  │     触发：定时提交（默认每天 6 点）                           │    │
│  └────────────────────────┬────────────────────────────────────┘    │
│                           │                                          │
│                           ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  6. observer (Agent 自检)                                    │    │
│  │     作用：检查 Agent 运行状态，发现错误并记录经验             │    │
│  │     输出：knowledge/05-summaries/ 经验总结                   │    │
│  │     触发：每次任务完成后                                     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  7. article-notes-integration (外部文章整合)                 │    │
│  │     作用：抓取外部文章并整合到知识库                          │    │
│  │     输出：knowledge/04-queries/                              │    │
│  │     触发：夜间定时任务                                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 关键设计

| 设计原则 | 说明 |
|----------|------|
| **Git 驱动** | 所有知识存储在 git 仓库，版本可控，可回溯 |
| **技能可组合** | 每个技能独立，可按需启用/禁用 |
| **夜间批处理** | 知识挖掘、聚合等重任务在夜间执行，不干扰白天使用 |
| **多 Agent 共享** | 同一知识库可被多个 Agent 访问，知识沉淀不丢失 |

## 快速安装

```bash
# 1. 克隆到技能目录
git clone https://github.com/jf7642132/brain-os.git ~/.hermes/skills/brain-os

# 2. 验证安装
hermes skills list | grep brain-os

# 3. 查看安装说明
hermes skills view brain-os

# 4. 导入定时任务
hermes cron import ~/.hermes/skills/brain-os/templates/jobs-template.json

# 5. 查看已导入任务
hermes cron list
```

## 配置

### 环境变量（可选）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_TODO_PATH` | 待办追踪路径 | `$HERMES_KNOWLEDGE/06-context/todo-tracking/todo-backlog.md` |
| `BRAINO_GIT_REPO` | Git 仓库路径 | `$HERMES_ROOT/brain-os` |

### 目录结构规范

```
knowledge/
├── 00-raw/                    # Layer 0: 原始数据
│   └── transcripts/           # 对话原始记录
│
├── 01-entities/               # Layer 1: 实体提取
│   ├── people/                # 人物信息
│   ├── projects/              # 项目信息
│   └── companies/             # 公司信息
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
├── 06-context/                # Layer 3: 上下文
│   └── todo-tracking/         # 待办追踪
│
└── 09-personal-ops/           # 个人运营（可选）
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
# 夜间文章整合
hermes skills run article-notes-integration

# 对话模式挖掘
hermes skills run conversation-knowledge-flywheel

# Agent 自检
hermes skills run observer
```

### 查看知识状态

```bash
# 查看知识库结构
ls -la ~/.hermes/knowledge/

# 查看待办事项
cat ~/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md

# 查看最近提交
cd ~/.hermes/brain-os && git log --oneline -10
```

## 技能清单

Brain OS 依赖以下 Hermes 内置技能（无需额外安装）：

| 技能 | 作用 | 触发方式 |
|------|------|----------|
| `chronicle-agent` | 对话记录归档 | 夜间定时 |
| `observer` | Agent 自检 | 每次任务完成后 |
| `llm-wiki` | 知识结构化 | 手动/定时 |
| `article-notes-integration` | 外部文章整合 | 夜间定时 |
| `conversation-knowledge-flywheel` | 对话模式挖掘 | 夜间定时 |
| `knowledge-flywheel-amplifier` | 跨源知识聚合 | 夜间定时 |
| `cron-git-state-monitoring` | Git 同步 | 定时提交 |

## 架构设计

详见 [references/brain-os-architecture.md](references/brain-os-architecture.md)

## 开源许可

MIT License