# 知识库 Lint 基线报告 — 2026-05-18

> 首次完整 lint 扫描结果，用于后续对比趋势。

## 扫描范围

- **知识库路径**: `/root/.hermes/knowledge`
- **文件总数**: 506 个 Markdown 文件
- **总内容量**: ~1.9MB (65,554 行)

---

## 问题汇总

| 严重度 | 问题类型 | 数量 | 说明 |
|--------|----------|------|------|
| 🔴 P0 | 缺失 YAML frontmatter | 443 | 无法结构化搜索、筛选、staleness 检测 |
| 🔴 P0 | 断链 (broken links) | 54 | 主要是 index.md 中的 wikilinks 指向不存在的文件 |
| 🔴 P0 | 孤立页面 (orphan pages) | 464 | 无入链页面，知识孤岛 |
| 🟡 P1 | 超大页面 (>200 行) | 80 | 主要是红果短剧 episode 脚本，属正常产出 |

---

## 断链详情

**主要来源**: `index.md` 中的大量 wikilinks

**典型断链模式**:
- 文件名大小写不匹配
- 文件名含空格/特殊字符，链接中未正确编码
- 文件已移动/重命名，链接未更新

**可自动修复比例**: ~75% (38/54)
- 可通过模糊匹配（忽略大小写、空格、连字符）找到正确文件

---

## Frontmatter 缺失详情

**分布**:
- `00-收件箱/`: 大部分临时收集文件无 frontmatter
- `01-项目/`: 部分项目文档缺失
- `04-知识库/`: 大量阅读消化笔记缺失
- `05-系统配置/`: 提示词模板、cron 配置等系统文件（可豁免）
- `99-系统/`: 日志、报告等（可豁免）

**优先级**:
1. `index.md` — 核心导航文件，必须添加
2. `SCHEMA.md` — 架构定义文件，必须添加
3. 项目文档 (PROJECT.md, PROGRESS.md)
4. 概念页、实体页

---

## 孤立页面分析

**464 个孤立页面构成**:
- 系统文件 (cron 配置、提示词模板): ~50 个 — 可豁免
- 日志文件 (daily logs, observer 记录): ~100 个 — 可豁免
- 项目子文件 (episode 脚本、原始素材): ~200 个 — 可豁免
- **重要业务页面**: ~114 个 — 需要添加入站链接

**修复建议**:
- 在 `index.md` 中为重要页面添加索引条目
- 在相关页面间建立交叉引用
- 系统文件和临时文件可豁免

---

## 修复优先级

### P0 - 立即修复

| ID | 问题 | 修复方式 | 预计工作量 |
|----|------|----------|------------|
| FM-001 | index.md 缺失 frontmatter | 手动添加 | 5 分钟 |
| BL-001 | 54 个断链 | 自动修复脚本 | 10 分钟 |

### P1 - 本周内

| ID | 问题 | 修复方式 | 预计工作量 |
|----|------|----------|------------|
| FM-002 | 重要页面缺失 frontmatter | 批量脚本 + 手动 | 1-2 小时 |
| OR-001 | 重要页面孤立 | 手动添加入站链接 | 1-2 小时 |

### P2 - 长期优化

| ID | 问题 | 修复方式 | 预计工作量 |
|----|------|----------|------------|
| SIZE-001 | 超大页面 | 拆分或添加摘要 | 持续优化 |

---

## 修复工具

### 断链修复

```bash
# 预览修复
python3 ~/.hermes/scripts/fix-knowledge-issues.py \
  --wiki /root/.hermes/knowledge --fix broken-links --dry-run

# 应用修复
python3 ~/.hermes/scripts/fix-knowledge-issues.py \
  --wiki /root/.hermes/knowledge --fix broken-links
```

### Frontmatter 批量添加

```bash
# 预览（dry run）
python3 ~/.hermes/scripts/fix-knowledge-issues.py \
  --wiki /root/.hermes/knowledge --fix frontmatter --dry-run

# 应用修复
python3 ~/.hermes/scripts/fix-knowledge-issues.py \
  --wiki /root/.hermes/knowledge --fix frontmatter
```

---

## 趋势追踪

| 日期 | 文件数 | 断链 | 孤立 | 缺失 FM | 超大页面 |
|------|--------|------|------|---------|----------|
| 2026-05-18 | 506 | 54 | 464 | 443 | 80 |
| 2026-05-25 | - | - | - | - | - |
| 2026-06-01 | - | - | - | - | - |

> 下次 lint: 2026-05-25 (周一 02:00)

---

*报告生成: 2026-05-18 14:52*
*执行脚本: wiki-lint.py*