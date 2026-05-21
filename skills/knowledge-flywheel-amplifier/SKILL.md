---
name: knowledge-flywheel-amplifier
description: >
  Cross-source nightly amplifier for merging article-derived and
  conversation-derived signals into topic updates, pattern candidates,
  open questions, and candidate research seeds. Use when: knowledge flywheel,
  amplify knowledge, cross-source synthesis, nightly amplifier,
  04:00 flywheel stage, topic merge, open question clustering.
---

# Knowledge Flywheel Amplifier

把 02:00 的文章整合结果与 03:00 的对话沉淀结果做轻量汇合，形成跨源主题、候选模式、开放问题与后续研究输入。

## Purpose

这个技能负责 **跨文章与对话的 amplification 层**，而不是重新做 article integration 或 transcript mining。

它处理的是：
1. 汇总 Stage A（文章）与 Stage B（对话）的新增高价值信号
2. 识别重复主题、交叉问题、共同模式与项目路由机会
3. 更新少量高价值的 topic / open-question / pattern-candidate surfaces
4. 生成 research seeds / context-pack candidates
5. 为后续是否值得深研提供条件化升级输入

## Primary Inputs

- Stage A outputs:
  - article integration reports
  - high-value article candidates
  - updated article-derived relation/index signals
- Stage B outputs:
  - transcript mining brief
  - conversation-derived notes
  - daily suggestions updates
  - candidate research seeds / context-pack candidates
- Read-only Brain context:
  - `99-system/01-indexes/`
  - `99-system/03-integration-reports/`
  - `99-system/trackers/` (e.g., `article-integration-tracker.md`)
  - relevant domain notes
  - `05-outputs/` project briefs
  - `09-personal-ops/05-channel-history/`
  - existing open questions / topic maps / pattern candidate surfaces

> **⚠️ Path Naming Convention**: The knowledge base uses **English naming** for system directories (`99-system/`, `09-personal-ops/`, `04-queries/`). Always verify with `ls` before assuming.

> **⚠️ Path Migration Note**: Prior to 2026-05-15, paths used `03-知识库/`. After wiki → knowledge migration, all paths use `04-queries/` and `99-system/`. Verify current path structure before writing.

**See**: `references/path-migration-2026-05-15.md` for migration incident details.

> **⚠️ Session Search Limitation**: `session_search` with exact time windows may return 0 results even when relevant sessions exist. Always verify by listing actual session files in `<HERMES_SESSIONS_DIR>/` and reading content directly if needed.

### Required Outputs

A successful run should produce some or all of:
- 1 machine-facing run report → `99-system/03-integration-reports/YYYY-MM-DD/knowledge-amplifier-report-YYYY-MM-DD.md`
- 1 human-facing digest section append → `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md`
- merged topic / open-question / pattern-candidate updates when justified
- zero to two research seeds
- zero or more context-pack drafts
- optional project/domain routing suggestions
- Brain git commit + post-commit visibility confirmation when Brain changed
- **Optional**: New project brief in `05-outputs/` when strategy→execution transition detected
- **Optional**: Write findings to `/tmp/knowledge-amplifier-findings-YYYYMMDD.md` and invoke `kanban-sync.py --write-todo` for P1/P2 items

**See**: `references/cross-source-patterns.md` for validated cross-source patterns.

**See**: `references/verified-paths-2026-05-20.md` for actual verified path mappings.

## What This Skill May Read

- outputs from `article-notes-integration`
- outputs from `conversation-knowledge-flywheel`
- existing Brain indexes / project briefs / knowledge notes / topic surfaces
- `references/verified-paths-2026-05-20.md` — actual verified path mappings
- `references/cross-source-patterns.md` — validated cross-source patterns

## What This Skill May Write

- Write topic map / topic index updates
- Write open questions
- Write pattern candidates
- Write cross-source routing notes or compact synthesis notes
- Write amplifier reports
- Write context-pack drafts / research seed drafts
- **Write new project briefs** in `05-outputs/` (strategy→execution transitions)

**See**: `references/cross-source-patterns.md` for pattern definitions and examples.

## Nightly Digest Coordination Protocol

This stage must always write **two layers**:

### Layer A — machine-facing run report
Write a detailed report to:
- `99-system/03-integration-reports/YYYY-MM-DD/knowledge-amplifier-report-YYYY-MM-DD.md`

### Layer B — human-facing nightly digest
Append / update the `04:00 Amplifier` section in:
- `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md`

Digest section must tell {{USER_NAME}} only:
- 今晚有没有真正形成跨源汇合
- 如果没有，是因为哪一段缺失 / degraded（e.g., Stage 2 无内容→纯工程日→专注于基础设施对话）
- 如果有，最值得看的 topic / open question / research seed 是什么
- 是否触发深度研究，若没触发，原因是什么

This stage should read the shared nightly digest first, then machine-facing reports only when needed.

## Additional Signal Sources

Beyond Stage A and Stage B reports, read these for broader context:

1. **Previous days' digests** — Read the past 1-2 days' `nightly-digest-YYYY-MM-DD.md` files to establish cross-day continuity. This enables insights like:
   - "X project was 'in progress' yesterday, today it's 'completed'" (cross-day tracking)
   - Infrastructure status trajectory (告警从多到少意味着什么?)
   - Pattern recurrence across days

2. **Chronicle Agent channel history** — The latest `09-personal-ops/05-channel-history/YYYY-MM-DD-HH.md` file contains infrastructure status, pipeline run results, error counts, and user session patterns. This provides system health context beyond what conversation mining captures.

3. **Git log** — `git log --oneline --since="YYYY-MM-DD"` shows what was committed and when, useful for confirming pipeline execution and detecting silent failures.

## Cross-Day Analysis Pattern

When doing weak signal / pattern detection, don't limit to a single day:
- Compare告警 counts across days — spikes/decreases reveal infrastructure health trends
- Track project state transitions across multiple digests (e.g., "in progress" → "completed" → "pending")
- Look for user behavior changes (earlier/later sign-off, different interaction density)
- Identify recurring patterns: same告警 persisting, same projects stuck at same stage

**Week profile synthesis**: If ≥3 consecutive daily digests exist, build a week-profile table following `references/cross-source-patterns.md → Pattern 5` to detect thematic progression, article silence duration, and work rhythm patterns.

---

## 🆕 Pattern Library — Reusable Cross-Source Patterns

These patterns have been validated through multiple nightly runs:

### Pattern 1: 战略→执行衔接 (Strategy → Execution Transition)

**Trigger**: User shifts from strategic planning to execution ("如何落地", "怎么开始做") + existing strategy documents found

**Signal chain**:
```
对话: 执行需求 → 知识库: 战略文档 → 工具: Kanban → 输出: 任务图
```

**Steps**:
1. Search for strategy docs (tags: `strategy`, `project`)
2. Extract priorities and implementation plans from strategy
3. Use Kanban to decompose strategy into executable tasks
4. Create "strategy → task" mapping
5. Output: executable task map + strategy alignment notes

**Example**: 通用业务数字化看板规划 → 四大板块 + T0-T9 任务图草案

---

### Pattern 2: 系统故障→技能沉淀 (System Bug → Skill)

**Trigger**: System-level bug fix completed

**Steps**：
1. Document problem symptoms + root cause
2. Document fix + verification steps
3. Create skill file with "故障特征" and "修复命令"
4. Update related docs' "Known Issues" section

**Example**: `_pipe_stdin` 死锁修复 → `hermes-agent-pipe-fix` 技能

---

### Pattern 3: 结构重构→路径适配 (Structure Refactor → Path Adaptation)

**Trigger**: Directory structure major change (e.g., wiki → knowledge migration)

**Signal chain**:
```
系统维护: 目录重构 → 技能路径失效 → Cron 任务路径更新 → 验证完整性
```

**Steps**:
1. Identify all skills referencing old paths
2. Batch update skill SKILL.md files
3. Update cron task templates
4. Verify with grep for orphaned references
5. Test cron execution to catch silent failures

**Example**: wiki → knowledge migration (823 files) → path updates across skills and cron

---

### Pattern 4: 连锁反应模式 (Chain Reaction Pattern)

**Trigger**: Single fix triggers multiple downstream changes

**Signal chain**:
```
bug 修复 → 发现路径不一致 → 触发目录迁移 → 触发 cron 更新 → 触发技能更新
```

**Steps**:
1. Document the initial trigger
2. Track all downstream effects
3. Create "变更影响评估" checklist for future fixes
4. Update skills with chain reaction awareness

**Example**: `_pipe_stdin` fix → path discovery → wiki → knowledge migration

---

## Default Nightly Behavior

The default 04:00 behavior is intentionally lightweight:
- merge signals
- detect overlaps and gaps
- update only small, high-value graph/index surfaces
- generate research seeds or context-pack candidates when warranted

It must **not** automatically escalate into heavy external research every night.

## Escalation Criteria

A follow-up deep-research task may be spawned only when:
- the theme is high-value
- internal context already exists
- the question is narrow enough to avoid drift
- the likely payoff is worth the additional complexity

If these are not met, stay at candidate seed / context-pack level.

## Success Criteria

A run is successful when:
- article and conversation signals are merged without collapsing their boundaries
- only justified graph/index updates are made
- high-value open questions / pattern candidates are surfaced clearly
- deep research remains optional and condition-based
- Brain changes are committed and Obsidian-visible

## Failure / Degraded Mode

- **Missing Stage A output** → continue with Stage B only, but say article context is partial
- **Missing Stage B output** → continue with Stage A only, but say conversation context is partial
- **No cross-source signal** → emit a no-op amplifier report; do not force graph changes
- **Unclear topic merge** → keep separate candidates rather than over-merge

### ⚠️ Pitfall: Path Migration Verification

After knowledge directory structure changes (e.g., wiki → knowledge migration on 2026-05-15):

1. **Verify path structure first** — Check actual directory layout before assuming paths
2. **Check cron task paths** — 823+ file migrations may leave orphaned cron tasks with old paths
3. **Test skill references** — Skills may still reference old `03-知识库/` paths; update them
4. **Silent failure risk** — Cron tasks with wrong paths fail silently; verify with `git log` and actual execution

**Verification command**:
```bash
# Check actual knowledge directory structure
ls -la <KNOWLEDGE_DIR>/

# Find any remaining old-path references
grep -r "03-知识库" <HERMES_ROOT>/skills/ 2>/dev/null | head -20
```

Nightly digests accumulate in **one location** — read from the correct one:

| Location | Status | Path |
|----------|--------|------|
| Main (pipeline output) | ✅ Current | `04-queries/daily/04-summary/nightly-digest-YYYY-MM-DD.md` |

**Resolution**: Always read from `04-queries/daily/04-summary/` as the primary source.

### ⚠️ Pitfall: Degraded Mode Transparency

When upstream stages produce no output:
- **Do not** fabricate cross-source signals to "make the run look productive"
- **Do** explicitly state which stage was degraded and why
- **Do** analyze what the degradation signals about the current work pattern (e.g., "pure engineering day → no articles, only system maintenance")
- **Do** update the nightly digest with honest assessment, not forced insights

### ⚠️ Pitfall: kanban-sync.py Output Format

When using `kanban-sync.py --write-todo`, the output file must contain items matching the regex pattern `r"([⚠️🔴🟡🟢✅❌]\s*.+)"` to be parsed correctly.

**Correct format**:
```markdown
⚠️ P1: 问题描述 - 详细说明
⚠️ P2: 另一个问题 - 详细说明
```

**Incorrect format** (will not be parsed):
```markdown
### P1: 通用业务风险预警日报积压
- **问题**: 详细说明
```

The parser extracts items line-by-line using emoji markers. Use bullet points or headers only for context, not for the actual items to be extracted.

## Anti-Scope

This skill must **not**:
- re-run full article note normalization
- re-run full transcript mining
- auto-run heavy NotebookLM / agent-reach deep research by default
- perform large-scale graph rewrites to simulate activity
- erase source boundaries between article-derived and conversation-derived knowledge

## Output Quality Bar

- Merge conservatively; preserve provenance
- Prefer compact high-value updates over broad topology surgery
- Open questions should be concrete, not vague brainstorming sludge
- Pattern candidates should remain candidates unless evidence is strong
- Research seeds should be scoped enough for safe downstream amplification

## Nightly Position in the Split Pipeline

This is the **04:00 stage** in the split nightly knowledge system:
1. `article-notes-integration` (02:00)
2. `conversation-knowledge-flywheel` (03:00) — formerly `conversation-knowledge-mining`
3. `knowledge-flywheel-amplifier` (04:00)

Upstream contract:
- read Stage A and Stage B outputs if present
- tolerate partial upstream success
- never pretend upstream work succeeded if inputs are missing

## Acceptance Standard

Do not call the job complete unless the result is:
- written into Brain only where justified
- committed to git when Brain changed
- confirmed visible in Obsidian / post-commit sync path
- explicit about whether deep research was merely proposed or actually escalated
