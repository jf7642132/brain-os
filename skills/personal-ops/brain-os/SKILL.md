---
name: brain-os
description: "Brain OS 个人操作系统架构与数据流闭环"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [brain-os, knowledge-base, data-flow, kanban, todo]
    category: personal-ops
    related_skills: [llm-wiki, cronjob, kanban]
---

# Brain OS 技能体系

基于 OpenClaw git-backed brain 设计灵感的 Hermes 技能体系，实现 Agent 的 git-backed brain 工作流。

> **重要定位**：Brain OS 不是独立系统，而是一套**可组合的技能集合**。灵感来源于 [OpenClaw](https://github.com/openclaw/openclaw) 的 git-backed brain 设计：Agent 的知识库、记忆、配置全部存储在 git 仓库中，每次启动自动同步，夜间自动提交变更。

## 当此技能激活

- 用户询问 Brain OS 架构、数据流、目录结构
- 需要创建/修改 kanban-sync.py 或 todo 相关脚本
- 需要整理知识库目录结构
- 需要设置新的 cron 任务并绑定数据流

---

## 一、核心架构

### 1.1 知识库结构（llm-wiki Layer 1/2）

```
knowledge/
├── SCHEMA.md              # 知识库规范
├── index.md               # 内容索引
├── log.md                 # 操作日志
│
├── 00-raw/                # Layer 1: 原始来源（不可变）
│   ├── articles/          # 文章、摘录
│   ├── papers/            # PDF、论文
│   ├── transcripts/       # 对话记录、会议笔记
│   │   └── 频道历史/      # 史官记录
│   └── assets/            # 图片、图表
│
├── 01-entities/           # Layer 2: 实体页面
│   ├── companies/
│   ├── people/
│   ├── products/
│   └── projects/
│
├── 02-concepts/           # Layer 2: 概念页面
│   ├── ai-ops/
│   ├── chemical-trade/
│   └── personal-ops/
│
├── 03-comparisons/        # Layer 2: 对比分析
├── 04-queries/            # Layer 2: 查询结果
├── 05-outputs/            # Layer 2: 工作产出
│   ├── work-reports/      # 工作汇报
│   ├── work-notes/        # 工作笔记
│   ├── project-reports/   # 项目报告
│   ├── daily-briefing/
│   ├── weekly-plan/
│   └── monthly-summary/
│
├── 06-context/            # Layer 2: 上下文
│   ├── todo-tracking/     # 待办跟进（统一入口）
│   ├── digital-ops/       # 数字化运维
│   ├── decisions/
│   └── stakeholders/
│
├── 07-config/             # Layer 2: 配置
│   ├── cron/
│   ├── memory/
│   └── scripts/
│
├── 08-archive/            # 归档
│
└── 99-system/             # 系统级
    ├── BRAIN-OS-ARCHITECTURE.md
    ├── kanban/
    ├── lint-reports/
    └── trackers/
```

### ⚠️ 目录命名规范

- **禁止中文目录名**：所有目录必须使用英文命名
- **已有中文目录需迁移**：按内容归类到对应英文目录
- **路径引用需同步更新**：脚本、prompt 中的路径必须使用新路径

---

## 二、数据流闭环

### 2.1 核心数据流

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         完整数据流闭环                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  生产者 (5 个任务)                                                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ 史官记录     │    │ 观察者自检   │    │ 知识库审计   │              │
│  │ 知识库 Lint  │    │ 自动提交巡检 │    │              │              │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘              │
│         │                   │                   │                       │
│         └───────────────────┼───────────────────┘                       │
│                             ▼                                           │
│                    ┌────────────────┐                                   │
│                    │  --write-todo  │  生产者只写入 todo                │
│                    │  输出 → todo   │  不直接创建 Kanban               │
│                    └───────┬────────┘                                   │
│                            │                                            │
│                            ▼                                            │
│              ┌───────────────────────────────┐                          │
│              │   todo-backlog.md (统一入口)   │                          │
│              │   - 高优先级 / 中优先级 / 低优先级│                          │
│              │   - 已完成                      │                          │
│              └───────────────┬───────────────┘                          │
│                              │                                           │
│              ┌───────────────┴───────────────┐                          │
│              ▼                               ▼                          │
│  ┌────────────────────┐         ┌────────────────────┐                 │
│  │ Kanban 管理层任务   │         │  消费者 (5 个任务)   │                 │
│  │ --read-todo        │         │  每日早报          │                 │
│  │ (定期运行)         │         │  待办提醒          │                 │
│  │ todo → Kanban      │         │  晚间待办提醒      │                 │
│  └───────────┬────────┘         │  每周计划          │                 │
│              │                  │  月度总结          │                 │
│              ▼                  └────────────────────┘                 │
│  ┌────────────────────┐                                                │
│  │ Kanban 卡片        │                                                │
│  │ (状态追踪)         │                                                │
│  └───────────┬────────┘                                                │
│              │                                                          │
│              │  Kanban 状态变更时                                         │
│              │  (完成/关闭/更新)                                         │
│              ▼                                                          │
│  ┌────────────────────┐                                                │
│  │ --update-todo      │  Kanban → todo 回写闭环                         │
│  │ Kanban → todo      │  更新 todo 状态/完成时间                        │
│  └────────────────────┘                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 生产者规则

| 规则 | 说明 |
|------|------|
| **禁止直接输出到 Kanban** | 生产者必须使用 `--write-todo` 模式 |
| **写入 todo 后不创建 Kanban** | Kanban 由管理层统一创建 |
| **输出格式** | 按任务特定 pattern 提取问题/发现项 |

### 2.3 消费者规则

| 规则 | 说明 |
|------|------|
| **从 todo 读取** | 消费者必须读取 `06-context/todo-tracking/todo-backlog.md` |
| **不直接操作 Kanban** | 消费者只读取 todo，不修改 Kanban |
| **路径引用** | 必须使用新路径 `06-context/todo-tracking/` |

### 2.4 Kanban 管理层规则

| 规则 | 说明 |
|------|------|
| **定期运行 `--read-todo`** | 从 todo 创建 Kanban 卡片 |
| **状态变更时 `--update-todo`** | Kanban 完成时回写 todo |
| **防重复机制** | 创建卡片前检查 todo 中是否已存在 |

---

## 三、kanban-sync.py 使用规范

### 3.1 三种模式

```bash
# 生产者模式：输出 → todo
python kanban-sync.py --task <task_name> --write-todo --output <output_file>

# 管理层模式：todo → Kanban
python kanban-sync.py --task <task_name> --read-todo

# 回写模式：Kanban → todo
python kanban-sync.py --task <task_name> --update-todo --kanban-id <id> --status <status>
```

### 3.2 参数说明

| 参数 | 说明 | 必需模式 |
|------|------|----------|
| `--task` | 任务名称（如 observer-self-check） | 所有 |
| `--output` | 任务输出文件路径 | --write-todo |
| `--write-todo` | 写入 todo 模式 | 生产者 |
| `--read-todo` | 读取 todo 模式 | 管理层 |
| `--update-todo` | 更新 todo 模式 | 回写 |
| `--kanban-id` | Kanban 卡片 ID | --update-todo |
| `--status` | 新状态 (open/in_progress/resolved/wontfix) | --update-todo |
| `--completed-date` | 完成日期 | --update-todo |
| `--method` | 处理方式 | --update-todo |
| `--dry-run` | 预览模式 | 所有 |

### 3.3 路径配置

脚本中的路径常量：

```python
KNOWLEDGE_PATH = os.path.join(HERMES_ROOT, "knowledge")
TRACKERS_DIR = os.path.join(KNOWLEDGE_PATH, "99-system", "trackers")
TODO_PATH = os.path.join(KNOWLEDGE_PATH, "06-context", "todo-tracking", "todo-backlog.md")
```

⚠️ **重要**：路径必须使用英文目录名，禁止使用中文目录名。

---

## 四、cron 任务配置

### 4.1 生产者任务

| 任务 ID | 任务名称 | 模式 | 时间 |
|--------|----------|------|------|
| `728448c1` | 史官记录 | --write-todo | 每 2h |
| `3cda2159` | 观察者自检 | --write-todo | 00:30 每天 |
| `1a37493b` | 知识库审计 | --write-todo | 01:30 周一 |
| `b62a532b` | 知识库 Lint | --write-todo | 01:00 周一 |
| `ce8a1963` | 自动提交巡检 | --write-todo | 整点 |

### 4.2 消费者任务

| 任务 ID | 任务名称 | 读取 todo | 时间 |
|--------|----------|-----------|------|
| `a750c4eb` | 每日早报 | ✓ | 07:00 每天 |
| `974794d1` | 待办提醒 | ✓ | 15:00 每天 |
| `409b522e` | 晚间待办提醒 | ✓ | 20:30 每天 |
| `4616b8bd` | 每周计划 | ✓ | 06:00 周一 |
| `df75453a` | 月度总结 | ✓ | 09:00 每月 1 号 |

### 4.3 Kanban 管理层任务

| 任务 ID | 任务名称 | 模式 | 时间 |
|--------|----------|------|------|
| (待创建) | kanban-manager | --read-todo | 定期运行 |

---

## 五、pitfalls

### 5.1 中文目录陷阱

**问题**：迁移知识库时，直接重命名中文目录会导致：
- 路径引用失效（脚本、prompt 中仍引用旧路径）
- 内容未重新归类（只是改名，未按 llm-wiki 规范整理）

**正确做法**：
1. 梳理中文目录内容
2. 按 llm-wiki Layer 1/2 架构重新归类
3. 更新所有路径引用（脚本、prompt、配置文件）
4. 删除空目录

### 5.2 数据流断裂

**问题**：生产者直接输出到 Kanban，绕过 todo 统一入口。

**正确做法**：
1. 生产者只使用 `--write-todo` 模式
2. 管理层定期运行 `--read-todo` 创建 Kanban
3. Kanban 状态变更时运行 `--update-todo` 回写 todo

### 5.3 路径引用不一致

**问题**：
- todo-backlog.md 已移动到新路径，但脚本仍引用旧路径
- 消费者任务 prompt 中仍引用 `03-个人运营/03-待办跟进/`

**正确做法**：
1. 统一使用 `06-context/todo-tracking/todo-backlog.md`
2. 更新 kanban-sync.py 中的 TODO_PATH
3. 更新所有 cron 任务 prompt 中的路径引用

### 5.4 防重复机制缺失

**问题**：同一问题被多次创建 Kanban 卡片。

**正确做法**：
1. 创建卡片前检查 todo 中是否已存在相同问题
2. 通过问题摘要相似度 + 来源任务 + Kanban 卡片 ID 判断
3. 已存在的跳过或更新状态

### 5.5 Todo Backlog 脏数据

**问题**：史官等生产者任务在不同日期重复记录同一问题，导致 todo-backlog.md 中存在大量重复/碎片化条目。

**常见模式**（2026-05-19 发现）：
- LLM Wiki 相关：9 次重复记录
- Telegram 推送错误：2 次重复
- 钉钉鉴权失败：2 次重复
- WebUI 构建超时：5 条碎片化记录（拆成任务 ID/路径/Git/命令/超时 5 条）

**影响**：
- 阻塞项统计虚高（21 条实际仅 8 条有效）
- 日报/周报质量下降
- Kanban 卡片创建混乱

**检测**：
```bash
# 按主题关键词聚类检测重复
grep -E "TODO-[0-9]+-" todo-backlog.md | sed 's/|.*//' | sort | uniq -c | sort -rn
```

**修复**：
1. 合并重复条目，保留最新一条
2. 合并碎片化条目为单一条目
3. 标记已解决但未更新状态的条目为 `resolved`
4. 史官 prompt 改造：记录前检查是否已存在相同主题

**参考**：`personal-ops-driver` skill 的 `references/todo-backlog-dirty-data-patterns.md`

### 5.6 Kanban 与 Todo 不同步

**问题**：`hermes kanban list --status open` 返回空，但 todo-backlog.md 中有多个 open 条目

**原因**：kanban-sync.py 的 `--read-todo` 模式未定期运行

**检测**：
```bash
# 对比 todo 和 Kanban 的 open 数量
grep -c "| open |" todo-backlog.md
hermes kanban list --status open | wc -l
```

**修复**：定期运行 `kanban-sync.py --read-todo`，确保 todo → Kanban 同步

### 5.7 残留中文目录清理

**问题**：迁移知识库时，旧中文目录可能残留（如 `03-个人运营/` 与 `03-personal-ops/` 并存），导致：
- 内容分散在两个目录
- cron 任务可能引用错误路径
- git 提交混乱

**检测**：
```bash
# 查找所有中文目录
find /root/.hermes/knowledge -type d -name '*[一-龥]*'

# 检查是否有重复目录
ls -la /root/.hermes/knowledge/ | grep -E "03-个人运营|03-personal-ops"
```

**修复**：
1. 确认新目录已创建且内容已迁移
2. 检查 cron 任务是否已更新路径引用
3. 删除旧中文目录（需确认无残留内容）
4. 提交 git 变更

**注意**：删除目录前务必确认：
- 新目录存在且内容完整
- cron 任务已更新路径引用
- 无其他脚本引用旧路径

### 5.8 kanban-sync.py: read_todo_backlog 与实际文件格式不匹配

**问题**：`kanban-sync.py` 的 `read_todo_backlog()` 函数硬编码解析 `## 高优先级` / `## 中优先级` / `## 低优先级` 章节下的固定 9 列表格（ID/来源/描述/状态/kanban_id/创建时间/更新时间/方式/完成时间），但实际的 `todo-backlog.md` 使用**日期-Journal 格式**，表格列数不同（4-5 列：分类/内容/状态/来源/时间），章节标题也不是固定优先级分类，而是 `## 2026-05-19` 时间戳。

**效果**：脚本运行后输出"待创建 Kanban 的 todo: 0 个"并提前 return，**实际是解析失败而非没有待办**。这是一个静默失败——脚本不会报错，只是返回空结果。

**检测**：
```bash
# 1. 用脚本读（可能返回空）
python3 /root/.hermes/scripts/kanban-sync.py --task kanban-manager --read-todo

# 2. 直接看文件确认是否有真正待办
grep -c "待执行" /root/.hermes/knowledge/todo-backlog.md

# 3. 如果 grep 返回 >0 但脚本说 0，就是格式不匹配
```

**修复方向**（如遇到，需要修改 `read_todo_backlog()` 函数）：
- 替代硬编码的 `## 高优先级` / `## 中优先级` 标题匹配，改用正则 `^## \d{4}-\d{2}-\d{2}` 检测日期章节
- 替代固定 9 列表格解析（`parts[0]=ID, parts[1]=来源...`），改为检测 `parts[0]` 是否为 `ops/config/notes` 这种分类标签来识别待办行
- 在 `pending_items` 为空时增加警告日志，提示可能是格式不匹配而非真的没有待办

### 5.9 kanban-sync.py 已知 Bug（已修复，在 2026-05-19 会话）

以下两个 bug 在 2026-05-19 的 Brain OS Kanban 管理层执行中被发现并修复，便于后续回溯：

| Bug | 症状 | 修复位置 | 修复内容 |
|-----|------|----------|----------|
| `task_name` 未定义 | `--read-todo` 模式：`UnboundLocalError: cannot access local variable 'task_name'` | `main()` 函数中 `if args.read_todo:` 块 | 在块内添加 `config = TASK_CONFIG.get(args.task, {}); task_name = config.get("name", args.task)` |
| `description` 参数名错误 | `create_kanban_task() got an unexpected keyword argument 'description'` | `main()` 函数中 `create_kanban_task()` 调用处 | `description=` 改为 `body=`（函数签名使用 `body` 参数） |

### 5.10 观察者 Session 文件格式不匹配（已修复，2026-05-19）

**问题**：Hermes Agent 存储 session 文件为 `.json` 格式（单个 JSON 对象），但 observer 技能期望 `.jsonl` 格式（每行一个 JSON 对象）。

**症状**：
- Observer cron 任务（00:30 运行）找不到今天的 session 文件
- 回退到昨天的 session 数据
- 生成 `2026-05-18-iteration-plan.md` 而非当天的报告

**根因**：
- 实际 session 文件：`session_20260519_105333_314e8b.json`
- 技能期望：`20260519_*.jsonl`

**修复**：
1. 更新 observer 技能 Step 1 的 shell 脚本，检查 `.json` 和 `.jsonl` 两种扩展名
2. 新增 Session File Format Detection Python 代码块
3. 更新 cron 任务 prompt 加入 session 格式说明

**参考**：`observer` skill 的 `references/session-file-format.md`

### 5.11 Telegram 推送失败：Bot 无法发送消息给 Bot（已修复，2026-05-19）

**问题**：Observer cron 任务配置 `deliver: telegram` 和 `telegram_chat_id: <YOUR_TELEGRAM_CHAT_ID>`，但推送目标是一个 bot，Telegram 不允许 bot 发送消息给另一个 bot。

**症状**：
```
delivery error: Telegram send failed: Forbidden: the bot can't send messages to the bot
```

**根因**：
- `telegram_chat_id` 配置为 bot 的 chat ID
- Telegram API 限制：bot 不能发送消息给 bot

**修复**：
1. 将 cron 任务 `deliver` 改为 `local`
2. 移除 `telegram_chat_id` 配置
3. 或配置为用户/群组的 chat ID（非 bot）

**验证**：
```bash
# 检查 cron 任务配置
hermes cron list | grep -A5 "观察者"

# 确认 deliver 和 telegram_chat_id
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | select(.name | contains("观察者")) | {deliver, telegram_chat_id}'
```

### 5.13 自动提取的待办描述被截断（2026-05-20 发现）

**问题**：夜间知识放大器等生产者任务自动提取的待办项，描述字段可能被截断。

**症状**：
- `M001`: "4 月 16 日至 18 日的 3 篇外贸风险预警日报积压超过 30 天，未进" — 描述被截断
- `M002`: "任务状态仍为 "In Progress"，预计完成时间" — 描述被截断

**根因**：生产者任务在提取待办时，描述字段长度受限，导致长描述被截断。

**影响**：
- 日报中待办描述不完整，影响优先级判断
- 用户无法从待办列表中了解完整问题

**修复**：
1. 在生成日报前，检查待办描述是否完整（如以"未进"、"预计"等不完整结尾）
2. 如不完整，标注为"⚠️ 描述被截断，需核实完整内容"
3. 反馈给生产者任务 prompt，要求完整描述或分段存储
4. 考虑在 todo-backlog.md 中增加"完整描述"字段或链接到详细报告

**预防**：
- 生产者任务 prompt 中明确要求：描述字段不超过 200 字符，超长时截断到关键信息
- 或增加 `detail_path` 字段，指向详细报告文件

**问题**：月度总结任务（`df75453a`）上次运行返回空响应。

**症状**：
```json
"last_status": "error",
"last_error": "Agent completed but produced empty response (model error, timeout, or misconfiguration)"
```

**可能原因**：
1. 模型超时（prompt 较长，约 2500 字符）
2. 模型配置问题
3. 数据源路径不存在或为空

**待观察**：等待下次运行（6 月 1 日 09:00），如仍失败则：
1. 简化 prompt
2. 切换模型
3. 检查数据源路径

### 5.14 技能文档路径漂移（2026-05-20 发现）

**问题**：定时任务技能的 SKILL.md 文档中同时保留了英文路径和中文路径，导致定时任务执行时输出了中文目录。

**症状**：
```
/root/.hermes/knowledge/03-知识库/
/root/.hermes/knowledge/04-知识库/
/root/.hermes/knowledge/99-系统/
```

**根因**：
- `article-notes-integration` 技能文档保留旧版 wiki 路径（`03-知识库/`）
- `conversation-knowledge-flywheel` 技能文档明确写中文路径（`04-知识库/99-系统/`）
- `knowledge-flywheel-amplifier` 技能文档明确写中文路径（`04-知识库/99-系统/`）

**影响**：
- 定时任务执行时按技能文档中的路径输出，产生中文目录
- 知识库结构混乱，内容分散在多个路径
- git 提交混乱

**检测**：
```bash
# 查找所有中文目录
find /root/.hermes/knowledge -type d -name '*[一-龥]*'

# 检查技能文档中的路径引用
grep -r "03-知识库\|04-知识库\|99-系统" /root/.hermes/skills/article-notes-integration/
grep -r "04-知识库\|99-系统" /root/.hermes/skills/conversation-knowledge-flywheel/
grep -r "04-知识库\|99-系统" /root/.hermes/skills/knowledge-flywheel-amplifier/
```

**修复**：
1. 统一技能文档中的路径为英文（`99-system/`、`04-queries/`）
2. 移除所有中文路径注释和备选路径说明
3. 清理已生成的中文目录
4. 验证 cron 任务输出路径正确

**预防**：
- 技能文档中路径引用必须与实际系统结构一致
- 迁移后必须 grep 检查所有技能文档中的路径引用
- 不要同时保留中英文路径作为"备选"
- 文档中的路径示例必须可运行

### 5.15 README 结构优化原则

**问题**：README 中"快速安装"章节位置靠后，用户需要先阅读大量架构说明才能看到安装步骤。

**正确做法**：
1. **快速安装前置**：将"快速安装"放在"这是什么"之后，让用户先看到如何入手
2. **提供自动安装选项**：添加"让 Hermes 自动安装"的选项，降低安装门槛
3. **保持结构清晰**：标题 → 一句话说明 → 快速安装 → 核心架构 → 核心组件 → 使用 → 配置

**参考**：开源项目 README 标准结构：
```
标题 + 副标题
↓
这是什么（一句话说明）
↓
快速安装（立刻能动手）
↓
核心架构（架构图）
↓
核心组件 → 运行逻辑 → 目录结构 → 技能清单 → 配置 → 使用 → 区别 → 许可 → 致谢
```

### 5.16 技能描述准确性

**问题**：技能清单中错误标注为"Hermes 内置技能（无需额外安装）"，实际为自定义技能。

**正确做法**：
1. 明确标注技能来源（官方内置 vs 自定义）
2. 自定义技能需说明安装要求
3. 不要误导用户以为技能是官方自带的

**参考**：README 技能清单应标注：
```markdown
> 以上技能均为自定义实现，非 Hermes 官方内置。安装时请确保这些技能已存在于 `~/.hermes/skills/` 目录中。
```
---

## 六、验证清单

### 6.1 目录结构验证

```bash
# 检查是否有中文目录
find /root/.hermes/knowledge -type d -name '*[一-龥]*'

# 检查 todo-backlog.md 位置
ls -la /root/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md
```

### 6.2 数据流验证

```bash
# 测试 --write-todo 模式
python /root/.hermes/scripts/kanban-sync.py --task observer-self-check --write-todo --dry-run

# 测试 --read-todo 模式
python /root/.hermes/scripts/kanban-sync.py --task kanban-manager --read-todo --dry-run

# 测试 --update-todo 模式
python /root/.hermes/scripts/kanban-sync.py --task kanban-manager --update-todo --kanban-id <id> --status resolved --dry-run
```

### 6.3 路径引用验证

```bash
# 检查 kanban-sync.py 中的路径
grep -n "TODO_PATH\|TRACKERS_DIR" /root/.hermes/scripts/kanban-sync.py

# 检查 cron 任务中的路径引用
grep -r "03-个人运营\|待办跟进" /root/.hermes/cron/jobs.json
```

---

## 七、阶段实施路线图

### P0: 知识库结构整理

**目标**：按 llm-wiki 规范重构知识库目录结构

**步骤**：

1. **创建新目录结构**
```bash
cd /root/.hermes/knowledge
mkdir -p 00-raw/{articles,papers,transcripts/assets}
mkdir -p 01-entities/{projects,companies,products,people}
mkdir -p 02-concepts/{trade-risk,chemical-trade,ai-ops,personal-ops}
mkdir -p 03-comparisons/{models,strategies,tools}
mkdir -p 04-queries/{daily,weekly,monthly}
mkdir -p 05-outputs/{nightly-digest,daily-briefing,weekly-plan,monthly-summary,observer,audit}
mkdir -p 06-context/{decisions,patterns,lessons,stakeholders}
mkdir -p 07-config/{cron,prompts,scripts}
mkdir -p 08-archive
mkdir -p 99-system/{lint-reports,trackers,kanban}
```

2. **编写核心文档**
   - `SCHEMA.md` - 知识库规范（目录结构、frontmatter、tag taxonomy）
   - `index.md` - 内容索引（按实体/概念/对比/查询/输出分类）
   - `log.md` - 操作日志（记录结构重构操作和待办）

3. **迁移现有文件**
   - 按新结构迁移文件
   - **中文目录改为英文，文件名保留中文**（可读性优先）
   - 清理空目录

4. **更新 cron 任务 workdir**
```bash
hermes cron edit <job-id> --workdir /root/.hermes/knowledge
```

5. **验证新结构**
```bash
ls -R /root/.hermes/knowledge
# 检查中文目录
find /root/.hermes/knowledge -type d -name "*[一-龥]*"
```

**完成标准**：
- ✅ 10 个主目录均为英文
- ✅ 文件名保留中文（可读性优先）
- ✅ SCHEMA.md、index.md、log.md 已创建
- ✅ git 提交

---

### P1: todo 格式扩展 + kanban-sync.py 双向同步

**目标**：todo-backlog.md 扩展格式，kanban-sync.py 支持双向同步

**步骤**：

1. **扩展 todo-backlog.md 格式**
```markdown
# 待办积压

## 高优先级

| ID | 来源任务 | 问题描述 | 状态 | Kanban 卡片 | 创建时间 | 最后更新 | 处理方式 | 完成时间 |
|----|----------|----------|------|-------------|----------|----------|----------|----------|
| H001 | `b62a532b` Lint | 443 个文件缺失 frontmatter | open | `t_a3268cfc` | 2026-05-18 | 2026-05-18 | 自动修复 | - |

## 中优先级

## 低优先级

## 已完成/已归档
```

2. **改造 kanban-sync.py 增加三种模式**

```python
# 新增参数
parser.add_argument("--write-todo", action="store_true", help="输出 → todo")
parser.add_argument("--read-todo", action="store_true", help="todo → Kanban")
parser.add_argument("--update-todo", action="store_true", help="Kanban → todo")

# 核心函数
def read_todo_backlog(todo_path):
    """读取 todo 中 open 状态的待办"""
    
def write_todo_backlog(todo_path, problem_summary, source_task, priority):
    """写入 todo（防重复）"""
    
def update_todo_from_kanban(todo_path, kanban_id, new_status):
    """根据 Kanban 状态更新 todo"""
```

3. **测试双向同步**
```bash
# 测试 --write-todo
python3 kanban-sync.py --write-todo --task test

# 测试 --read-todo
python3 kanban-sync.py --read-todo --task kanban-manager

# 测试 --update-todo
python3 kanban-sync.py --update-todo --task kanban-manager
```

**完成标准**：
- ✅ todo-backlog.md 9 个字段完整
- ✅ kanban-sync.py 支持 3 种模式
- ✅ 防重复机制（问题摘要相似度 + 来源任务 + Kanban 卡片 ID）
- ✅ 双向同步（todo ID ↔ Kanban 卡片 ID 一一对应）

---

### P2: 史官记录待办一次性提取

**目标**：从史官记录中提取待办，一次性写入 todo

**步骤**：

1. **编写提取脚本**
```python
#!/usr/bin/env python3
# scripts/extract-chronicle-todos.py

import re
from pathlib import Path

TODO_PATTERNS = [
    r'待办[:：]\s*(.+)',
    r'需要[:：]\s*(.+)',
    r'应该[:：]\s*(.+)',
    r'建议[:：]\s*(.+)',
    r'计划[:：]\s*(.+)',
    r'TODO[:：]\s*(.+)',
]

def extract_from_file(file_path):
    """从单个史官文件提取待办"""
    content = file_path.read_text(encoding='utf-8')
    todos = []
    for pattern in TODO_PATTERNS:
        matches = re.findall(pattern, content)
        todos.extend(matches)
    return todos

def classify_priority(text):
    """优先级分类"""
    high_keywords = ['紧急', '重要', '必须', '立即', 'P0', '关键']
    mid_keywords = ['应该', '建议', '计划', '需要']
    
    if any(k in text for k in high_keywords):
        return 'H'
    elif any(k in text for k in mid_keywords):
        return 'M'
    return 'L'
```

2. **运行提取脚本**
```bash
# Dry-run 预览
python3 extract-chronicle-todos.py --dry-run

# 执行提取
python3 extract-chronicle-todos.py --write
```

3. **写入 todo-backlog.md**
   - 按优先级分类（H/M/L）
   - 生成唯一 ID（H001, M001, L001...）
   - 记录来源任务、创建时间

**完成标准**：
- ✅ 提取脚本可运行
- ✅ 待办写入 todo-backlog.md
- ✅ 分类清晰（高/中/低优先级）

---

### P3: 生产者/消费者 prompt 改造

**目标**：生产者写入 todo，消费者读取 todo

**生产者任务（8 个）**：

| 任务 | 修改内容 |
|------|----------|
| 史官记录 | 增加"提取待办 → 写入 todo"步骤 |
| 观察者自检 | 增加"发现问题 → 写入 todo"步骤 |
| 知识库审计 | 增加"发现问题 → 写入 todo"步骤 |
| Lint | 增加"发现问题 → 写入 todo"步骤 |
| 自动提交巡检 | 增加"发现异常 → 写入 todo"步骤 |
| 夜间文章整合 | 增加"提取要点 → 写入 todo"步骤 |
| 夜间对话挖掘 | 增加"提取知识 → 写入 todo"步骤 |
| 夜间知识放大器 | 增加"合成洞察 → 写入 todo"步骤 |

**消费者任务（5 个）**：

| 任务 | 修改内容 |
|------|----------|
| 每日早报 | 增加"读取 todo → 生成日报"步骤 |
| 每周计划 | 增加"读取 todo → 生成周计划"步骤 |
| 月度总结 | 增加"读取 todo → 生成月报"步骤 |
| 午间待办提醒 | 读取 todo 高优先级事项 |
| 晚间待办提醒 | 读取 todo 未完成事项 + 总结 |

**修改命令**：
```bash
# 编辑任务 prompt
hermes cron edit <job-id> --prompt "新的 prompt 内容"

# 示例：史官记录增加写入 todo 步骤
hermes cron edit 728448c18c9c --prompt "作为 Brain OS 史官记录，扫描聊天记录并提取待办：

1. 扫描最近 2 小时的聊天记录
2. 提取实质性内容（决策/待办/技术讨论）
3. 提取待办事项，按优先级分类
4. 写入 todo-backlog.md（使用 kanban-sync.py --write-todo）
5. 输出提取摘要

工作目录：/root/.hermes/knowledge"
```

**完成标准**：
- ✅ 8 个生产者任务 prompt 包含"写入 todo"
- ✅ 5 个消费者任务 prompt 包含"读取 todo"
- ✅ cron/jobs.json 已更新

---

### P4: 技能绑定

**目标**：为关键任务绑定标准化技能

**绑定映射**：

| 任务 | 技能 | 理由 |
|------|------|------|
| 史官记录 | `chronicle-agent` | 标准化会话扫描流程 |
| 观察者自检 | `observer` | 标准化健康检查流程 |
| 知识库审计 | `llm-wiki` | 知识库审计/查询 |
| Lint | `llm-wiki` | 知识库格式检查 |
| 自动提交巡检 | `cron-git-state-monitoring` | git 状态监控 |
| 夜间文章整合 | `article-notes-integration` | 文章整合流水线 |
| 夜间对话挖掘 | `conversation-knowledge-flywheel` | 对话知识沉淀 |
| 夜间知识放大器 | `knowledge-flywheel-amplifier` | 跨源知识合成 |

**绑定命令**：
```bash
hermes cron edit <job-id> --add-skill <skill-name>

# 示例
hermes cron edit 728448c18c9c --add-skill chronicle-agent
hermes cron edit 3cda2159065c --add-skill observer
```

**完成标准**：
- ✅ 8 个核心任务绑定技能
- ✅ 技能绑定率 ≥ 60%

---

## 八、Kanban 管理层任务

**创建命令**：
```bash
hermes cron create "0 8 * * *" "作为 Brain OS Kanban 管理层，执行 Kanban 双向同步：

1. 运行 kanban-sync.py --read-todo --task kanban-manager
   - 读取 todo-backlog.md 中 open 状态的待办
   - 为每个待办创建 Kanban 卡片
   - 更新 todo 中的 Kanban 卡片字段

2. 检查 Kanban 卡片状态
   - 如果 Kanban 卡片已 resolved，运行 --update-todo 更新 todo 状态

3. 输出同步摘要
   - 新建卡片数量
   - 更新卡片数量
   - 同步失败项

工作目录：/root/.hermes/knowledge" --name "Brain OS Kanban 管理层" --deliver local --workdir /root/.hermes/knowledge
```

**调度**：0 8 * * *（每天早上 8 点）

**职责**：
- 将 todo 转换为 Kanban 卡片
- 状态变更时回写 todo
- 确保 Kanban 与 todo 同步

---

## 九、关键命令速查

```bash
# 查看 cron 任务
hermes cron list

# 编辑任务
hermes cron edit <job-id> --add-skill <skill-name>
hermes cron edit <job-id> --prompt "新 prompt"

# 创建新任务
hermes cron create "0 8 * * *" "prompt 内容" --name "任务名"

# 运行 kanban-sync.py
python3 scripts/kanban-sync.py --write-todo --task <task-name>
python3 scripts/kanban-sync.py --read-todo --task kanban-manager
python3 scripts/kanban-sync.py --update-todo --task kanban-manager

# 验证知识库结构
find /root/.hermes/knowledge -type d -name "*[一-龥]*"

# 查看 todo 状态
cat /root/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md
```

---

## 十、开源准备规范

### 10.1 定位原则

Brain OS 是**技能体系**而非独立系统，开源时应明确：

| 项目 | 正确表述 | 错误表述 |
|------|----------|----------|
| 定位 | "一套可组合的技能集合" | "独立系统/平台" |
| 灵感来源 | "OpenClaw git-backed brain 设计" | 不提或错误引用 |
| 依赖 | "全部为 Hermes 官方内置技能" | "需要额外安装 XX 系统" |

### 10.2 内容隔离

开源仓库**必须排除个人数据**：

```
.gitignore 排除：
- knowledge/00-raw/transcripts/    # 对话原始记录
- knowledge/01-entities/projects/  # 用户项目文件
- knowledge/09-personal-ops/       # 个人运营记录
```

**检查清单**：
- [ ] 无 Paperclip 相关内容（公司项目、TradeRisk、TrendRadar 等）
- [ ] 无红果短剧项目内容
- [ ] 无化工品贸易相关内容
- [ ] 无个人运营数据
- [ ] 所有路径参数化（使用环境变量）

### 10.3 部署简化

**错误做法**：复杂部署脚本、多步骤配置

**正确做法**：hermes 直接读取技能目录

```bash
# 方式一：克隆 + 配置技能路径
git clone <repo> ~/.hermes/brain-os
hermes config set skills.paths+=~/.hermes/brain-os/skills

# 方式二：直接复制技能
cp -r ~/.hermes/brain-os/skills/* ~/.hermes/skills/

# 方式三：环境变量
export HERMES_SKILLS_PATH=~/.hermes/brain-os/skills
hermes
```

### 10.4 参数化规范

所有硬编码路径必须参数化，支持环境变量：

```python
import os
from pathlib import Path

HERMES_ROOT = os.environ.get("HERMES_ROOT", str(Path.home() / ".hermes"))
HERMES_KNOWLEDGE = os.environ.get("HERMES_KNOWLEDGE", str(Path(HERMES_ROOT) / "knowledge"))
HERMES_TODO_PATH = os.environ.get(
    "HERMES_TODO_PATH",
    str(Path(HERMES_KNOWLEDGE) / "06-context" / "todo-tracking" / "todo-backlog.md")
)
```

**环境变量清单**：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_ROOT` | Hermes 根目录 | `~/.hermes` |
| `HERMES_KNOWLEDGE` | 知识库路径 | `$HERMES_ROOT/knowledge` |
| `HERMES_TODO_PATH` | Todo 文件路径 | `$HERMES_KNOWLEDGE/06-context/todo-tracking/todo-backlog.md` |

### 10.5 开源仓库结构

```
brain-os/
├── src/
│   └── kanban-sync.py          # 参数化同步工具
├── config/
│   └── jobs-template.json      # 任务配置模板
├── docs/
│   └── brain-os-architecture.md
├── scripts/
│   └── deploy.sh               # 简化部署脚本
├── README.md                   # 技能体系说明
├── LICENSE                     # MIT
├── .env.example                # 环境变量示例
└── .gitignore                  # Git 忽略规则
```

---

## 相关技能

- `llm-wiki` - 知识库架构规范
- `cronjob` - cron 任务管理
- `kanban` - Kanban 卡片管理
- `chronicle-agent` - 史官记录
- `observer` - Agent 观察者
- `article-notes-integration` - 文章整合
- `conversation-knowledge-flywheel` - 对话知识沉淀
- `knowledge-flywheel-amplifier` - 知识放大器
- `cron-git-state-monitoring` - git 状态监控

---

## 参考文档

- `references/brain-os-open-source-prep.md` - Brain OS 开源准备完整流程
- `references/kanban-sync-implementation.md` - kanban-sync.py 核心函数实现参考
- `references/todo-backlog-dirty-data-patterns.md` - todo-backlog 脏数据模式与修复策略
- `references/cron-path-update-pattern.md` - cron 任务路径更新模式（目录重构后批量更新路径引用）
- `references/daily-brief-generation.md` - 每日简报（驾驶舱）多源数据聚合生成模式
- `references/path-drift-pattern.md` - 技能文档路径漂移模式（wiki → knowledge 迁移后路径引用不一致）