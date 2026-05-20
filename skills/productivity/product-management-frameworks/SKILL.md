---
name: product-management-frameworks
description: "[索引技能] PM框架快速索引 — 指向65个独立技能。strategy: product-strategy/* (12个); execution: product-execution/* (15个); discovery: product-discovery/* (13个); market research: market-research/* (7个); GTM: go-to-market/* (6个); monetization: product-strategy/monetization-strategy; data: data-analytics/* (3个); growth: marketing-growth/* (5个); toolkit: pm-toolkit/* (4个)。**不要直接用这个技能干活** — 加载具体技能(如pre-mortem)执行，这个只做索引和快速定位。"
---

# Product Management Frameworks

A comprehensive library of proven product management frameworks for making better product decisions — from discovery to strategy, execution, launch, and growth. Each framework encodes the rigor of Teresa Torres, Marty Cagan, Alberto Savoia, Geoffrey Moore, and other industry leaders, built directly into your workflow.

## When to Load This Skill

- Making a strategic product decision (what to build, for whom, why)
- Creating or reviewing a product roadmap
- Planning a GTM launch
- Analyzing competitors or market size
- Deciding on pricing/monetization model
- Prioritizing a backlog or initiative list
- Writing a PRD or product spec
- Setting quarterly OKRs
- Running a product discovery process
- Any time the user mentions frameworks like OST, SWOT, RICE, TAM/SAM/SOM

## Domain Organization

### 1. Product Discovery (探知)
Frameworks for understanding customer needs and validating solutions.

| Framework | Creator | Best For |
|-----------|---------|----------|
| **Opportunity Solution Tree (OST)** | Teresa Torres | Structuring continuous discovery — outcome → opportunities → solutions → experiments |
| **Assumption Testing** | Alberto Savoia | Validating riskiest assumptions before building |
| **Opportunity Score** | Dan Olsen | Prioritizing customer problems: Importance × (1 − Satisfaction) |
| **Job Stories / User Stories** | — | Framing features as jobs to be done, not spec lists |
| **Interview Script Design** | — | Structured customer interview protocols |

**Key principle**: Never let customers design solutions. Prioritize problems (opportunities), not features.

### 2. Product Strategy (战略)
Frameworks for defining product direction, vision, and competitive position.

| Framework | Best For |
|-----------|----------|
| **Product Strategy Canvas (9 sections)** | Full strategic plan: Vision → Segments → Costs → Value Props → Trade-offs → Metrics → Growth → Capabilities → Defensibility |
| **SWOT Analysis** | Internal/external strategic assessment |
| **PESTLE Analysis** | Macro-environmental factors (Political, Economic, Social, Tech, Legal, Environmental) |
| **Porter's Five Forces** | Industry competitive dynamics |
| **Ansoff Matrix** | Growth strategy (market penetration/development vs product development/diversification) |
| **Value Proposition Canvas** | Customer pains/gains → product features mapping |

**Key principle**: Strategy guides decisions; clarity enables faster execution. Revisit quarterly.

### 3. Execution (执行)
Frameworks for turning strategy into delivered outcomes.

| Framework | Best For |
|-----------|----------|
| **PRD Template (8 sections)** | Summary → Contacts → Background → Objective → Market Segments → Value Props → Solution → Release |
| **OKR Framework** | Qualitative objectives + 3 measurable key results per objective |
| **Outcome Roadmap** | Transforming output-focused roadmaps to outcome-focused (customer/business impact) |
| **Prioritization Frameworks (9)** | RICE, ICE, Kano, MoSCoW, Opportunity Score, Eisenhower, Impact vs Effort, Risk vs Reward, Weighted Decision Matrix |
| **Pre-mortem** | Identifying failure modes before they happen |
| **Stakeholder Map** | Influence/interest grid for stakeholder management |

**Key principle**: Outcome roadmaps are more resilient to change than feature roadmaps. Embrace flexibility.

### 4. Market Research (市场研究)
Frameworks for understanding markets, customers, and competitors.

| Framework | Best For |
|-----------|----------|
| **TAM/SAM/SOM** | Top-down + bottom-up market sizing |
| **Competitor Analysis (5-profile)** | Competitive landscape mapping + differentiation strategy |
| **User Personas** | Target user archetypes for design decisions |
| **Market Segmentation** | Segmenting by JTBD (not demographics) |
| **Customer Journey Map** | End-to-end experience mapping |

**Key principle**: Always provide both top-down and bottom-up estimates to triangulate market size.

### 5. Go-To-Market (上市)
Frameworks for launching products and acquiring first customers.

| Framework | Best For |
|-----------|----------|
| **Beachhead Segment Selection** | Choosing first niche market (Moore's Crossing the Chasm) — evaluate: pain point × willingness to pay × winnability × referral potential |
| **GTM Strategy (5-step)** | Channels → Messaging → Metrics → Launch Plan → Optimization |
| **Ideal Customer Profile (ICP)** | Defining the perfect first customer |
| **Growth Loops** | Viral/paid/content/sales-driven growth mechanics |
| **Competitive Battlecard** | Sales-facing competitive positioning docs |

**Key principle**: Start absurdly specific. Niche > vague mass market. Plan exit only after 60%+ market share in beachhead.

### 6. Monetization (变现)
Frameworks for revenue model design and validation.

| Model | Best Fit | Key Risk |
|-------|----------|----------|
| **Freemium** | High-volume, low-touch | Low conversion (1-5%) |
| **Subscription** | Continuous-value products | Churn |
| **Usage-based** | B2B APIs, variable-need | Unpredictable revenue |
| **Enterprise/Seat** | B2B SaaS teams | Sales complexity |
| **One-time purchase** | Niche tools | No recurring revenue |
| **Marketplace fee** | Platforms | Chicken-and-egg |
| **Advertising** | High-traffic consumer | UX degradation |

**Key principle**: Test early and often. Most successful products use hybrid models. Design a low-effort validation experiment for each candidate model before committing.

### 7. Data Analytics (数据分析)
| Framework | Best For |
|-----------|----------|
| **Cohort Analysis** | Retention patterns and user behavior segments |
| **AB Test Analysis** | Statistical significance, sample size, MDE calculation |

### 8. Marketing Growth (营销增长)
| Framework | Best For |
|-----------|----------|
| **North Star Metric** | Single customer-centric KPI that drives growth |
| **Product Naming & Positioning** | Market positioning statements |

## User Preferences

- **Use Chinese for all output**. Communicate in clear, concise Chinese.
- **Apply frameworks directly** — don't explain framework theory unless asked; use them to produce structured output.
- **Tie every framework application back to the project's business goals**. If applying a PM framework, always include a brief "so what does this mean for us" section.
- **Prefer action-oriented output** — frameworks are tools for decisions, not academic exercises.
- **When multiple frameworks apply**, choose the most directly relevant one, not the most comprehensive one.

## References

- `references/pm-skills-marketplace.md` — Full reference of the PM Skills Marketplace (phuryn/pm-skills) including all 8 plugins, 65+ skills, and 36 commands  
  **现状：所有 65 个技能已作为独立 Hermes SKILL.md 安装**，位于各自分类目录下（product-discovery/*, product-strategy/*, product-execution/* 等）。**不要只用这个索引技能** — 需要用时加载具体技能（如 `skill_view('pre-mortem')`）。

- `references/product-strategy-canvas.md` — Full 9-section Product Strategy Canvas template (vision, segments, costs, value props, trade-offs, metrics, growth, capabilities, defensibility)
- `references/project-health-check-workflow.md` — 项目全面审计工作流（数据采集→健康诊断→SWOT→Pre-mortem→需求缺口→里程碑→决策→沉淀） — Beachhead segment selection criteria and process (Geoffrey Moore)
- `references/monetization-strategies.md` — 7 monetization models with evaluation framework and 6-step process

## Templates

- `templates/prd.md` — Product Requirements Document template (8 sections: summary, contacts, background, objective, segments, value props, solution, release)
- `templates/swot-analysis.md` — SWOT analysis worksheet with cross-reference matrix
- `templates/opportunity-solution-tree.md` — OST template (outcome → opportunities → solutions → experiments)

## Framework Application Guide

The PM frameworks are NOT academic exercises — each one has a specific trigger and output in our workflow:

| Trigger | Framework | Output |
|---------|-----------|--------|
| User says "我们要做这个新产品" | Product Strategy Canvas (9 sections) | Complete strategy document |
| User says "需求太多不知道怎么排" | OST + Opportunity Score | Prioritized problem list |
| User says "这季度目标是什么" | OKR + Outcome Roadmap | Outcome-driven quarterly plan |
| User says "第一批客户去哪找" | Beachhead Selection | ICP + customer acquisition plan |
| User says "怎么定价" | Monetization Framework | Pricing plan + validation experiment |
| User says "竞争对手怎么样" | Competitor Analysis | 5-competitor profile + differentiation |
| User says "市场有多大" | TAM/SAM/SOM (top-down + bottom-up) | Market sizing + reachable share |
| User says "有什么风险" | SWOT + Pre-mortem | Risk matrix + mitigation plan |
| User says "帮我全面审计项目/制定项目计划" | Project Health Check (SWOT + Pre-mortem + Gap Analysis) | 项目状态报告 + 风险矩阵 + 需求缺口 + 里程碑 + 决策建议 |

## Command Chains (Multi-Framework Workflows)

Chaining multiple frameworks produces better results than using any single one:

**GTM Planning Chain**: TAM/SAM/SOM → Beachhead Selection → Competitor Analysis → Value Proposition → GTM Strategy → Monetization Strategy
**Quarterly Planning Chain**: SWOT → Strategy Canvas → OKR → Outcome Roadmap → OST → Prioritization
**Discovery Chain**: Desired Outcome → Opportunity Identification → Solution Generation → Experiment Design → Metrics
**Project Audit Chain**: SWOT → Pre-mortem → Gap Analysis → Outcome Roadmap → Issue Creation
  - 1. **SWOT**: 评估项目内外部环境（优势/劣势/机会/威胁）
  - 2. **Pre-mortem**: 预判风险（Tigers/Paper Tigers/Elephants 分类）
  - 3. **Gap Analysis**: 比对现有 Issue/Goal 覆盖度，识别5类缺口（客户/产品形态/价值主张/竞品/成功标准）
  - 4. **Outcome Roadmap**: 将输出清单转化为结果导向的里程碑
  - 5. **Issue Creation**: 将计划落地到Paperclip/项目管理系统的 Issue 树

## Further Reading

- [Product Compass by Paweł Huryn](https://www.productcompass.pm) — Source of most frameworks above
- [Continuous Discovery Habits by Teresa Torres](https://www.producttalk.org)
- [Inspired by Marty Cagan](https://www.svpg.com)
- [Crossing the Chasm by Geoffrey Moore](https://en.wikipedia.org/wiki/Crossing_the_Chasm)
- [The Lean Product Playbook by Dan Olsen](https://www.leanproductplaybook.com)
