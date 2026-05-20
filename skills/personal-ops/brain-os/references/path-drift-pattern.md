# 技能文档路径漂移模式

## 问题描述

定时任务技能的 SKILL.md 文档中同时保留了英文路径和中文路径，导致定时任务执行时按文档中的路径输出，产生中文目录。

## 根因分析

1. **wiki → knowledge 迁移**（2026-05-15）：知识库目录从 `03-知识库/` 迁移到 `04-知识库/`，但部分技能文档未完全更新
2. **备选路径模式**：技能文档中同时保留中英文路径作为"备选"，导致定时任务执行时可能输出中文路径
3. **文档更新滞后**：技能文档更新后未同步检查所有路径引用

## 受影响技能

| 技能 | 中文路径残留 |
|------|-------------|
| `article-notes-integration` | `03-知识库/`、`03-KNOWLEDGE/` |
| `conversation-knowledge-flywheel` | `04-知识库/99-系统/`、`04-知识库/01-阅读消化/` |
| `knowledge-flywheel-amplifier` | `04-知识库/99-系统/`、`04-知识库/01-阅读消化/` |

## 检测方法

```bash
# 查找所有中文目录
find /root/.hermes/knowledge -type d -name '*[一-龥]*'

# 检查技能文档中的路径引用
grep -r "03-知识库\|04-知识库\|99-系统" /root/.hermes/skills/article-notes-integration/
grep -r "04-知识库\|99-系统" /root/.hermes/skills/conversation-knowledge-flywheel/
grep -r "04-知识库\|99-系统" /root/.hermes/skills/knowledge-flywheel-amplifier/
```

## 修复步骤

1. **统一技能文档路径**：将所有路径引用改为英文（`99-system/`、`04-queries/`）
2. **移除备选路径说明**：不要同时保留中英文路径
3. **清理已生成目录**：删除已生成的中文目录
4. **验证 cron 输出**：确认下次 cron 运行输出到正确路径

## 预防规范

- 技能文档中路径引用必须与实际系统结构一致
- 迁移后必须 grep 检查所有技能文档中的路径引用
- 不要同时保留中英文路径作为"备选"
- 文档中的路径示例必须可运行

## 统一路径规范

| 组件 | 正确路径 |
|------|----------|
| 知识库根目录 | `/root/.hermes/knowledge/` |
| 文章整合报告 | `99-system/03-integration-reports/YYYY-MM-DD/` |
| 对话挖掘报告 | `99-system/03-integration-reports/YYYY-MM-DD/` |
| 放大器报告 | `99-system/03-integration-reports/YYYY-MM-DD/` |
| 夜间摘要 | `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md` |
| 主题索引 | `99-system/01-indexes/` |
