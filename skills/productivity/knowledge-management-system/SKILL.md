---
name: knowledge-management-system
description: Build dynamic, evolving knowledge management systems that adapt to user needs over time.
---

# Building Dynamic Knowledge Management Systems

A systematic approach to creating, maintaining, and evolving personal knowledge bases that adapt to user needs over time.

## When to Use

- User wants to organize notes, projects, tasks, and interests
- Existing knowledge is scattered or unstructured
- User needs a system that can grow and change
- Goal is long-term knowledge retention and retrieval

## Core Principles

1. **Modular Structure**: Organize by function, not just topic
2. **Template-Driven**: Standardize common document types
3. **Evolution-Ready**: Design for regular review and adjustment
4. **Integration-Focused**: Connect with existing workflows (WeChat, email, etc.)
5. **Shareable**: Make knowledge exportable and presentable

## Environment-Specific Adaptation (for Brain OS Wiki)

⚠️ **MIGRATION NOTICE (2026-05-14)**: The knowledge base was migrated from `<OLD_KNOWLEDGE_DIR>/` to `<KNOWLEDGE_DIR>/`. The old `<OLD_KNOWLEDGE_DIR>/` directory has been deleted. All new content should use the new paths.

When working with the Brain OS Wiki structure (`<KNOWLEDGE_DIR>/`):

```
<KNOWLEDGE_DIR>/
├── 00-收件箱/        # 零散内容待处理
├── 01-项目/          # 项目空间
├── 02-工作产出/      # 工作产出归档
├── 03-个人运营/      # 个人运营（简报/计划/待办/日志）
├── 04-知识库/        # 结构化知识（阅读/工作/系统）
├── 05-系统配置/      # 系统配置
├── 06-工作上下文/    # 当前工作上下文
├── 07-参考资料/      # 参考资料
└── 08-归档/          # 归档
```

### Directory Mapping (Old → New)

| Old Path | New Path |
|----------|----------|
| `<OLD_KNOWLEDGE_DIR>/01-个人运营/` | `<KNOWLEDGE_DIR>/03-个人运营/` |
| `<OLD_KNOWLEDGE_DIR>/03-知识库/` | `<KNOWLEDGE_DIR>/04-知识库/` |
| `<OLD_KNOWLEDGE_DIR>/05-系统配置/` | `<KNOWLEDGE_DIR>/05-系统配置/` |

### Project Directory Naming Rules (来自实操教训)

**核心原则：Wiki项目目录名必须与外部系统中的项目名完全一致。**

| 规则 | 说明 | 示例 |
|------|------|------|
| 01-前缀 | 按创建顺序编号 | 01-化工通用业务智能系统 |
| 名称一致 | 跟外部系统项目名完全一致 | 不要写"通用业务风险预警"而外部系统里叫"化工通用业务智能系统" |
| 99-存档 | 旧项目/已合并项目放99-前缀 | 99-通用业务风险预警智能体(旧存档) |

**文档组织：**
```
01-项目名/
├── 计划文档/        # 项目规划、PRD、路线图、审计报告
├── 日报归档/        # 每日产出报告（历史记录）
├── 历史数据/        # 落地方案、图谱资料、经验总结
└── README.md        # 项目概述
```

### 与外部系统同步维护

当项目状态在外部系统中发生变化时（新增Agent、Goal、Issue），必须同步更新Wiki项目文档：
1. 更新 PROJECT-START.md（项目概况、团队、任务数）
2. 更新 多Agent框架设计（Agent列表变化）
3. 更新 TEAM-RECRUITMENT（任务分布、商业化进度）
4. 创建 README 索引方便快速查阅
5. 旧名称目录要么删除要么重命名为99-存档标记

## Implementation Steps

### 1. Assess User Needs
- Ask about primary use cases (work, personal, projects, learning)
- Identify existing tools and workflows to integrate
- Determine sharing requirements
- Understand preferred review frequency

### 2. Design Directory Structure
```
knowledge/
├── 00-inbox/              # Temporary capture
├── 01-work/               # Professional activities
├── 02-personal/           # Personal growth
├── 03-interests/          # Hobbies and passions
├── 04-tasks/              # Action items
├── 05-connections/        # Cross-references
├── 06-shares/             # Export-ready content
└── 99-archive/            # Historical records
```

**Key design decisions:**
- Use numbered prefixes for consistent ordering
- Create subdirectories by function, not just topic
- Include an "inbox" for rapid capture
- Reserve "archive" for old content

### 3. Create Core Templates
Develop reusable templates for:
- **Project templates**: Goals, tasks, timelines, 复盘
- **Meeting templates**: Decisions, action items, follow-ups
- **Goal templates**: OKRs, milestones, progress tracking
- **Task templates**: Priority, dependencies, completion criteria
- **Review templates**: Weekly/monthly reflection frameworks

### 4. Establish Maintenance Routines
Define review cycles:
- **Daily**: Inbox cleanup, task updates
- **Weekly**: Progress review, priority adjustment
- **Monthly**: Module usage analysis, template optimization
- **Quarterly**: Full framework review, structural changes

### 5. Set Up Automation
- **Capture automation**: WeChat → inbox, email → work
- **Reminder system**: Review notifications, deadline alerts
- **Export tools**: One-click format conversion (Markdown → PDF/PPT)
- **Search indexing**: FTS5 for fast retrieval

### 6. Plan for Evolution
- **Version control**: Track framework changes
- **Usage metrics**: Monitor which modules are active
- **Feedback loops**: Regular user input on system effectiveness
- **Adaptation rules**: When to add/remove modules

## Common Pitfalls

### ❌ Over-structuring
- Don't create too many categories initially
- Start with 5-8 core modules, expand as needed
- Allow content to exist in multiple places (tags > folders)

### ❌ Template bloat
- Keep templates concise and focused
- Include only fields you'll actually use
- Leave room for custom additions

### ❌ Maintenance burden
- Review cycles must be realistic
- Automate what you can
- Make it easy to skip a week without breaking the system

### ❌ Ignoring integration
- Connect with existing tools (calendar, email, messaging)
- Don't create another silo
- Minimize friction in the capture process

## Evolution Triggers

**When to restructure:**
- 某模块使用频率持续低于 20%
- 用户开始频繁创建新模块
- 跨模块内容关联变得困难
- 分享需求超出当前框架能力
- 季度审查发现系统性问题

**Adjustment strategies:**
- Merge underused modules
- Split bloated modules
- Add new categories for emerging needs
- Update templates based on actual usage
- Archive obsolete content

## Integration Patterns

### WeChat Capture Flow
```
User message → Inbox → Weekly review → Proper category
```

### Task Management Flow
```
Capture → Prioritize → Schedule → Execute → Review → Archive
```

### Project Lifecycle
```
Idea → Planning → Execution → Review → Archive → Lessons learned
```

## Success Metrics

- **Capture rate**: How quickly can you record new information?
- **Retrieval time**: How fast can you find what you need?
- **Review completion**: Do you actually do the scheduled reviews?
- **Usage diversity**: Are multiple modules being used?
- **Shareability**: Can you easily export content?

## Customization Options

### By User Type
- **Developer**: Emphasize code documentation, project specs
- **Researcher**: Focus on literature reviews, experiment logs
- **Creative**: Prioritize inspiration capture, portfolio building
- **Manager**: Highlight meeting notes, team coordination

### By Platform
- **WeChat**: Optimize for mobile capture, short messages
- **Email**: Integration with inbox rules, filters
- **Calendar**: Time-blocking, deadline tracking
- **GitHub**: Code documentation, version control

## Knowledge Base Audit (Weekly)

Run a systematic audit weekly via cron (`knowledge-lint-weekly`) to detect structural decay. The audit checks YAML frontmatter coverage, broken wikilinks, orphan notes, duplicate basenames, and format issues.

### Audit Checklist

| Check | What It Finds | Acceptable Baseline |
|-------|--------------|-------------------|
| YAML frontmatter | Files missing `--- ... ---` | Auto-generated content (logs, scripts, reports) don't need it |
| Broken Obsidian `[[wikilinks]]` | `[[target]]` pointing to non-existent files | 0 tolerated for non-template files |
| Broken relative `.md` links | `[text](path.md)` pointing to wrong paths | 0 tolerated |
| Orphan notes (no inbound links) | Files no other file references | Contextual — auto-content is expected orphan |
| Duplicate basenames | Same filename in multiple directories | Check for consolidation opportunity |
| Trailing whitespace | Lines ending with spaces/tabs | Auto-fix when touching files |
| Very long lines (>500 chars) | Lines exceeding readability threshold | Acceptable in data tables |
| Empty/small files (<50 bytes) | Files that are effectively empty | 0 tolerated |

### Exempt Categories (auto-generated, no audit concern)

- 特定项目脚本 (`01-项目/02-特定项目改编/*/script/`)
- Channel history logs (`03-个人运营/05-频道历史/`)
- Nightly digests (`04-知识库/01-阅读消化/04-摘要汇总/`)
- Nightly reports (`04-知识库/99-系统/03-*报告/`)
- Cron prompt files (`05-系统配置/提示词/`)
- Archives (`08-归档/`)
- `README.md`, `index.md` at root

### Audit Script Template

```python
#!/usr/bin/env python3
"""Weekly knowledge base audit"""
import json, re, os
from collections import defaultdict

KB = "<KNOWLEDGE_DIR>"
files = []
for root, dirs, fnames in os.walk(KB):
    if '.git' in dirs: dirs.remove('.git')
    for fn in fnames:
        if fn.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, fn), KB)
            if rel.startswith('./'): rel = rel[2:]
            files.append(rel)
files.sort()
total = len(files)

# Build lookup maps
basename_map = defaultdict(list)
title_to_path = {}
for f in files:
    base = os.path.splitext(os.path.basename(f))[0]
    basename_map[base].append(f)
    title_to_path[os.path.splitext(f)[0]] = f

# === YAML Frontmatter ===
for f in files:
    fp = os.path.join(KB, f)
    with open(fp, 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read(5000)
    lines = content.split('\n')
    if not lines or lines[0].strip() != '---':
        no_frontmatter.append(f); continue
    # find closing ---
    end_idx = next((i for i in range(1, min(len(lines), 60))
                     if lines[i].strip() == '---'), None)
    if end_idx is None: broken_frontmatter.append(f)

# === Broken Wikilinks ===
for f in files:
    with open(os.path.join(KB, f), 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read()
    wikilinks = re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*)?\]\]', content)
    for link in wikilinks:
        target = link.strip()
        found = False
        for c in [target, target + '.md']:
            if c in title_to_path: found = True; break
            if os.path.splitext(os.path.basename(c))[0] in basename_map:
                found = True; break
        if not found: obsidian_broken[f].append(target)

# === Orphan Notes (Inbound Link Graph) ===
inbound_graph = defaultdict(set)
# build from wikilinks found above
for src, targets in obsidian_links.items():
    for tgt in targets:
        found_path = None
        if tgt in title_to_path: found_path = title_to_path[tgt]
        else:
            base = os.path.splitext(os.path.basename(tgt))[0]
            if base in basename_map:
                found_path = basename_map[base][0]
        if found_path and found_path != src:
            inbound_graph[found_path].add(src)

orphans = [f for f in files if f not in inbound_graph]
```

### Common Pitfalls

1. **index.md migration artifacts**: After directory restructuring (e.g. `03-知识库/` → `04-知识库/`), the root `index.md` index.md`often retains old paths. Always check and update `index.md` after any structural rename.
2. **SCHEMA.md example links**: `SCHEMA.md` often contains `[[wikilinks]]` as a documentation example, not a real broken link. Filter these out.
3. **Cron prompt template paths**: Prompt files may contain `[[YYYY-MM-DD]]` or path templates like `03-KNOWLEDGE/...` that are substituted at runtime. These are not real broken links.
4. **Duplicate basenames are often intentional**: The same content may live in `02-工作产出/` (deliverable) and `04-知识库/` (knowledge reference). Only flag duplicates across same-category directories as consolidation candidates.
5. **Orphan notes need judgment**: ~90% of files in a cron-populated knowledge base are orphans by design (scripts, logs, reports). Focus on knowledge document orphans — domain knowledge, topic notes, project docs that lack inbound links.

## Maintenance Commands

```bash
# Check knowledge base structure
tree ~/.hermes/knowledge

# Count files by module
find ~/.hermes/knowledge -name "*.md" | wc -l

# Find outdated content
find ~/.hermes/knowledge -mtime +90

# Generate usage report
find ~/.hermes/knowledge -name "*.md" | while read f; do
  size=$(wc -c < "$f")
  lines=$(wc -l < "$f")
  echo "$size $lines $f"
done | sort -rn | head -20

# Weekly audit (run standalone)
python3 /path/to/audit-script.py 2>&1
```

## Review Questions

**Weekly:**
- What new information did I capture?
- What tasks did I complete?
- What needs to be prioritized next week?

**Monthly:**
- Which modules am I using most/least?
- Are my templates still relevant?
- What patterns am I noticing?

**Quarterly:**
- Does the structure still make sense?
- What new needs have emerged?
- What should be archived?
- What templates need updating?

## Example Implementation Timeline

**Day 1**: Create basic structure and templates (30 min)
**Week 1**: Test with real content, adjust as needed
**Month 1**: First full review, identify improvements
**Month 3**: Quarterly review, restructure if needed
**Ongoing**: Monthly maintenance, quarterly evolution

---

## Related Skills

- `productivity/chronicle-agent` - Chronicle Agent for conversation mining and logging
- `note-taking/obsidian` - Alternative knowledge management approach
- `productivity/google-workspace` - Cloud-based alternatives
- `productivity/notion` - Database-driven knowledge systems
- `research/arxiv` - Academic paper management
- `mlops/weights-and-biases` - ML experiment tracking

## Lint → Kanban 闭环

**参考文档**: `references/lint-kanban-loop.md`

将知识库 Lint 发现的问题自动创建为 Kanban 卡片，形成修复闭环：
- `scripts/lint-to-kanban.py` — Lint → Kanban 集成脚本（调用 `hermes kanban create`）
- `scripts/fix-knowledge-issues.py` — 自动修复脚本（断链、frontmatter）
- 问题追踪器: `lint-reports/issues-tracker.md`
- 通知渠道: Telegram（避免微信限流）

**脚本位置**: `<HERMES_SCRIPTS_DIR>/`（也可从 skill 的 scripts 目录调用）

## Migration History

**2026-05-14**: Knowledge base migrated from `<OLD_KNOWLEDGE_DIR>/` to `<KNOWLEDGE_DIR>/`
- See `chronicle-agent/references/directory-structure-migration.md` for details
