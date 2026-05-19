# Brain OS

> 一套基于 OpenClaw git-backed brain 设计的 Hermes 技能体系，实现 Agent 的 git 驱动知识管理。

## 快速安装

```bash
# 从仓库克隆技能到本地
git clone https://github.com/<your-org>/brain-os.git ~/.hermes/skills/brain-os

# 验证安装
hermes skills list | grep brain-os

# 查看技能详情
hermes skills view brain-os
```

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

## 核心技能

Brain OS 依赖以下 Hermes 内置技能（无需额外安装）：

| 技能 | 作用 |
|------|------|
| `chronicle-agent` | 对话记录归档，构建知识时间线 |
| `observer` | Agent 自检，发现错误并记录经验 |
| `llm-wiki` | 知识结构化存储 |
| `article-notes-integration` | 外部文章抓取与整合 |
| `conversation-knowledge-flywheel` | 对话模式挖掘 |
| `knowledge-flywheel-amplifier` | 跨源知识聚合 |
| `cron-git-state-monitoring` | 定时 git 提交 |

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

## 架构

灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计：

```
用户对话 → chronicle-agent 记录
    ↓
conversation-knowledge-flywheel 提取模式
    ↓
knowledge-flywheel-amplifier 聚合知识
    ↓
llm-wiki 结构化存储
    ↓
cron-git-state-monitoring 定时提交
    ↓
Git 仓库（版本历史 + 多 Agent 共享）
```

详见 [references/brain-os-architecture.md](references/brain-os-architecture.md)

## 目录结构

```
brain-os/
├── SKILL.md                 # 本文件
├── references/
│   ├── kanban-sync.py       # 同步工具
│   └── brain-os-architecture.md
├── templates/
│   └── jobs-template.json   # 任务配置模板
└── scripts/
    └── deploy.sh            # 部署脚本
```

## 开源许可

MIT License