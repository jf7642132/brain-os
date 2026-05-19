# Brain OS

> 一套基于 OpenClaw git-backed brain 设计、结合 Hermes Kanban 调度的技能体系

## 这是什么

Brain OS **不是独立系统**，而是一套**可组合的技能集合**，灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计。

**核心创新**：在 OpenClaw 的 git-backed brain 基础上，**结合 Hermes Kanban 任务调度**，实现：
- **任务驱动的知识管理** — 每个知识操作都是 kanban 上的可追踪任务
- **自动化工作流** — 夜间自动执行知识挖掘、聚合、同步
- **版本可控** — 所有知识变更通过 git 提交，可回溯
- **多 Agent 共享** — 同一知识库可被多个 Agent 访问

## 运行逻辑

Brain OS 的核心是 **Kanban 任务调度 + Git 知识存储** 的双轮驱动：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Brain OS 运行逻辑                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    Kanban 任务调度层 (Hermes)                      │      │
│  │                                                                    │      │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │      │
│  │  │ 夜间归档     │  │ 模式挖掘     │  │ 知识聚合     │               │      │
│  │  │ cron: 0 3 * │  │ cron: 0 4 * │  │ cron: 0 5 * │               │      │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │      │
│  │         │                │                │                        │      │
│  │         └────────────────┼────────────────┘                        │      │
│  │                          ▼                                         │      │
│  │              ┌─────────────────────┐                               │      │
│  │              │  cron-git-state     │                               │      │
│  │              │  定时 Git 同步       │                               │      │
│  │              │  cron: 0 6 * * *    │                               │      │
│  │              └──────────┬──────────┘                               │      │
│  └─────────────────────────┼──────────────────────────────────────────┘      │
│                            │                                                  │
│                            ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                    Git 知识存储层 (Brain OS)                       │      │
│  │                                                                    │      │
│  │  knowledge/                                                        │      │
│  │  ├── 00-raw/transcripts/   ← chronicle-agent 对话归档             │      │
│  │  ├── 01-entities/          ← 人物/项目/公司实体提取               │      │
│  │  ├── 02-concepts/          ← llm-wiki 知识结构化                  │      │
│  │  ├── 03-comparisons/       ← 对比分析                             │      │
│  │  ├── 04-queries/           ← 知识图谱/查询模板                    │      │
│  │  ├── 05-summaries/         ← 总结归档                             │      │
│  │  └── 06-context/           ← 上下文/待办追踪                      │      │
│  │                                                                    │      │
│  │  Git 仓库 ← cron-git-state-monitoring 定时提交                    │      │
│  └──────────────────────────────────────────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 详细流程

#### 1. 对话发生（实时）

```
用户 ──► Agent (Hermes) ──► 对话记录
                              │
                              ▼
                    hermes 自动记录到会话历史
```

#### 2. 夜间归档（cron: 0 3 * * *）

```
chronicle-agent 触发
    │
    ▼
读取最近 24 小时对话
    │
    ▼
归档到 knowledge/00-raw/transcripts/YYYY-MM-DD.md
    │
    ▼
标记 kanban 任务为 "已完成"
```

#### 3. 模式挖掘（cron: 0 4 * * *）

```
conversation-knowledge-flywheel 触发
    │
    ▼
分析归档的对话
    │
    ├── 提取可复用模式 → knowledge/03-comparisons/
    ├── 提取经验技巧 → knowledge/05-summaries/
    └── 提取待办事项 → knowledge/06-context/todo-tracking/
```

#### 4. 知识聚合（cron: 0 5 * * *）

```
knowledge-flywheel-amplifier 触发
    │
    ▼
合并多源知识：
    ├── 对话挖掘的模式
    ├── 外部文章整合 (article-notes-integration)
    └── 已有知识图谱
    │
    ▼
输出统一知识图谱 → knowledge/04-queries/
```

#### 5. Git 同步（cron: 0 6 * * *）

```
cron-git-state-monitoring 触发
    │
    ▼
检查 knowledge/ 变更
    │
    ▼
git add + commit + push
    │
    ▼
版本历史更新，多 Agent 可拉取最新知识
```

#### 6. Agent 自检（cron: 0 9 * * *）

```
observer 触发
    │
    ▼
检查 Agent 运行状态
    │
    ├── 发现错误 → 记录到 knowledge/05-summaries/errors/
    ├── 总结经验 → 更新技能文档
    └── 报告状态 → 发送通知
```

## 核心设计

### 1. Kanban 任务驱动

Brain OS 的所有知识操作都是 **kanban 上的任务**：

```bash
# 查看 Brain OS 相关任务
hermes kanban list --filter "brain-os"

# 手动触发某个任务
hermes kanban run nightly-article-integration

# 查看任务状态
hermes kanban status
```

**优势**：
- 每个操作可追踪、可回溯
- 失败任务可重试
- 任务状态可视化

### 2. Git 驱动的知识存储

所有知识存储在 git 仓库中：

```bash
# 查看知识变更历史
cd ~/.hermes/brain-os && git log --oneline

# 回滚到某个版本
git checkout <commit-hash>

# 多 Agent 共享
git pull  # 拉取其他 Agent 的知识更新
```

**优势**：
- 版本可控，可回溯
- 多 Agent 共享同一知识库
- 变更有完整审计日志

### 3. 技能可组合

Brain OS 依赖的 7 个技能均为 Hermes 内置，可独立使用：

| 技能 | 作用 | 是否必需 |
|------|------|----------|
| `chronicle-agent` | 对话归档 | ✅ 必需 |
| `conversation-knowledge-flywheel` | 模式挖掘 | ✅ 必需 |
| `knowledge-flywheel-amplifier` | 跨源聚合 | ✅ 必需 |
| `llm-wiki` | 知识结构化 | ✅ 必需 |
| `cron-git-state-monitoring` | Git 同步 | ✅ 必需 |
| `article-notes-integration` | 文章整合 | 可选 |
| `observer` | Agent 自检 | 可选 |

## 快速安装

```bash
# 1. 克隆技能到本地
git clone https://github.com/jf7642132/brain-os.git ~/.hermes/skills/brain-os

# 2. 验证安装
hermes skills list | grep brain-os

# 3. 查看安装说明
hermes skills view brain-os

# 4. 导入定时任务（配置 kanban 调度）
hermes cron import ~/.hermes/skills/brain-os/templates/jobs-template.json

# 5. 查看已导入任务
hermes cron list

# 6. 手动测试
hermes cron run nightly-article-integration
```

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_TODO_PATH` | 待办追踪路径 | `$HERMES_KNOWLEDGE/06-context/todo-tracking/todo-backlog.md` |
| `BRAINO_GIT_REPO` | Git 仓库路径 | `$HERMES_ROOT/brain-os` |

### Kanban 任务配置

编辑 `templates/jobs-template.json` 后导入：

```bash
# 复制模板
cp ~/.hermes/skills/brain-os/templates/jobs-template.json ~/.hermes/brain-os-jobs.json

# 编辑配置（调整 schedule 或 command）
vim ~/.hermes/brain-os-jobs.json

# 导入
hermes cron import ~/.hermes/brain-os-jobs.json
```

## 目录结构

```
brain-os/
├── SKILL.md                          # 技能主文档
├── references/
│   ├── kanban-sync.py                # Kanban-Git 同步工具
│   └── brain-os-architecture.md      # 详细架构设计
├── templates/
│   └── jobs-template.json            # Kanban 任务配置模板
├── scripts/
│   └── deploy.sh                     # 部署脚本
├── LICENSE                           # MIT
├── .gitignore                        # Git 忽略规则
└── README.md                         # 本文件
```

## 与 OpenClaw 的区别

| 特性 | OpenClaw | Brain OS |
|------|----------|----------|
| 设计灵感 | - | ✅ OpenClaw git-backed brain |
| Git 存储 | ✅ | ✅ |
| Kanban 调度 | ❌ | ✅ **核心创新** |
| 夜间批处理 | ❌ | ✅ |
| 技能可组合 | 部分 | ✅ 全部 Hermes 内置 |
| 多 Agent 共享 | ✅ | ✅ |

**总结**：Brain OS 在 OpenClaw 的 git-backed brain 基础上，**增加了 Hermes Kanban 任务调度层**，使知识管理从"被动存储"变为"主动调度"。

## 开源许可

MIT License