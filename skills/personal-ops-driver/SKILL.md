---
name: personal-ops-driver
description: >
  Alex个人事务管理执行技能。用于个人事务收件、待办/提醒/跟进项记录、backlog 状态更新、daily briefing 管理、当前承诺事项整理、00-INBOX/01-PERSONAL-OPS 分层治理。Use when: personal ops, daily briefing, todo management, commitment tracking, life management, 00-INBOX/01-PERSONAL-OPS governance. 遇到个人事务管理、排序、提醒、承诺跟踪、驾驶舱维护等请求时，应主动使用本技能。
---

# Personal Ops Driver

> Alex个人事务管理技能（标准化版）

## 适用场景

当任务明显属于以下任一类时，优先使用本 skill：
- 个人事务收件
- 待办 / 提醒 / 跟进项记录
- backlog 状态更新
- daily briefing 管理
- 当前承诺事项整理
- 个人事务体系结构调整
- 00-INBOX / 01-PERSONAL-OPS 分层治理
- **周计划生成**（自动驾驶舱简报 + 项目进度 + 待办 → 周计划文档）

## 使用方式

本 skill 本身只保留：
- 任务入口判断
- 最小执行规则
- references 导航

**不要把全部方法论硬塞进 SKILL.md。**
遇到个人事务任务时，先读本 skill，再按需要读取下列 references 文件。

## 必读 references（默认）

1. 执行基线：
- `./references/operating-model.md`

2. references 导航：
- `./references/reference-map.md`

3. 脏数据模式识别（必读）：
- `./references/todo-backlog-dirty-data-patterns.md`

4. 当前真相源（生产环境路径）：
- `/root/.hermes/knowledge/03-个人运营/03-待办跟进/todo-backlog.md`

> ⚠️ **路径说明**：生产 vault 路径为 `/root/.hermes/knowledge/`，前缀为 `03-个人运营/`。引用文件中的 `/tmp/brain-os-test/vault/` 前缀和 `01-PERSONAL-OPS/` 前缀属于早期测试 vault 结构，实际路径以 `03-个人运营/` 为准。

## 按需读取 references

### A. 方法论 / 哲学层
当需要判断轻重缓急、节奏、取舍时，读取：
- `./references/personal-ops-philosophy.md`
- `./references/personal-priority-rules.md`

### B. 决策锚点
当需要确认这套系统已经拍板过什么，读取：
- `/root/.hermes/knowledge/05-系统配置/log.md`
- `./references/reference-map.md`

### C. 历史证据源
当需要回查原始说法、语义变化、频道上下文时，读取：
- `/root/.hermes/knowledge/03-个人运营/05-频道历史/`

注意：
- 它是证据源，不是当前状态真相源

## 周计划生成工作流

当任务为「生成周计划」（如 cron job personal-ops-weekly-plan），执行以下流程：

### 数据源读取顺序

1. **上周周计划** → `03-个人运营/02-计划日程/周计划-YYYY-第N周.md`
2. **最近7天每日简报** → `03-个人运营/01-每日简报/YYYY-MM-DD.md`
3. **项目进度文件** → `01-项目/` 下的 PROJECT.md / PROGRESS.md（重点关注近期活跃项目）
4. **待办积压** → `03-个人运营/03-待办跟进/todo-backlog.md`
5. **月度里程碑提示词** → `05-系统配置/提示词/personal-ops-monthly-milestones.prompt.md`
6. **工作产出** → `02-工作产出/` 下的近期待归档报告

### 文档结构（固定格式）

```
# 周计划 2026 第 N 周 (MM/DD - MM/DD, 2026)

## 一、上周完成任务回顾

### ✅ 已完成任务
- 逐项列出，标注完成时间
- 关键成果用 📊 单独归纳
- 遗留问题用 ⚠️ 标记

**格式要点**：
- 每项任务用 **粗体标题** + 描述 + 完成时间
- 关键成果：完成率、里程碑、量化指标
- 遗留问题：表格形式（问题 | 严重度 | 说明），严重度用 🔴🟡⚪️

### 二、本周核心目标与优先级

优先级分级体系：
- **🔴 P0 — 紧急修复**：系统异常、阻断性问题
- **🔴 P1 — 核心项目推进**：主线业务/项目任务
- **🟡 P2 — 重要推进**：日常运维、后续跟进
- **🟢 P3 — 低优先级**：备选优化事项

每条目标带明确的任务列表和验收标准。

### 三、本周待办列表

表格格式：

| 优先级 | 待办事项 | 计划完成时间 | 状态 |
|--------|----------|--------------|------|
| 🔴 P0 | 任务描述 | YYYY-MM-DD | ⏳ 待开始 |

### 四、计划摘要

- **周期**: 2026 年第 N 周 (YYYY-MM-DD 至 YYYY-MM-DD)
- **本周主题**: 一句话主题
- **本周主要矛盾**: 本周需应对的核心冲突或挑战
- **核心里程碑**: 2-3个可验证的里程碑
- **当前待办积压**: N 项
```

### 输出路径

```
03-个人运营/02-计划日程/周计划-YYYY-第N周.md
```

### git 提交

```bash
cd /root/.hermes/knowledge
git add "03-个人运营/02-计划日程/周计划-YYYY-第N周.md"
git commit -m "chore(personal-ops): refresh weekly plan for YYYY-Www"
```

### 周数计算
- 使用 ISO 周数（`date -d "YYYY-MM-DD" "+%V"`）
- 每周一为本周第一天

### ⚠️ 常见陷阱
- 不要省略上周遗留问题 — 未修复的问题需在新的本周计划中接力
- 优先级标签保持统一：P0/P1/P2/P3 对应 🔴P0 / 🔴P1 / 🟡P2 / 🟢P3
- 计划完成时间按工作日分配，P0/P1 安排在前，P3 安排在周末
- 待办列表当前为空时，在计划摘要中标注"待办积压：0项"

## 核心原则

1. **`03-个人运营/03-待办跟进/todo-backlog.md` 是个人事务唯一真相源（SSoT）**
2. **`03-个人运营/` 全部视为从待办派生出的操作视图与整理层**
3. 新事项、状态变化、提醒、承诺更新，默认先落 `todo-backlog.md`
4. `05-频道历史/` 是证据源，不是当前状态真相源
5. 过往 `每日简报` 应归档，不应直接覆盖到历史消失
6. 不允许私自删除事项；只有用户明确说"已完成/可归档"才允许移出主面
7. **每日简报生成前必须检查 todo-backlog 脏数据** — 重复/碎片化条目需标注并建议清理

## 最小执行动作

### 0. 每日简报生成前检查（新增）

在生成每日简报前，必须执行以下检查：

1. **脏数据检测**: 读取 `references/todo-backlog-dirty-data-patterns.md`，识别重复/碎片化条目
2. **Kanban 同步验证**: 运行 `hermes kanban list --status open`，对比 todo-backlog 中的 open 数量
3. **目录结构验证**: 确保 `03-个人运营/01-每日简报/` 目录存在

### 1. 收到新事项
- 先判断是否应进入 `todo-backlog.md`
- 补全：优先级、领域、截止、下一动作、是否必须本人、是否可委派、状态
- 必要时再同步派生视图

### 2. 收到状态变化
- 先更新 `todo-backlog.md`
- 再决定是否同步 `每日简报` / `周计划` / 其他派生视图

### 3. 收到"提醒我"
- 写成明确提醒型事项
- 需要写清时间窗口或触发条件

### 4. 收到"已完成"
- 将 backlog 条目标记为 `已完成`
- 保留结果说明
- 暂不立即删除

### 5. 生成周计划（cron job 模式）
- 见上文「周计划生成工作流」章节
- 本周回顾基于过去7天每日简报 + 项目 PROGRESS 文件
- 本周目标需继承上周遗留问题
- 输出格式严格遵循 P0-P3 优先级框架

## 查询顺序

1. `03-个人运营/03-待办跟进/todo-backlog.md`
2. `03-个人运营/05-频道历史/`
3. `03-个人运营/` 其他派生视图（每日简报/周计划）
4. `01-项目/` 下的活跃项目进度文件
5. `05-系统配置/` 下的提示词和配置
6. 方法论与决策 references
7. 相关项目/上下文文件

## 当前执行基线

在本 skill 与其他旧散落规则冲突时，优先级如下：
1. 用户最新明确指令
2. `references/operating-model.md`
3. skill 下的 `references/` 文档
4. Brain 中的决策锚点与历史证据
5. 本 SKILL.md

---

### ⚠️ Pitfalls（已知陷阱）

### P1. Todo Backlog 脏数据

**现象**: `todo-backlog.md` 中存在大量重复/碎片化条目，导致：
- 阻塞项统计虚高（如 21 条实际仅 8 条有效）
- 日报/周报质量下降（重复内容干扰优先级判断）

**常见模式**:
- **重复记录**: 同一问题被史官在不同日期重复记录（如 LLM Wiki 相关 ×9 次）
- **碎片化**: 同一问题拆分成多条（如 WebUI 构建超时拆成 5 条）
- **状态滞后**: 已解决的问题未标记 `resolved`

**检测**: 生成日报前运行脏数据检测（见 `references/todo-backlog-dirty-data-patterns.md`）

**修复**: 合并重复条目，标记已解决条目，清理碎片化记录

### P2. 待办未验证即执行

**现象**: 直接根据史官/观察者提取的待办创建 Kanban 卡片并执行，但部分问题可能已在项目过程中自动解决。

**风险**:
- 浪费资源执行已解决的问题
- 用户需要手动清理无效卡片
- 降低系统可信度

**⚠️ 核心原则**: **处理待办前必须先验证问题是否仍存在**

**验证工作流**（见 `references/todo-validation-workflow.md`）：

| 步骤 | 操作 | 工具 |
|------|------|------|
| 1 | 检查系统状态（Gateway、Telegram、钉钉等） | `hermes status`, `systemctl status` |
| 2 | 检查文件/目录是否存在 | `ls`, `find` |
| 3 | 检查配置是否存在 | `grep`, `cat` |
| 4 | 对比当前计数 vs 原始计数 | `grep -c`, `wc -l` |
| 5 | 分类结果：✅已解决 / 🟡部分解决 / 🔴仍存在 | 人工判断 |

**分类标准**：
- ✅ **已解决**: 问题已修复，无需处理
- 🟡 **部分解决**: 有改善但未完全解决，需确认
- 🔴 **仍存在**: 问题仍存在，需要真实处理

**⚠️ 用户偏好**: 用户明确要求"处理前先核验证该待办问题是否还存在"，这是第一优先级规则。

### P2. Kanban 与 Todo 不同步

**现象**: `hermes kanban list --status open` 返回空，但 `todo-backlog.md` 中有多个 open 条目

**原因**: kanban-sync.py 的 `--read-todo` 模式未定期运行，或生产者直接绕过 todo 写入 Kanban

**检测**:
```bash
# 对比 todo 和 Kanban 的 open 数量
grep -c "| open |" todo-backlog.md
hermes kanban list --status open | wc -l
```

**修复**: 定期运行 `kanban-sync.py --read-todo`，确保 todo → Kanban 同步

### P3. 每日简报目录缺失

**现象**: `03-个人运营/01-每日简报/` 目录不存在，导致无法写入日报

**检测**: 生成日报前检查目录是否存在

**修复**: 创建目录 `mkdir -p 03-个人运营/01-每日简报/`
