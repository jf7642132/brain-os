# Brain OS

> 一套基于 OpenClaw 设计灵感的 Hermes 技能体系，实现 Agent 的 git-backed brain 工作流。

## 核心理念

灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 **git-backed brain** 设计：
- Agent 的知识库、记忆、配置全部存储在 git 仓库中
- 每次启动自动同步仓库状态
- 夜间自动提交变更，保持版本历史
- 多 Agent 协作时共享同一知识库

## 技能体系

Brain OS 不是独立系统，而是一套**可组合的技能集合**，所有技能均为 Hermes 官方内置：

| 技能 | 作用 |
|------|------|
| `chronicle-agent` | 对话记录归档，构建知识时间线 |
| `observer` | Agent 自检，发现错误并记录经验 |
| `llm-wiki` | LLM 知识库，结构化知识管理 |
| `article-notes-integration` | 外部文章抓取与知识整合 |
| `conversation-knowledge-flywheel` | 对话知识挖掘，提取可复用模式 |
| `knowledge-flywheel-amplifier` | 跨源知识聚合，构建统一知识图谱 |
| `cron-git-state-monitoring` | 定时 git 提交，保持仓库同步 |

## 快速安装

### 方式一：直接克隆（推荐）

```bash
# 克隆技能仓库到本地
git clone https://github.com/<your-org>/brain-os.git ~/.hermes/brain-os

# 让 hermes 识别技能（需配置技能路径）
hermes config set skills.paths+=~/.hermes/brain-os/skills
```

### 方式二：环境变量自动加载

```bash
# 设置环境变量
export HERMES_SKILLS_PATH=~/.hermes/brain-os/skills

# hermes 启动时自动加载
hermes
```

### 方式三：手动安装单个技能

```bash
# 从仓库复制技能到本地技能目录
cp -r ~/.hermes/brain-os/skills/* ~/.hermes/skills/

# 验证安装
hermes skills list
```

## 目录结构

```
brain-os/
├── skills/                    # 技能目录
│   ├── brain-os-architect/    # 架构师技能
│   ├── brain-os-ops/          # 运维技能
│   └── brain-os-review/       # 审核技能
├── config/
│   └── jobs-template.json     # 定时任务配置模板
├── docs/
│   └── brain-os-architecture.md
├── scripts/
│   └── sync.sh                # 一键同步脚本
├── README.md
└── LICENSE                    # MIT
```

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_SKILLS_PATH` | 技能路径 | `$HERMES_ROOT/skills` |

### 定时任务

编辑 `config/jobs-template.json`，然后导入：

```bash
hermes cron import config/jobs-template.json
hermes cron list  # 查看已导入任务
```

## 工作流

```
┌─────────────────────────────────────────────────────────┐
│                    Brain OS 工作流                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  用户对话 ──► chronicle-agent 记录                      │
│       │                                                 │
│       ▼                                                 │
│  conversation-knowledge-flywheel 提取模式               │
│       │                                                 │
│       ▼                                                 │
│  knowledge-flywheel-amplifier 聚合知识                  │
│       │                                                 │
│       ▼                                                 │
│  llm-wiki 结构化存储                                    │
│       │                                                 │
│       ▼                                                 │
│  cron-git-state-monitoring 定时提交                     │
│       │                                                 │
│       ▼                                                 │
│  Git 仓库同步（版本历史 + 多 Agent 共享）                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 架构设计

详见 [docs/brain-os-architecture.md](docs/brain-os-architecture.md)

核心设计：
- **Layer 0**: 对话层 — 原始对话记录
- **Layer 1**: 实体层 — 人物/项目/概念提取
- **Layer 2**: 概念层 — 领域知识体系
- **Layer 3**: 查询层 — 知识检索与问答

## 开源许可

MIT License

## 致谢

灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计。