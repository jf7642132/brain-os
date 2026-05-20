---
title: Verified Knowledge Base Paths
created: 2026-05-20
updated: 2026-05-20
type: reference
---
# 验证过的知识库路径 (2026-05-20)

> 本文件记录实际验证过的路径，避免技能文档中的路径假设错误。

## 系统级路径 (English naming)

| 用途 | 实际路径 | 验证状态 |
|------|---------|---------|
| 文章整合报告 | `99-system/03-integration-reports/YYYY-MM-DD/` | ✅ 验证 |
| 对话挖掘报告 | `99-system/03-integration-reports/YYYY-MM-DD/` (同目录) | ✅ 验证 |
| 集成报告输出 | `99-system/03-集成报告/YYYY-MM-DD/` | ✅ 验证 (中文别名) |
| 索引目录 | `99-system/01-indexes/` | ✅ 验证 |
| 追踪器 | `99-system/trackers/` | ✅ 验证 |
| 频道历史 | `09-personal-ops/05-channel-history/` | ✅ 验证 |

## 知识库路径 (Chinese naming)

| 用途 | 实际路径 | 验证状态 |
|------|---------|---------|
| 夜间摘要 | `04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-YYYY-MM-DD.md` | ✅ 验证 |
| 放大器报告 | `04-知识库/99-系统/03-集成报告/YYYY-MM-DD/` | ✅ 验证 |
| 主题知识 | `04-知识库/01-阅读消化/02-主题知识/` | ⚠️ 未验证存在 |
| 项目文档 | `01-entities/projects/` | ✅ 验证 |

## 双重位置 (需小心)

| 内容 | 主位置 (当前) | 旧位置 (历史) | 说明 |
|------|-------------|-------------|------|
| 夜间摘要 | `04-知识库/01-阅读消化/04-摘要汇总/` | `04-queries/daily/04-summary/` | 旧位置包含4月及5月初的旧数据 |
| 文章整合 | `99-system/03-integration-reports/` | `04-queries/daily/02-article-integration/` | 旧位置可能仍有数据 |

## 验证命令

```bash
# 检查实际目录结构
ls -la /root/.hermes/knowledge/

# 查找旧路径引用
grep -r "03-知识库" /root/.hermes/skills/ 2>/dev/null | head -20

# 检查频道历史文件
ls /root/.hermes/knowledge/09-personal-ops/05-channel-history/

# 检查集成报告
ls /root/.hermes/knowledge/99-system/03-integration-reports/
```

## 命名约定总结

- **系统级目录** (99-system, 09-personal-ops, 01-entities): 使用英文命名
- **知识库目录** (04-知识库, 01-阅读消化): 使用中文命名
- **混合情况**: `04-知识库/99-系统/` 是中文别名，实际指向 `99-system/`

**建议**: 始终使用 `ls` 验证路径，不要假设命名一致性。