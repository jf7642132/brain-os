---
name: product-audit-to-roadmap
description: "Comprehensive project audit → requirements gap analysis → structured PM requirement analysis (Q&A) → phased roadmap → persist to PM system. Chains SWOT, Pre-mortem, and structured discovery to produce an actionable project plan with milestones. Use when taking over an existing project, auditing an unclear initiative, or creating a first-class project plan from scratch."
---

# Product Audit → Roadmap Planning Workflow

## Purpose

You are a project manager taking over or auditing an existing project. The project has artifacts (issues, documents, goals) but lacks clear product direction, requirements completeness, or a prioritized execution plan. This skill chains multiple PM frameworks to produce a complete, actionable plan.

## When to Use

- Taking over a project with many existing Issues but unclear product direction
- User says "推进项目" or "制定项目计划" for an existing project
- Requirements feel incomplete or scattered across systems
- Need to surface risks and gaps the user hasn't considered
- Project needs milestones, phases, and success criteria

## Workflow Steps

### Step 1: Current State Audit

Gather all data from the project management system (Issues, Goals, Projects, Agents). Produce a health snapshot:

```
| Dimension | Data | Rating |
|-----------|------|--------|
| Team size | N Agents | ✅/🟡/🔴 |
| Total tasks | N Issues | ✅/🟡/🔴 |
| Completion rate | X% | ✅/🟡/🔴 |
| Blocked rate | X% | ✅/🟡/🔴 |
| Core workflows running? | Yes/No | ✅/🟡/🔴 |
```

**Look for**:
- High blocked rate (>30%) → likely infrastructure issue
- Stalled issues pattern (e.g., "Recover stalled issue" × many) → scheduler/system bug
- Backlog of fundamental setup tasks → incomplete onboarding

### Step 2: SWOT Analysis

Apply the `swot-analysis` skill. Focus on:
- What internal strengths can be leveraged for commercialization
- Infrastructure weaknesses that could break the product
- Market opportunities (customer pain points, competitive gaps)
- Threats (scheduler bugs, competitor moves, customer disinterest)

**Output**: 3-5 strategic recommendations (Build/Defend/Fix)

### Step 3: Pre-mortem Risk Analysis

Apply the `pre-mortem` skill. Categorize risks:
- **🐅 Tigers** (real risks that need action now)
- **🐘 Elephants** (unspoken concerns no one is discussing)
- **🧻 Paper Tigers** (overblown fears, don't waste time)

For each Tiger: Risk description → Mitigation → Owner → Priority (P0-P2)

### Step 4: Requirements Gap Analysis

Cross-reference existing Issues/Goals against a **complete product definition**. The gaps to check:

| Gap | Question to answer |
|-----|-------------------|
| **Customer** | Who exactly is the customer? Be specific, not a broad category |
| **Product form** | SaaS web app? Report push? Consulting? API? |
| **Value prop** | Save money? Make money? Save time? Prioritize |
| **Competition** | What are alternatives? How are we different? |
| **Success criteria** | What measurable outcome defines success? |

Flag each as ✅ (covered) or ❌ (missing). For missing gaps → mark as needing PM requirement analysis.

### Step 5: Structured PM Requirement Analysis

For each missing gap, conduct a **structured Q&A session** with the user. **Do NOT present all gaps at once** — show the overview once, then ask one gap per message. Present options clearly:

```
**Gap #N: [Topic]**

We need to decide [question]. Here are the options:

A) [Option A] — [pros/cons]
B) [Option B] — [pros/cons]
C) [Option C] — [pros/cons]
D) 其他（你补充）

Which one fits your vision?
```

**Key technique**: Always include a "D) 其他（你补充）" option. Users with strong domain knowledge often have a unique vision that doesn't fit preset options. The "其他" option invites them to articulate their own idea rather than feeling constrained.

**Two-phase approach**: First present the full gap map as a summary ("I found 5 gaps, here they are"), then resolve them one at a time in subsequent messages. This gives the user context without overwhelming them.

**Confirm each decision** before moving to the next gap. Say "已记录 ✅" or similar to signal closure.

### Step 6: Assemble Product Definition

After all gaps are filled, compile a one-page product definition:

```
## Product Definition

**One-liner**: [compressed value prop]

**Target customer**: [specific segment, with expansion stages]

**Core capabilities**:
1. [Capability 1] — brief
2. [Capability 2] — brief

**Delivery form**: [SaaS/push/etc]

**Value prop**: [primary benefit] + [secondary benefit]

**Competitive differentiation**: [how we're different]
```

### Step 7: Phased Roadmap

Create a phased plan with milestones:

| Phase | Timeline | Goal | Key Deliverables |
|-------|----------|------|------------------|
| Phase 0: Fix | Week 1-2 | System stability | Scheduler fix, agent skills |
| Phase 1: Validate | Week 3-4 | Internal validation | Product entry, market analysis, first report |
| Phase 2: MVP | Month 2 | Demo-able product | SaaS frontend, API, push channels |
| Phase 3: Pilot | Month 3-5 | Customer validation | 3-5 free trials, feedback loop |
| Phase 4: Launch | Month 6+ | Revenue | Paid customers, success system |

For each phase, define:
- **Completion criteria** (checklist of what "done" means)
- **Gate decision** (what must be true to proceed to next phase)
- **Owner**

### Step 8: Define Success Metrics

Define a **North Star metric** — the single metric that captures the product's value to customers.

Examples:
- "Customer revenue generated through our recommendations"
- "Markets analyzed per customer per month"
- "Recommendation accuracy rate"

Add supporting metrics:
- Customer acquisition cost
- Monthly active users
- Report open rate

### Step 9: Persist to PM System

Write the plan into the project management system:

1. **Update the main Goal** with the new product direction
2. **Create Issues** for each Phase 0/1 deliverable (one issue per deliverable)
3. **Assign to appropriate agents/owners**
4. Set correct status (in_progress/todo/backlog)

API tip: For systems with CSRF protection, ensure the Origin header matches the server URL in mutation requests.

### Step 10: Save to Wiki/Docs

Write the complete plan to a document in the project's documentation directory. Structure:

```
project-name/
├── 产品定位与项目计划-YYYY-MM-DD.md    (the full plan)
├── 项目全面审计与计划-YYYY-MM-DD.md     (the audit report)
└── ...existing docs...
```

## Pitfalls

1. **Don't present all gaps at once** — users get overwhelmed. One gap per message.
2. **Don't use open-ended questions** — always provide structured options (A/B/C).
3. **Don't skip the blocker analysis** — high blocked rate almost always signals a system-level issue, not a task-level issue.
4. **Don't assume pricing** — validate even rough pricing with customer research.
5. **Don't create the plan before filling gaps** — the plan will be wrong if requirements aren't defined.
6. **Don't forget the API auth** — when persisting to Paperclip, you need Origin header for mutations, cookie-based session (not bearer token), and status code is 201 for create, not 200.

## User Preference Embedding

- The user who prompted this skill's creation prefers Chinese, structured analyses, and methodical phased approaches (validate → pilot → launch).
- Always present options, not blank pages. Users respond to structured choices.
- Flag risks proactively — the user appreciates being warned about things they didn't think of.
