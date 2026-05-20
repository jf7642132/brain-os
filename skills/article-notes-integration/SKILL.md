---
name: article-notes-integration
description: >
  Nightly pipeline for integrating newly captured external article notes into
  Brain knowledge surfaces. Use when: 文章整合, article notes integration,
  nightly article sync, update article relations, topic index update,
  article knowledge graph, 前一天文章整理, 或 run the 02:00 article pipeline.
---

# Article Notes Integration

把前一天新增或待整合的 Article Notes，转成可检索、可关联、可继续提炼的 Brain 知识输入层。

## Purpose

这个技能负责 **文章 ingestion 之后的 nightly integration**，而不是原始外部文章采集本身。

它处理的是：
1. 扫描昨天新增或尚未 integrated 的 article notes
2. 校验并补足结构 / frontmatter / relation 状态
3. **交叉引用更新**（见下方 Cross-Reference Protocol，每次 ingest 后执行）
4. 更新 topic / domain / project 相关的轻量图谱入口
5. 生成 open questions / pattern candidates / article-derived graph signals
6. 输出高价值 article candidates，供后续 flywheel amplification 使用

## Primary Inputs

- Brain root: `{{BRAIN_ROOT}}` (default: `/root/.hermes/knowledge`)
- Source notes: **Multiple possible locations** (see "Knowledge Base Structure Variations" below):
- `00-raw/articles/` — raw article references
  - `02-concepts/<domain>/01-article-notes/` — domain-specific article notes
  - `04-queries/daily/02-article-integration/` — daily integration queue
  - `99-system/01-indexes/` 下已有 topic / topic-map / open-question surfaces
  - `05-outputs/` 下 project briefs（若能稳定识别项目）

## Required Outputs

A successful run should produce some or all of:
- 1 machine-facing run report → `99-system/03-integration-reports/YYYY-MM-DD/article-integration-report-YYYY-MM-DD.md`
- 1 human-facing digest section append → `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md`
- article note frontmatter / relation field updates
- topic index / topic map updates when justified
- open question / pattern candidate markers when justified
- high-value article candidates for the 04:00 amplifier stage
- Brain git commit + post-commit visibility confirmation

## What This Skill May Read

- Article notes themselves (from any of the source directories listed above)
- Existing Brain knowledge / indexes / project briefs
- Existing relation fields and topic surfaces

## What This Skill May Write

- Article note metadata and relation fields
- Lightweight graph/index surfaces in `99-system/01-indexes/`
- Candidate-only pattern / open-question surfaces
- Integration reports in `99-system/03-integration-reports/`

## Raw Asset Storage Rule（2026-04-13）

这个 skill 必须严格区分：

### 正式知识层（可提交 Git）
- 提炼后的文章 note `.md`
- relation / topic / open-question / digest / report 等结构化产物

### 原始抓取层（默认不提交 Git）
- 微信/小红书抓下来的整套图片
- OCR 图包
- 原始 PDF / EPUB / Office 附件
- debug html
- `.raw/` / `raw/` 响应
- 任何可再抓取或可再生成的中间素材

### 默认本地落点
统一放到：
- `LOCAL-LARGE-FILES/knowledge-sources/`

例如：
- `LOCAL-LARGE-FILES/knowledge-sources/ai-agent/2026-04-12-harness-survey/`

### 禁止事项
- 不要把 `_images-*`、`images/`、`.raw/`、原始 PDF 当作正式知识产物提交到 Brain Git
- 不要为了“资料完整”把整包截图/附件塞进 `03-KNOWLEDGE/`
- 如果正文需要引用原始资产，只在 note 中写来源链接或本地路径说明

## Cross-Reference Protocol（每次 ingest 后执行）

每次处理文章落库后，按以下步骤执行交叉引用：

### Step 1：topic-map 更新
- 读取文章 frontmatter 的 `topic` 字段
- 打开 `99-system/01-indexes/topic-map.md`
- **⚠️ 若文件不存在**: 先创建文件，写入 frontmatter 和基础结构，再创建第一个 topic entry
  ```markdown
  ---
  title: Topic Map
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: index
  ---
  # Topic Map
  
  知识图谱主题索引，记录各主题下的文章来源与交叉引用关系。
  
  ---
  
  ## <topic-name>
  
  > <description>
  
  ### Sources
  
  | 文章 | 摘要 | 来源标记 |
  |------|------|----------|
  | [[<filename>]] | <summary> | `article-derived` |
  ```
- 若该 topic 已有 entry：在其下追加该文章作为新 source（含文件名、一行摘要、来源标记 `article-derived`）
- 若该 topic 不存在：在文件末尾创建新 entry（含 topic 名、一行说明、首个 source）
- 保守原则：每次仅追加小块增量，不重写整页

### Step 2：related_notes 双向链接
- 分两层扫描候选：
  1. 所有 article notes 目录中的原始相关文章
  2. 对应 domain 目录（如 `02-concepts/AI-Agent/`、`02-concepts/AI-Workflow/`）中的提炼页 / pattern 页
- 计算 topic 字段交集 + tags 字段交集
- 交集 ≥ 2：自动在双方 `related_notes` 字段互相追加对方的 `[[文件名]]`（不含扩展名）
- 交集 = 1：标记为候选，列入 integration report，不自动写入
- 不跨 domain 强加关联；若 domain 不明确，先只在 Article-Notes 层做比较

### Step 3：open-questions 追加
- 阅读文章内容，识别文章中提出但未解答的问题（"未来工作"/"开放问题"/"值得探讨"等线索词）
- 若发现有价值的未解答问题，追加到 `99-system/01-indexes/open-questions.md`
- 每条格式：`- [article-derived] 问题描述 → 来源：[[文章文件名]]`
- 若文章无明显 open questions，skip 此步骤

### Step 4：Consume latest lint report（不再重复执行）
- 若 `99-system/lint-reports/` 下存在最近 24 小时内的 lint 报告，可读取其摘要作为 integration 的参考上下文
- 若最新 lint 报告含 🔴 级问题，在 integration report 中单独标注
- 本 skill **不再主动执行 lint**；知识库 lint 由独立的 `knowledge-lint-weekly` job 负责，避免重复运行
- **⚠️ 路径注意**: 旧版技能文档可能引用 `12-REVIEWS/KNOWLEDGEBASE/`，但实际路径为 `99-system/lint-reports/`

## File Discovery Pattern for 24-Hour Window

When scanning for articles updated in the last 24 hours:

1. **Use epoch-based comparison** (more reliable than `-mmin` or `-mtime`):
   ```bash
   window_start=$(date -d "24 hours ago" +%s)
   find /path/to/article-notes -name "*.md" -type f -exec stat --format='%Y %n' {} \; | \
     while read mtime path; do
       if [ "$mtime" -ge "$window_start" ]; then echo "$path"; fi
     done
   ```

2. **Cross-reference with known pipeline times**:
   - Check if file timestamps align with known cron run times
   - If all files are older than 24 hours, verify the pipeline is running correctly
   - Note: File modification times may be set to historical dates during batch operations

3. **Check multiple directories** (adapt based on knowledge base structure):
   - English-style:
     - `00-raw/articles/`
     - `02-concepts/<domain>/01-article-notes/`
     - `04-queries/daily/02-article-integration/`
- `04-queries/daily/02-article-integration/`

### Discovery Commands
```bash
# Find all article-related directories
find /root/.hermes/knowledge -type d \( -name "*article*" -o -name "*文章*" \) 2>/dev/null

# Find all integration-related directories
find /root/.hermes/knowledge -type d \( -name "*integration*" -o -name "*整合*" \) 2>/dev/null
```

4. **When no new articles found**:
   - Report the last known update time from existing files
   - Note if this is unusual for the pipeline
   - Check if user activity patterns explain the gap

## Success Criteria

A run is successful when:
- new or pending article notes are normalized enough to participate in Brain retrieval
- relation/index updates happen only when there is real incremental signal
- no duplicate truth source is created
- Brain changes are committed
- resulting files are Obsidian-visible

## Failure / Degraded Mode

- **No new notes found** → emit a clear no-op report; do not force changes
  - Write a digest section explaining the empty state
  - Note the last known article update time for context
  - Flag if empty state persists >7 days (potential pipeline issue)
  - Response: `[SILENT]` if truly nothing to report, or minimal summary if context needed
- **Conflicting metadata** → mark for review, avoid pretending integration is complete
- **Index update would be no-op** → report that nothing meaningful changed
- **One note fails** → keep batch going; report the failed note separately

## Pitfalls & Known Issues

### P1: Index files don't exist
The skill assumes `topic-map.md` and `open-questions.md` exist in `99-system/01-indexes/`. If they don't, **create them** with proper frontmatter and structure before adding entries. Do not skip this step.

### P2: Lint report path outdated
Old documentation references `12-REVIEWS/KNOWLEDGEBASE/` but actual path is `99-system/lint-reports/`. Always verify with `find` before assuming.

### P3: Digest path variations
The nightly digest location varies by implementation:
- **Default**: `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md`
- **Alternative**: `05-outputs/nightly-digest/trade-risk-alert/` (for trade-risk-alert specific)

Always scan for existing digest files before creating new ones.

### P4: Kanban sync for todo tracking
When findings require human follow-up, use the kanban-sync.py pattern:
1. Write findings to `/tmp/article-integration-findings-YYYYMMDD.md`
2. Run `python ~/.hermes/scripts/kanban-sync.py --write-todo --task article-integration --output /tmp/article-integration-findings-YYYYMMDD.md`
3. Script auto-parses issues, generates todo IDs, writes to todo-backlog.md
4. For P0 issues, also create Kanban cards

**Do not edit todo-backlog.md directly** — always use kanban-sync.py as the single writer.

> 📚 See `references/kanban-sync-pattern.md` for detailed usage patterns and common findings templates.

### P5: Article backlog accumulation
If article notes accumulate without integration for >7 days, flag in the integration report and suggest:
1. Manual review of backlog
2. Checking upstream data pipeline health
3. Archiving stale content if no longer relevant

### Empty State Handling Pattern

When scanning for articles in the last 24 hours:

1. **File discovery with epoch comparison** (more reliable than `-mmin`):
   ```bash
   # Get current epoch boundaries for 24-hour window
   current_epoch=$(date +%s)
   window_start=$((current_epoch - 86400))  # 24 hours ago in seconds
   
   # Find files and filter by epoch time
   find /path/to/article-notes -name "*.md" -type f -printf '%T@ %p\n' | \
     awk -v start="$window_start" '$1 > start {print $2}'
   ```

2. **Alternative: Direct epoch comparison with stat**:
   ```bash
   window_start=$(date -d "24 hours ago" +%s)
   find /path/to/article-notes -name "*.md" -type f -exec sh -c '
     ts=$(stat -c %Y "{}");
     if [ "$ts" -gt '"$window_start"' ]; then echo "{}"; fi
   ' \;
   ```

3. **Timestamp verification**: Cross-reference file modification times with current time:
   ```bash
   stat -c "%Y %n" file.md
   date +%s  # current epoch
   ```
   Calculate: `(current_epoch - file_epoch) / 3600` to get hours since modification

4. **Important caveat**: File modification times may be set to historical dates (e.g., when files are batch-created or restored). Always verify by:
   - Checking multiple files' timestamps together
   - Comparing against known pipeline run times
   - Using `find ... -printf '%T+ %p\n'` for human-readable timestamps

3. **Contextual analysis**: If empty, check:
   - Last known article update time (from most recent file)
   - Recent user activity patterns (engineering work vs. reading)
   - Whether pipeline configuration is intact

4. **Report format for empty state**:
   ```markdown
   ## 02:00 文章整合
   
   执行时间：YYYY-MM-DD HH:00
   扫描范围：00-raw/articles/（最近 24 小时）
   
   ### 📊 扫描结果
   
   **无新增/更新文章**。
   
   最近一次文章笔记更新为 YYYY-MM-DD HH:MM，距今已超过 24 小时。
   
   ### 📁 现有文章笔记清单
   
   | 文件名 | 创建日期 | 最后更新 | 类型 |
   |--------|----------|----------|------|
   | ... | ... | ... | ... |
   
   ### 🔍 分析
   
   1. **文章管道状态**: [brief observation about pipeline health]
   2. **文章类型分布**: [if relevant, note patterns in existing articles]
   3. **建议**: [if pipeline has been empty >7 days, suggest checking config]
   ```

5. **When to use [SILENT]**:
   - If the nightly digest file doesn't exist yet and there's truly nothing to add
   - If all stages (01:00, 02:00, 03:00, 04:00) are empty
   - When the user explicitly prefers silent delivery for no-op runs

6. **When to write minimal summary**:
   - If the nightly digest already exists and needs the 02:00 section filled
   - If the empty state is unusual (e.g., pipeline has been active before)
   - If context about recent user activity helps explain the empty state

## Anti-Scope

This skill must **not**:
- use raw coding transcripts as its primary input
- perform transcript mining / conversation synthesis
- run full external deep research by default
- create a parallel truth source outside Brain
- over-write stable knowledge surfaces just to appear active

---

### Knowledge Base Structure Variations

⚠️ **Pitfall**: Different knowledge base implementations may use different directory structures. The paths in this skill are defaults, not absolutes. Always verify paths with `find` before assuming.

### Common Variations

| Purpose | Path |
|---------|------|
| Article notes source | `00-raw/articles/` |
| Domain-specific notes | `02-concepts/<domain>/01-article-notes/` |
| Integration reports | `99-system/03-integration-reports/` |
| Nightly digest | `04-queries/daily/04-summary/` |
| Topic index | `99-system/01-indexes/` |

---

## Cross-Reference Protocol（每次 ingest 后执行）

- Preserve article/source boundary; do not turn speculation into fact
- Prefer minimal, high-signal index updates over bulk rewrites
- Pattern extraction should be cautious; candidate-first is preferred
- If project linkage is low-confidence, leave it unresolved rather than hallucinating

## Nightly Digest Coordination Protocol

This stage is responsible for writing **two layers**:

### Layer A — machine-facing run report
- Write a detailed report to:
  - `99-system/03-integration-reports/YYYY-MM-DD/article-integration-report-YYYY-MM-DD.md`

This is for agents, auditing, and downstream debugging.

### Layer B — human-facing nightly digest
Append / update the `02:00 Article Integration` section in:
- `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md`

Digest section must be readable by {{USER_NAME}} in 30 seconds and include only:
- 处理了哪些文章
- 有无新增 topic / open question
- 是否 no-op / degraded
- 一句话说明为什么值得看或为什么没产出

Downstream 03:00 and 04:00 stages should read this digest first, then read machine reports only if needed.

## Nightly Position in the Split Pipeline

This is the **02:00 stage** in the split nightly knowledge system:
1. `knowledge-lint-weekly` (01:00, Mondays only)
2. `article-notes-integration` (02:00)
3. `conversation-knowledge-mining` (03:00)
4. `knowledge-flywheel-amplifier` (04:00)

Downstream contract:
- 03:00 should first read the shared nightly digest, then machine reports if needed
- 04:00 should first read the shared nightly digest, then machine reports if needed

## Acceptance Standard

Do not call the job complete unless the result is:
- integrated into Brain (if there was real signal)
- committed to git
- confirmed visible in Obsidian / post-commit sync path
