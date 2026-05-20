# Lint → Kanban 闭环工作流

> 将知识库 Lint 发现的问题自动创建为 Kanban 卡片，形成修复闭环。

## 核心架构

```
周一 02:00 → Lint 执行
              ↓
         生成 lint-report
              ↓
         解析问题统计
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
新问题 → 创建 Kanban 卡片   已有问题 → 更新状态
    ↓                   ↓
更新 issues-tracker    检查是否已修复
    ↓
发送 Telegram 通知
```

## 关键文件

| 文件 | 用途 |
|------|------|
| `scripts/lint-to-kanban.py` | Lint → Kanban 集成脚本 |
| `scripts/fix-knowledge-issues.py` | 自动修复脚本（断链、frontmatter） |
| `lint-reports/issues-tracker.md` | 问题追踪器 |
| `lint-reports/lint-report-*.md` | Lint 报告 |

## 使用方式

**手动执行 Lint → Kanban 同步：**
```bash
python3 ~/.hermes/scripts/lint-to-kanban.py --wiki ~/.hermes/knowledge
```

**预览模式（不实际创建卡片）：**
```bash
python3 ~/.hermes/scripts/lint-to-kanban.py --wiki ~/.hermes/knowledge --dry-run
```

**自动修复断链：**
```bash
python3 ~/.hermes/scripts/fix-knowledge-issues.py --wiki ~/.hermes/knowledge --fix broken-links
```

**自动修复 frontmatter：**
```bash
python3 ~/.hermes/scripts/fix-knowledge-issues.py --wiki ~/.hermes/knowledge --fix frontmatter
```

## 闭环机制

1. **问题追踪持久化** — `issues-tracker.md` 记录所有问题状态（open/in_progress/resolved/wontfix）
2. **Kanban 卡片自动创建** — P0/P1 问题自动创建为卡片，分配给 `knowledge-ops`
3. **状态同步** — 下次 lint 执行时对比追踪器，更新卡片状态
4. **修复闭环** — 问题修复后，卡片标记完成，追踪器更新为 `resolved`
5. **升级提醒** — P0 问题连续 2 次 lint 未修复 → 升级提醒

## 优先级映射

| Severity | Kanban Priority | 说明 |
|----------|-----------------|------|
| P0 | 1 (high) | 立即修复（断链、缺失 frontmatter） |
| P1 | 2 (medium) | 本周内（孤立页面） |
| P2 | 3 (low) | 长期优化（超大页面） |

## 通知渠道

**重要：** Lint 和审计任务使用 **Telegram** 推送（避免微信限流）。

| 任务 | 推送渠道 | Chat ID |
|------|----------|---------|
| 周一知识库 Lint | Telegram | <YOUR_TELEGRAM_CHAT_ID> |
| 每周知识库审计 | Telegram | <YOUR_TELEGRAM_CHAT_ID> |

## 常见问题

### Q: 为什么报告之前没发送？

A: 所有 cron 任务的 `delivery_mode` 都是 `None`，报告生成了但没人看到。解决方案：
- Lint 和审计任务改为 Telegram 推送
- 时间分散（01:30 审计 → 02:00 Lint），避免限流

### Q: 如何验证卡片创建成功？

A: `hermes kanban list` 查看待处理卡片，`hermes kanban show <id>` 查看详情。

### Q: 自动修复脚本安全吗？

A: 支持 `--dry-run` 预览模式，先预览再执行。断链修复通过模糊匹配，不会破坏现有链接。

## 实施时间线

**2026-05-18**: 首次实施
- 创建 `lint-to-kanban.py` 和 `fix-knowledge-issues.py`
- 设置 Telegram 推送渠道
- 创建 4 个 Kanban 卡片（P0: 2, P1: 1, P2: 1）
- 建立 `issues-tracker.md` 追踪器
