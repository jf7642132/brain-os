---
name: llm-wiki
description: "Karpathy's LLM Wiki: build/query interlinked markdown KB."
version: 2.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [obsidian, arxiv]
---

# Karpathy's LLM Wiki

Build and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent
summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## Wiki Location

**Location:** Set via `WIKI_PATH` environment variable (e.g. in `~/.hermes/.env`).

If unset, defaults to `~/wiki`.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
```

### ⚠️ WIKI_PATH Configuration

When using llm-wiki with an existing knowledge base that's NOT at `~/wiki`:

1. **Set the environment variable** in `~/.hermes/.env`:
   ```bash
   WIKI_PATH=/path/to/your/knowledge/base
   ```

2. **Restart the gateway** to pick up the new env var:
   ```bash
   hermes gateway restart
   ```

3. **Verify** the skill is using the correct path:
   ```bash
   hermes cron list  # Check cron job workdir matches WIKI_PATH
   ```

**Common pitfall:** Cron jobs may have hardcoded paths (e.g., `/root/.hermes/knowledge`) while llm-wiki defaults to `~/wiki`. Always align `WIKI_PATH` with the actual knowledge base location before running lint/audit tasks.

The wiki is just a directory of markdown files — open it in Obsidian, VS Code, or
any editor. No database, no special tooling required.

## Architecture: Three Layers

```
wiki/
├── SCHEMA.md           # Conventions, structure rules, domain config
├── index.md            # Sectioned content catalog with one-line summaries
├── log.md              # Chronological action log (append-only, rotated yearly)
├── raw/                # Layer 1: Immutable source material
│   ├── articles/       # Web articles, clippings
│   ├── papers/         # PDFs, arxiv papers
│   ├── transcripts/    # Meeting notes, interviews
│   └── assets/         # Images, diagrams referenced by sources
├── entities/           # Layer 2: Entity pages (people, orgs, products, models)
├── concepts/           # Layer 2: Concept/topic pages
├── comparisons/        # Layer 2: Side-by-side analyses
└── queries/            # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown files. Created, updated, and
cross-referenced by the agent.
**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing Wiki (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

① **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
② **Read `index.md`** — learn what pages exist and their summaries.
③ **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
WIKI="${WIKI_PATH:-$HOME/wiki}"
# Orientation reads at session start
read_file "$WIKI/SCHEMA.md"
read_file "$WIKI/index.md"
read_file "$WIKI/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New Wiki

When the user asks to create or start a wiki:

1. Determine the wiki path (from `$WIKI_PATH` env var, or ask the user; default `~/wiki`)
2. Create the directory structure above
3. Ask the user what domain the wiki covers — be specific
4. Write `SCHEMA.md` customized to the domain (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain. The schema constrains agent behavior and ensures consistency:

```markdown
# Wiki Schema

## Domain
[What this wiki covers — e.g., "AI/ML research", "personal health", "startup intelligence"]

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `transformer-architecture.md`)
- Every wiki page starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages that synthesize 3+ sources, append `^[raw/articles/source-file.md]`
  at the end of paragraphs whose claims come from a specific source. This lets a reader trace each
  claim back without re-reading the whole raw file. Optional on single-source pages where the
  `sources:` frontmatter is enough.

## Frontmatter
  ```yaml
  ---
  title: Page Title
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  type: entity | concept | comparison | query | summary
  tags: [from taxonomy below]
  sources: [raw/articles/source-name.md]
  # Optional quality signals:
  confidence: high | medium | low        # how well-supported the claims are
  contested: true                        # set when the page has unresolved contradictions
  contradictions: [other-page-slug]      # pages this one conflicts with
  ---
  ```

`confidence` and `contested` are optional but recommended for opinion-heavy or fast-moving
topics. Lint surfaces `contested: true` and `confidence: low` pages for review so weak claims
don't silently harden into accepted wiki fact.

### raw/ Frontmatter

Raw sources ALSO get a small frontmatter block so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article   # original URL, if applicable
ingested: YYYY-MM-DD
sha256: <hex digest of the raw content below the frontmatter>
---
```

The `sha256:` lets a future re-ingest of the same URL skip processing when content is unchanged,
and flag drift when it has changed. Compute over the body only (everything after the closing
`---`), not the frontmatter itself.

## Tag Taxonomy
[Define 10-20 top-level tags for the domain. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. If a new tag is needed,
add it here first, then use it. This prevents tag sprawl.

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one source
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines — break into sub-topics with cross-links
- **Archive a page** when its content is fully superseded — move to `_archive/`, remove from index

## Entity Pages
One page per notable entity. Include:
- Overview / what it is
- Key facts and dates
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison (table format preferred)
- Verdict or synthesis
- Sources

## Update Policy
When new information conflicts with existing content:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources
3. Mark the contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in the lint report
```

### index.md Template

The index is sectioned by type. Each entry is one line: wikilink + summary.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its type with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- Alphabetical within section -->

## Concepts

## Comparisons

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections
by first letter or sub-domain. When the index exceeds 200 entries total, create
a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

## Core Operations

### 1. Ingest

When the user provides a source (URL, file, paste), integrate it into the wiki:

① **Capture the raw source:**
   - URL → use `web_extract` to get markdown, save to `raw/articles/`
   - PDF → use `web_extract` (handles PDFs), save to `raw/papers/`
   - Pasted text → save to appropriate `raw/` subdirectory
   - Name the file descriptively: `raw/articles/karpathy-llm-wiki-2026.md`
   - **Add raw frontmatter** (`source_url`, `ingested`, `sha256` of the body).
     On re-ingest of the same URL: recompute the sha256, compare to the stored value —
     skip if identical, flag drift and update if different. This is cheap enough to
     do on every re-ingest and catches silent source changes.

② **Discuss takeaways** with the user — what's interesting, what matters for
   the domain. (Skip this in automated/cron contexts — proceed directly.)

③ **Check what already exists** — search index.md and use `search_files` to find
   existing pages for mentioned entities/concepts. This is the difference between
   a growing wiki and a pile of duplicates.

④ **Write or update wiki pages:**
   - **New entities/concepts:** Create pages only if they meet the Page Thresholds
     in SCHEMA.md (2+ source mentions, or central to one source)
   - **Existing pages:** Add new information, update facts, bump `updated` date.
     When new info contradicts existing content, follow the Update Policy.
   - **Cross-reference:** Every new or updated page must link to at least 2 other
     pages via `[[wikilinks]]`. Check that existing pages link back.
   - **Tags:** Only use tags from the taxonomy in SCHEMA.md
   - **Provenance:** On pages synthesizing 3+ sources, append `^[raw/articles/source.md]`
     markers to paragraphs whose claims trace to a specific source.
   - **Confidence:** For opinion-heavy, fast-moving, or single-source claims, set
     `confidence: medium` or `low` in frontmatter. Don't mark `high` unless the
     claim is well-supported across multiple sources.

⑤ **Update navigation:**
   - Add new pages to `index.md` under the correct section, alphabetically
   - Update the "Total pages" count and "Last updated" date in index header
   - Append to `log.md`: `## [YYYY-MM-DD] ingest | Source Title`
   - List every file created or updated in the log entry

⑥ **Report what changed** — list every file created or updated to the user.

A single source can trigger updates across 5-15 wiki pages. This is normal
and desired — it's the compounding effect.

### 2. Query

When the user asks a question about the wiki's domain:

① **Read `index.md`** to identify relevant pages.
② **For wikis with 100+ pages**, also `search_files` across all `.md` files
   for key terms — the index alone may miss relevant content.
③ **Read the relevant pages** using `read_file`.
④ **Synthesize an answer** from the compiled knowledge. Cite the wiki pages
   you drew from: "Based on [[page-a]] and [[page-b]]..."
⑤ **File valuable answers back** — if the answer is a substantial comparison,
   deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`.
   Don't file trivial lookups — only answers that would be painful to re-derive.
⑥ **Update log.md** with the query and whether it was filed.

### 3. Lint

When the user asks to lint, health-check, or audit the wiki:

### ① **Orphan pages:** Find pages with no inbound `[[wikilinks]]` from other pages.

**Use the provided script** for automated linting:
```bash
# Run lint check with optional report save
python $HERMES_SKILLS/research/llm-wiki/scripts/wiki-lint.py [WIKI_PATH] [--save]

# Example:
python ~/hermes/skills/research/llm-wiki/scripts/wiki-lint.py ~/wiki --save
```

The script performs all 13 lint checks and outputs a formatted markdown report.

② **Broken wikilinks:** Find `[[links]]` that point to pages that don't exist.

③ **Index completeness:** Every wiki page should appear in `index.md`. Compare
   the filesystem against index entries.

④ **Frontmatter validation:** Every wiki page must have all required fields
   (title, created, updated, type, tags, sources). Tags must be in the taxonomy.

⑤ **Stale content:** Pages whose `updated` date is >90 days older than the most
   recent source that mentions the same entities.

⑥ **Contradictions:** Pages on the same topic with conflicting claims. Look for
   pages that share tags/entities but state different facts. Surface all pages
   with `contested: true` or `contradictions:` frontmatter for user review.

⑦ **Quality signals:** List pages with `confidence: low` and any page that cites
   only a single source but has no confidence field set — these are candidates
   for either finding corroboration or demoting to `confidence: medium`.

⑧ **Source drift:** For each file in `raw/` with a `sha256:` frontmatter, recompute
   the hash and flag mismatches. Mismatches indicate the raw file was edited
   (shouldn't happen — raw/ is immutable) or ingested from a URL that has since
   changed. Not a hard error, but worth reporting.

⑨ **Page size:** Flag pages over 200 lines — candidates for splitting.

⑩ **Tag audit:** List all tags in use, flag any not in the SCHEMA.md taxonomy.

⑪ **Log rotation:** If log.md exceeds 500 entries, rotate it.

⑫ **Report findings** with specific file paths and suggested actions, grouped by
   severity (broken links > orphans > source drift > contested pages > stale content > style issues).

⑬ **Append to log.md:** `## [YYYY-MM-DD] lint | N issues found`

## Working with the Wiki

### Searching

```bash
# Find pages by content
search_files "transformer" path="$WIKI" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$WIKI"

# Find pages by tag
search_files "tags:.*alignment" path="$WIKI" file_glob="*.md"

# Recent activity
read_file "$WIKI/log.md" offset=<last 20 lines>
```

### Bulk Ingest

When ingesting multiple sources at once, batch the updates:
1. Read all sources first
2. Identify all entities and concepts across all sources
3. Check existing pages for all of them (one search pass, not N)
4. Create/update pages in one pass (avoids redundant updates)
5. Update index.md once at the end
6. Write a single log entry covering the batch

### Archiving

When content is fully superseded or the domain scope changes:
1. Create `_archive/` directory if it doesn't exist
2. Move the page to `_archive/` with its original path (e.g., `_archive/entities/old-page.md`)
3. Remove from `index.md`
4. Update any pages that linked to it — replace wikilink with plain text + "(archived)"
5. Log the archive action

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.

### Brain OS 特定 Pitfalls

- **编号冲突** — 创建新目录前必须检查编号唯一性。编号 00-09 应连续，99 用于系统层。
- **路径引用同步** — 修改目录结构后，必须同步更新 `cron/jobs.json`、`SCHEMA.md`、`index.md`、`kanban-sync.py`。
- **根级文件位置** — `SCHEMA.md`、`index.md`、`log.md` 应位于知识库根目录，不应放入编号子目录。
- **中文目录规范** — 目录名英文，文件名中文。子目录名也应为英文，避免嵌套中文。
- **kanban-sync.py 任务配置** — `TASK_CONFIG` 必须与 cron 任务保持同步，添加新任务时需更新。

### kanban-sync.py 已知问题与修复

**问题 1: `--read-todo` 模式只有打印语句，无实际实现**

```python
# ❌ 错误代码（已修复）
elif args.read_todo:
    print(f"子模式: READ_TODO（todo → Kanban）")
```

**修复**: 添加完整实现，包括读取 todo、过滤已有卡片的待办、创建 Kanban 卡片、更新 todo 中的卡片 ID。

```python
# ✅ 正确代码
if args.read_todo:
    print("📋 步骤 1: 读取 todo-backlog.md...")
    todo_items = read_todo_backlog()
    open_items = todo_items.get("H", []) + todo_items.get("M", []) + todo_items.get("L", [])
    pending_items = [item for item in open_items if not item.get("kanban_id")]
    
    print(f"   待创建 Kanban 的 todo: {len(pending_items)} 个")
    
    if not pending_items:
        print("   无待办需要创建 Kanban 卡片")
        return 0
    
    print("📌 步骤 2: 创建 Kanban 卡片...")
    for item in pending_items:
        kanban_id = create_kanban_task(
            title=f"[{task_name}] {item['description'][:60]}",
            body=f"来源: `{args.task}`\n\n原始待办 ID: {item['id']}\n\n问题描述: {item['description']}",
            assignee=args.assignee,
            priority=PRIORITY_MAP.get(args.priority, 2),  # ⚠️ 必须转换为 int
            dry_run=args.dry_run
        )
        if kanban_id and not args.dry_run:
            update_todo_kanban_id(item['id'], kanban_id)
```

**问题 2: `read_todo_backlog()` 不兼容单一"活跃待办"章节格式**

原代码只识别 `## 高优先级`、`## 中优先级`、`## 低优先级`、`## 已完成` 章节，但 todo-backlog.md 使用单一 `## 活跃待办` 章节。

**修复**: 添加对 `## 活跃待办` 章节的兼容，根据状态字段自动分类。

```python
elif line.startswith('## 活跃待办'):
    current_section = "active"
    continue

# 在解析行时根据状态分类
if status in ['open', 'in_progress']:
    items["H"].append({...})
elif status in ['completed', 'resolved', 'done']:
    items["done"].append({...})
elif current_section == "active":
    items["H"].append({...})
```

**问题 3: 缺少 `update_todo_kanban_id()` 函数**

创建 Kanban 卡片后需要更新 todo 中的 Kanban 卡片 ID 字段，但原代码没有此函数。

**修复**: 添加新函数。

```python
def update_todo_kanban_id(todo_id: str, kanban_id: str) -> bool:
    """更新 todo 中的 Kanban 卡片 ID"""
    if not Path(TODO_PATH).exists():
        return False
    
    content = Path(TODO_PATH).read_text(encoding='utf-8')
    
    for line in content.split('\n'):
        if todo_id in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                parts[4] = kanban_id  # Kanban 卡片字段
                parts[6] = datetime.now().strftime('%Y-%m-%d %H:%M')  # 最后更新时间
                new_line = '| ' + ' | '.join(parts) + ' |\n'
                content = content.replace(line, new_line)
                Path(TODO_PATH).write_text(content, encoding='utf-8')
                return True
    return False
```

**问题 4: `task_name` 作用域错误**

`task_name` 定义在模式判断之后，但 `--read-todo` 模式在模式判断内部使用，导致 `UnboundLocalError`。

**修复**: 将 `task_name` 定义移到模式判断之前。

```python
# 获取任务配置（在模式判断之前）
config = TASK_CONFIG.get(args.task, {})
task_name = config.get("name", args.task)

# 模式判断
if args.update_todo:
    ...
elif args.read_todo:
    # 现在可以访问 task_name
    ...
```

**问题 5: `priority` 类型不匹配**

`create_kanban_task()` 期望 `priority` 为 `int`，但 `args.priority` 是 `str`（如 "P2"）。

**修复**: 使用 `PRIORITY_MAP.get()` 转换。

```python
priority=PRIORITY_MAP.get(args.priority, 2)  # "P2" → 2
```

**测试流程（CRITICAL）**:

正确的测试顺序应该是：

```
生产者 → todo → Kanban 管理层 → Kanban → todo → 消费者 → 报告
```

1. **第一步：生产者 → todo** — 手动创建测试待办，验证格式正确
2. **第二步：todo → Kanban 管理层** — 执行 `--read-todo`，验证创建卡片并更新 todo
3. **第三步：todo → 消费者 → 报告** — 触发消费者任务，验证读取 todo 并生成报告

**⚠️ 常见错误**: 测试顺序颠倒（先触发消费者再验证 todo），导致无法验证完整闭环。

### Cron Job Configuration

When running llm-wiki tasks via cron:

1. **Bind the skill to cron jobs** — don't leave `skills: []` empty. Use:
   ```bash
   hermes cron edit <job-id> --add-skill llm-wiki
   ```

2. **Align WIKI_PATH with cron workdir** — ensure `hermes config get` or `.env` has:
   ```bash
   WIKI_PATH=/root/.hermes/knowledge
   ```

3. **Spread out multiple cron jobs** — if multiple jobs send to the same messaging channel
   (e.g., WeChat/iLink), stagger their schedules to avoid rate limiting:
   - Minimum 30-minute gaps between consecutive deliveries
   - Example: 01:30, 02:00, 06:00 instead of all at 01:00

4. **Check for stale gateway warnings** — `hermes gateway status` may show "token already in use"
   with a stale PID. Verify the process actually exists:
   ```bash
   ps aux | grep <stale-pid>
   ```
   If the PID doesn't exist, the warning is harmless and can be ignored.

5. **⚠️ delivery_mode MUST be set** — cron jobs with `delivery_mode: None` will generate reports
   but never send them. Always configure a delivery channel:
   ```bash
   hermes cron edit <job-id> --set-delivery telegram --set-chat-id <YOUR_TELEGRAM_CHAT_ID>
   ```
   - **WeChat/iLink** has strict rate limiting (ret=-2). Use for real-time user interactions only.
   - **Telegram** has no rate limits for bot messages. Use for scheduled/automated reports.
   - **DingTalk** is reliable for enterprise notifications.

6. **Verify delivery after editing** — run a manual trigger to confirm:
   ```bash
   hermes cron run <job-id>
   # Then check the target channel for the message
   ```

### Lint Closed-Loop Workflow

Lint should not just generate reports — it must track issues and verify fixes:

1. **Issue Tracker** — Maintain `99-system/lint-reports/issues-tracker.md`:
   - Record each issue with ID, type, status (`open`/`in_progress`/`resolved`/`wontfix`)
   - Compare new lint results against tracker on each run
   - Update status: fixed → `resolved`, new → `open`, still present → `open`

2. **Escalation Rules**:
   - P0 issues unresolved for 2 consecutive lints → escalate alert
   - All issues resolved → send "✅ 知识库健康检查通过"
   - New critical issues → immediate alert

3. **Auto-Fix Scripts** — Use `scripts/fix-knowledge-issues.py` for common fixes:
   ```bash
   # Preview fixes (dry run)
   python3 ~/.hermes/scripts/fix-knowledge-issues.py --wiki $WIKI_PATH --fix broken-links --dry-run
   
   # Apply fixes
   python3 ~/.hermes/scripts/fix-knowledge-issues.py --wiki $WIKI_PATH --fix broken-links
   
   # Fix all fixable issues
   python3 ~/.hermes/scripts/fix-knowledge-issues.py --wiki $WIKI_PATH --fix all
   ```

4. **Report Retention** — Archive lint reports in `99-system/lint-reports/`:
   - Format: `lint-report-YYYY-MM-DD.md`
   - Include trend comparison (new/resolved/unresolved counts)

### Kanban 双向同步集成

Brain OS 使用 `kanban-sync.py` 实现 todo 与 Kanban 的双向同步：

```bash
# 写入 todo 模式：从任务输出写入 todo-backlog.md
python3 ~/.hermes/scripts/kanban-sync.py --task <task_name> --write-todo --output <output_file>

# 读取 todo 模式：从 todo 创建 Kanban 卡片
python3 ~/.hermes/scripts/kanban-sync.py --task <task_name> --read-todo

# 更新 todo 模式：Kanban 状态变更回写 todo
python3 ~/.hermes/scripts/kanban-sync.py --task <task_name> --update-todo
```

**⚠️ 任务配置维护（CRITICAL）：**
`kanban-sync.py` 中的 `TASK_CONFIG` 字典必须与 cron 任务保持同步。添加新任务时：
1. 在 `TASK_CONFIG` 中添加任务配置（name, tracker, issue_pattern, default_severity）
2. 在 `cron/jobs.json` 中创建对应的 cron 任务
3. 验证 `--help` 输出包含新任务名称

**可用任务列表：**
| 任务 key | 任务名称 |
|----------|----------|
| `observer-self-check` | 每日观察者自检 |
| `lint` | 周一知识库 Lint |
| `article-integration` | 夜间文章整合 |
| `dialogue-mining` | 夜间对话挖掘 |
| `knowledge-amplifier` | 夜间知识放大器 |
| `weekly-plan` | 每周计划 |
| `monthly-summary` | 月度总结 |
| `chronicle` | 史官记录 |
| `auto-commit` | 自动提交巡检 |
| `kanban-manager` | Kanban 管理层 |
| `daily-brief` | 每日早报 |
| `noon-reminder` | 午间待办提醒 |
| `evening-reminder` | 晚间待办提醒 |

## Brain OS 目录结构变体

Brain OS 项目在 llm-wiki 标准结构基础上扩展了编号体系，详见 `references/brain-os-directory-structure.md`。

**标准编号方案：**
| 编号 | 目录 | 用途 |
|------|------|------|
| 00 | raw | Layer 1: 原始来源 |
| 01-04 | entities/concepts/comparisons/queries | Layer 2: 知识库核心 |
| 05-08 | outputs/context/config/archive | 扩展层 |
| 09 | personal-ops | 个人运营 |
| 99 | system | 系统运营（基础设施） |

**根级文件（不应放入编号子目录）：**
- `SCHEMA.md` - 知识库规范
- `index.md` - 内容索引
- `log.md` - 操作日志

**⚠️ 编号冲突检查（CRITICAL）：**
创建新目录前必须检查编号唯一性：
```bash
# 检查编号冲突
for d in */; do
  num=$(echo "$d" | grep -oE '^[0-9]{2}')
  if [ -n "$num" ]; then
    count=$(ls -d ${num}-*/ 2>/dev/null | wc -l)
    if [ "$count" -gt 1 ]; then
      echo "❌ 编号 $num 冲突: $(ls -d ${num}-*/)"
    fi
  fi
done
```

**⚠️ 路径引用同步（CRITICAL）：**
修改目录结构后，必须同步更新以下文件：
1. `cron/jobs.json` - 所有 cron 任务 prompt 中的路径引用
2. `SCHEMA.md` - 目录结构说明
3. `index.md` - 内容索引中的路径
4. `scripts/kanban-sync.py` - TASK_CONFIG 中的任务配置

**⚠️ 中文目录规范：**
- 目录名：英文（符合 llm-wiki 规范）
- 文件名：中文（用户可读性优先）
- 子目录名：英文（避免嵌套中文）

---

## Related Tools

[llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler) is a Node.js CLI that
compiles sources into a concept wiki with the same Karpathy inspiration. It's Obsidian-compatible,
so users who want a scheduled/CLI-driven compile pipeline can point it at the same vault this
skill maintains. Trade-offs: it owns page generation (replaces the agent's judgment on page
creation) and is tuned for small corpora. Use this skill when you want agent-in-the-loop curation;
use llmwiki when you want batch compile of a source directory.

## Support Files

- `scripts/wiki-lint.py` — Automated lint script for health checks
- `scripts/fix-knowledge-issues.py` — Auto-fix script for broken links and frontmatter
- `references/knowledge-base-lint-findings-2026-05-18.md` — Baseline lint findings for `/root/.hermes/knowledge`
- `references/brain-os-directory-structure.md` — Brain OS 编号体系与目录结构规范
- `references/brain-os-test-workflow.md` — Brain OS 数据流闭环测试工作流
- `scripts/kanban-sync.py` — Kanban 双向同步脚本（todo ↔ Kanban 卡片）
