# Brain OS 架构设计

> 一套基于 Karpathy LLM Wiki 概念和 Obsidian-Brain-OS 设计灵感的 Hermes 技能体系

## 核心理念

Brain OS 不是独立系统，而是一套**可组合的技能集合**，灵感来源于 [Karpathy 的 LLM Wiki 概念](https://github.com/karpathy/llm-wiki) 和 [Obsidian-Brain-OS](https://github.com/FairladyZ625/Obsidian-Brain-OS) 的 git-backed brain 设计：

- **Git-backed 知识管理**：所有知识存储在 git 仓库中，版本可控
- **技能可组合**：每个技能独立，可按需组合
- **自动化工作流**：夜间自动同步、知识挖掘、经验总结
- **多 Agent 共享**：同一知识库可被多个 Agent 访问

## 技能清单

Brain OS 包含 5 个核心技能，均为自定义实现：

| 技能 | 定位 | 触发方式 |
|------|------|----------|
| `chronicle-agent` | 对话记录归档 | 夜间定时 |
| `observer` | Agent 自检 | 每次任务完成后 |
| `article-notes-integration` | 外部文章整合 | 夜间定时 |
| `conversation-knowledge-flywheel` | 对话模式挖掘 | 夜间定时 |
| `knowledge-flywheel-amplifier` | 跨源知识聚合 | 夜间定时 |

> 以上技能均为自定义实现，非 Hermes 官方内置。

## 数据流架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Brain OS 数据流                              │
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
│                     └────────────────┬─────────────────────────┘   │
│                                      │                              │
│                                      ▼                              │
│                     ┌──────────────────────────────────────────┐   │
│                     │  Git 自动提交 (cron-git-state-monitoring)  │   │
│                     │  → 定时提交 → Git 仓库                     │   │
│                     └──────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## 目录结构规范

```
knowledge/
├── 00-raw/                    # Layer 0: 原始数据
│   └── transcripts/           # 对话原始记录（个人数据，gitignore 排除）
│
├── 01-entities/               # Layer 1: 实体提取
│   ├── people/                # 人物信息
│   ├── projects/              # 项目信息（个人数据，gitignore 排除）
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

## 技能配置

### article-notes-integration

夜间抓取外部文章并整合：

```json
{
  "name": "nightly-article-integration",
  "schedule": "0 3 * * *",
  "command": "hermes skills run article-notes-integration"
}
```

### Git 自动提交

使用 cron-git-state-monitoring 技能或系统级 cron 任务：

```bash
# 系统级 cron 任务
0 2 * * * cd ~/.hermes && git add -A && git commit -m 'nightly sync' || true && git push
```

## 多 Agent 协作

同一知识库可被多个 Agent 共享：

```
┌─────────────────────────────────────────────────────────┐
│                    多 Agent 协作模式                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Agent A ──┐                                           │
│             ├──► Git 仓库 ──► 知识库同步                │
│   Agent B ──┘                                           │
│                                                         │
│   共享内容：                                             │
│   - knowledge/02-concepts/  (概念体系)                  │
│   - knowledge/04-summaries/ (总结归档)                  │
│   - knowledge/06-context/   (上下文)                    │
│                                                         │
│   个人内容（不共享）：                                   │
│   - knowledge/00-raw/transcripts/                       │
│   - knowledge/01-entities/projects/                     │
│   - knowledge/09-personal-ops/                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 部署方式

### 方式一：技能目录挂载

```bash
# 克隆技能仓库
git clone https://github.com/<your-org>/brain-os.git ~/.hermes/brain-os

# 配置技能路径
hermes config set skills.paths+=~/.hermes/brain-os/skills
```

### 方式二：直接复制

```bash
# 复制技能到本地
cp -r ~/.hermes/brain-os/skills/* ~/.hermes/skills/
```

### 方式三：环境变量

```bash
export HERMES_SKILLS_PATH=~/.hermes/brain-os/skills
hermes
```

## 开源许可

MIT License

## 致谢

灵感来源于 [Karpathy 的 LLM Wiki 概念](https://github.com/karpathy/llm-wiki) 和 [Obsidian-Brain-OS](https://github.com/FairladyZ625/Obsidian-Brain-OS) 的 git-backed brain 设计。