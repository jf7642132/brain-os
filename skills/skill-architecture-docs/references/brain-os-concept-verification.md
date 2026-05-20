# Brain OS 概念验证记录

> 记录在 Brain OS 文档编写过程中发现的概念验证问题，避免重复犯错。

## OpenClaw "git-backed brain" 术语验证

**问题**：README 中声称"灵感来源于 OpenClaw 的 git-backed brain 设计"，但用户搜索后发现该术语不存在于 OpenClaw 官方文档。

**调查结果**：

| 来源 | 发现 |
|------|------|
| OpenClaw 官方 GitHub | 有 21k+ 关注者，但无 "git-backed brain" 术语 |
| Helm chart `openclaw-with-brain` | 社区/第三方实现，非官方 |
| Reddit `clawbrain` 项目 | 社区项目，非官方 |
| OpenClaw 官方文档 | 使用 "workspace"、"git sync" 等表述 |

**结论**："git-backed brain" 不是 OpenClaw 官方术语，是社区/第三方实现的概念。

**修正**：
- 原表述：`OpenClaw 的 git-backed brain 设计`
- 修正后：`OpenClaw 的 git 驱动持久化设计`（将 agent 的 memory、config、workspace 存储在 git 仓库中实现持久化和多实例共享）

## Brain OS 架构核心概念验证

### 统一任务入口

**错误理解**：Kanban 是大脑中枢，调度所有任务

**正确理解**：
- **todo-backlog.md 是统一任务入口** — 生产者写入，消费者读取
- **Kanban 是可视化界面** — 与 todo 双向同步，非调度中心
- **定时任务由 cron 调度** — 非 Kanban

### 消费者定义

**错误理解**：消费者是 5 个抽象概念（知识检索/任务执行/决策支持/技能调用/上下文管理）

**正确理解**（Brain OS 特定）：
- 消费者是 **3 个真实任务**：每日早报、每周计划、月度总结
- 消费者从 `todo-backlog.md` 读取，不是从 `knowledge/` 读取

### 目录命名冲突

**问题**：`02-concepts/personal-ops/` 和 `09-personal-ops/` 同名，容易混淆

**修正**：
- `02-concepts/ops/` — 运营概念（公开知识）
- `09-personal-data/` — 个人数据（不公开，gitignore 排除）

## 概念验证检查清单

在文档中声称"灵感来源于 X 项目"时：

1. ✅ 搜索官方文档确认术语存在
2. ✅ 搜索 GitHub Issues/PRs 确认术语使用
3. ✅ 如是社区实现，明确标注"社区/第三方实现"
4. ✅ 使用准确描述，避免臆造术语

## 相关资源

- OpenClaw 官方：https://github.com/openclaw/openclaw
- OpenClaw 文档：https://docs.openclaw.ai
- Helm chart（社区）：https://artifacthub.io/packages/helm/openclaw-with-brain/openclaw-with-brain
