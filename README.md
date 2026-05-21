# Brain OS

> 一套基于 Karpathy LLM Wiki 概念和 Obsidian-Brain-OS 设计灵感、结合 Hermes Kanban 任务管理的技能体系

## 这是什么

Brain OS **不是独立系统**，而是一套**可组合的技能集合**，灵感来源于 [Karpathy 的 LLM Wiki 概念](https://github.com/karpathy/llm-wiki) 和 [Obsidian-Brain-OS](https://github.com/FairladyZ625/Obsidian-Brain-OS) 的 git-backed brain 设计（将 agent 的 memory、config、workspace 存储在 git 仓库中实现持久化和多实例共享）。

**核心创新**：以 **`todo-backlog.md` 为统一任务入口**，通过 **生产者-消费者架构** 实现知识的自动生产、管理和进化，Kanban 作为 todo 的可视化界面提供双向同步。

## 快速安装

### 方式一：让 Hermes 自动安装（推荐）

直接把仓库地址发给 Hermes，让它自己完成克隆、安装、导入定时任务：

> "安装 brain-os 技能：https://github.com/jf7642132/brain-os"

### 方式二：手动安装

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

## 核心架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Brain OS 生产者-消费者架构                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    统一任务入口：todo-backlog.md                       │   │
│  │                                                                      │   │
│  │  所有发现/问题/待办 → 写入 todo → 消费者读取 → Kanban 双向同步         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              ↑                                              │
│         ┌────────────────────┼────────────────────┐                        │
│         ↓                    ↓                    ↓                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│  │ 夜间流水线   │    │ 系统运维层   │    │ 观察者自检   │                 │
│  │ (3 个任务)    │    │ (5 个任务)    │    │ (1 个任务)    │                 │
│  └──────────────┘    └──────────────┘    └──────────────┘                 │
│         ↓                    ↓                    ↓                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    消费者（从 todo 读取）                              │   │
│  │                                                                      │   │
│  │  每日早报 ← 读取 todo 高优先级 → 输出日报                             │   │
│  │  每周计划 ← 读取 todo 中优先级 → 输出周计划                           │   │
│  │  月度总结 ← 读取 todo 低优先级 → 输出月报                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Kanban 双向同步                                    │   │
│  │                                                                      │   │
│  │  todo ↔ Kanban 卡片：状态同步、防重复、唯一 ID 对应                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. todo-backlog.md（统一任务入口）

`todo-backlog.md` 是 Brain OS 的**核心枢纽**，所有生产者发现的问题写入这里，所有消费者从这里读取：

| 字段 | 说明 |
|------|------|
| `ID` | 唯一标识（H/M/L + 序号） |
| `来源任务` | 哪个任务发现的 |
| `问题描述` | 问题/待办的简要描述 |
| `状态` | `open` / `in_progress` / `resolved` / `wontfix` |
| `Kanban 卡片` | 关联的 Kanban 卡片 ID |
| `优先级` | 高/中/低（决定被哪个消费者读取） |

### 2. Kanban 双向同步

Kanban 是 `todo-backlog.md` 的**可视化界面**，不是调度中心：

| 同步方向 | 说明 |
|----------|------|
| todo → Kanban | 生产者写入 todo 时，自动创建 Kanban 卡片 |
| Kanban → todo | Kanban 卡片状态变更时，同步更新 todo 状态 |

**同步脚本**（`kanban-sync.py`）负责：

- **读取 todo 状态** — 从 `todo-backlog.md` 解析待办事项
- **创建 Kanban 卡片** — 为每个新 todo 创建对应卡片
- **双向状态同步** — Kanban 卡片状态变更时更新 todo
- **防重复机制** — 创建前检查 todo 中是否已存在相同问题

```bash
# 预览变更
python kanban-sync.py --dry-run

# 同步并提交
python kanban-sync.py --commit
```

### 3. 生产者（6 个）

生产者负责发现问题并写入 `todo-backlog.md`：

| 生产者 | 输出 | 写入 todo |
|--------|------|-----------|
| 史官记录 (chronicle-agent) | 对话归档 | 发现待办 → 写入 todo |
| 观察者自检 (observer) | 错误记录/经验 | 发现问题 → 写入 todo |
| 夜间文章抓取 (article-notes-integration) | 外部文章笔记 | 发现待办 → 写入 todo |
| 对话知识挖掘 (conversation-knowledge-flywheel) | 可复用模式 | 发现待办 → 写入 todo |
| 跨源知识聚合 (knowledge-flywheel-amplifier) | 统一知识图谱 | 发现待办 → 写入 todo |
| 周一知识库 Lint | 格式/断链报告 | 发现问题 → 写入 todo |

### 4. 消费者（3 个）

消费者从 `todo-backlog.md` 读取待办并生成报告：

| 消费者 | 输入 | 作用 |
|--------|------|------|
| 每日早报 | `todo-backlog.md`（高优先级） | 生成今日待办简报 |
| 每周计划 | `todo-backlog.md`（中优先级） | 生成周计划 |
| 月度总结 | `todo-backlog.md`（低优先级） | 生成月报 |

### 5. V2 升级方向：知识消费者

> 当前消费者仅从 todo 读取待办，未来可扩展为从 knowledge/ 读取知识：

| 消费者 | 输入 | 作用 |
|--------|------|------|
| 知识检索 | `knowledge/04-queries/` | 快速检索知识 |
| 决策支持 | `knowledge/02-concepts/` | 基于知识做决策 |
| 技能调用 | `knowledge/07-skills/` | 调用自定义技能 |
| 上下文管理 | `knowledge/06-context/` | 管理对话上下文 |

## 运行逻辑

### 夜间批处理流程

```
23:00 ──► 用户结束当日对话
              │
              ▼
02:00 ──► article-notes-integration 抓取文章 → 写入 todo
              │
              ▼
03:00 ──► conversation-knowledge-flywheel 挖掘模式 → 写入 todo
              │
              ▼
04:00 ──► knowledge-flywheel-amplifier 聚合知识 → 写入 todo
              │
              ▼
06:00 ──► kanban-sync.py 同步 todo ↔ Kanban
              │
              ▼
09:00 ──► observer 自检，检查夜间流水线状态 → 写入 todo
```

### 每日消费流程

```
07:00 ──► 每日早报 读取 todo 高优先级 → 输出日报
              │
              ▼
周一 06:00 ──► 每周计划 读取 todo 中优先级 → 输出周计划
              │
              ▼
每月 1 号 09:00 ──► 月度总结 读取 todo 低优先级 → 输出月报
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
│   ├── ops/                   # 运营概念（个人/组织）
│   └── <your-domain>/         # 自定义领域
│
├── 03-comparisons/            # Layer 2: 对比分析
├── 04-queries/                # Layer 2: 查询模板
├── 05-summaries/              # Layer 2: 总结归档
│
├── 06-context/                # Layer 3: 上下文管理
│   └── todo-tracking/         # 待办跟踪（todo-backlog.md 在此）
│
├── 07-skills/                 # Layer 3: 技能库
│   └── <skill-name>/          # 自定义技能
│
├── 08-references/             # Layer 3: 参考资料
│
└── 09-personal-data/          # 个人数据（不公开，gitignore 排除）
```

## 技能清单

Brain OS 依赖以下自定义技能，需安装到技能目录：

| 技能 | 定位 | 触发方式 |
|------|------|----------|
| `chronicle-agent` | 对话记录归档 | 夜间定时 |
| `observer` | Agent 自检 | 每次任务完成后 |
| `article-notes-integration` | 外部文章整合 | 夜间定时 (02:00) |
| `conversation-knowledge-flywheel` | 对话模式挖掘 | 夜间定时 (03:00) |
| `knowledge-flywheel-amplifier` | 跨源知识聚合 | 夜间定时 (04:00) |

> 以上技能均为自定义实现，非 Hermes 官方内置。安装时请确保这些技能已存在于 `~/.hermes/skills/` 目录中。

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_TODO_PATH` | 待办追踪路径 | `$HERMES_KNOWLEDGE/06-context/todo-tracking/todo-backlog.md` |
| `BRAINO_GIT_REPO` | Git 仓库路径 | `$HERMES_ROOT/brain-os` |

### 导入定时任务（jobs-template.json）

`templates/jobs-template.json` 是 **脱敏版定时任务模板**，包含 19 个 Brain OS 核心任务的配置。导入前需要替换占位符：

#### 步骤 1：复制模板

```bash
cp ~/.hermes/skills/brain-os/templates/jobs-template.json ~/.hermes/brain-os-jobs.json
```

#### 步骤 2：替换占位符

打开 `~/.hermes/brain-os-jobs.json`，替换以下占位符：

| 占位符 | 替换为 | 说明 |
|--------|--------|------|
| `<YOUR_WEIXIN_CHAT_ID>` | `o9cq802KK_bHFh7CbnaLfVpn24GY@im.wechat` | 微信聊天 ID |
| `<YOUR_TELEGRAM_CHAT_ID>` | `8377601886` | Telegram 聊天 ID |
| `<YOUR_CHAT_ID>` | `1234567890` | 其他聊天 ID |
| `<KNOWLEDGE_DIR>` | `/path/to/your/knowledge` | 知识库路径 |
| `<PAPERCLIP_URL>` | `http://<YOUR_PAPERCLIP_URL>` | Paperclip 服务地址（可选） |

#### 步骤 3：导入任务

```bash
# 导入到 hermes cron
hermes cron import ~/.hermes/brain-os-jobs.json

# 查看已导入任务
hermes cron list

# 启用/禁用任务
hermes cron enable <task-id>
hermes cron disable <task-id>
```

#### 步骤 4：验证任务

```bash
# 查看任务详情
hermes cron show <task-id>

# 手动触发任务测试
hermes cron run <task-id>
```

#### 任务列表（14 个）

| 任务名称 | 调度 | 作用 |
|----------|------|------|
| Brain OS 每日早报 | `0 7 * * *` | 生成今日待办简报 |
| Brain OS 午间待办提醒 | `0 14 * * *` | 午间待办提醒 |
| Brain OS 晚间待办提醒 | `30 20 * * *` | 晚间待办提醒 |
| Brain OS 史官记录 | `every 120m` | 对话记录归档 |
| Brain OS 自动提交巡检 | `0 */1 * * *` | 自动提交知识变更 |
| Brain OS 夜间文章整合 | `0 2 * * *` | 文章整合流水线 |
| Brain OS 夜间对话挖掘 | `0 3 * * *` | 对话模式挖掘 |
| Brain OS 夜间知识放大器 | `0 4 * * *` | 跨源知识聚合 |
| Brain OS 每日观察者自检 | `30 0 * * *` | Agent 健康监控 |
| Brain OS 每周计划 | `0 6 * * 1` | 周计划生成 |
| Brain OS 月度总结 | `0 9 1 * *` | 月度报告生成 |
| Brain OS 周一知识库 Lint | `0 6 * * 1` | 知识库质量检查 |
| Brain OS 每周知识库审计 | `0 7 * * 0` | 知识库审计 |

### 自定义调度

编辑 `~/.hermes/brain-os-jobs.json` 中的 `schedule.expr` 字段来自定义调度时间：

```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *"  // 改为每天 8 点执行
  }
}
```

## 使用

### 同步 todo 到 Kanban

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

### 查看 todo 和 Kanban 状态

```bash
# 查看 todo 待办
cat ~/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md

# 列出所有 Kanban 卡片
hermes kanban list

# 查看任务状态
hermes kanban status
```

## 架构设计

详见 [references/brain-os-architecture.md](references/brain-os-architecture.md)

## 开源许可

MIT License

## 致谢

灵感来源于 [Karpathy 的 LLM Wiki 概念](https://github.com/karpathy/llm-wiki) 和 [Obsidian-Brain-OS](https://github.com/FairladyZ625/Obsidian-Brain-OS) 的 git-backed brain 设计。

## 更新日志

### 2026-05-21

- 移除通用生产力工具（airtable, notion, powerpoint 等 10 个）
- 更新 SKILL.md 和 README.md 依赖说明
- 移除外贸风险相关任务（非 Brain OS 核心）
- 仓库精简至 97 个文件

### 2026-05-20

- 添加 `templates/jobs-template.json` 脱敏版定时任务模板
- 添加 54 个技能到开源仓库
- 添加 23 个实用脚本
- 更新 `.gitignore` 排除敏感文件
- 所有 chat IDs 替换为占位符