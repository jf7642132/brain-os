# PM Skills Marketplace — Full Reference

**Source**: https://github.com/phuryn/pm-skills
**Author**: Paweł Huryn (pawel@productcompass.pm)
**License**: MIT

## Status ✅ 全部已安装

All 65 skills have been installed as **individual Hermes Agent SKILL.md files** under their respective categories:
- product-discovery/ (13)
- product-strategy/ (12)
- product-execution/ (15)
- market-research/ (7)
- data-analytics/ (3)
- go-to-market/ (6)
- marketing-growth/ (5)
- pm-toolkit/ (4)

Do NOT use this reference file for execution — load the specific skill (e.g. `skill_view('pre-mortem')`) instead.

## Structure

100+ agentic skills, 36 chained workflows, 8 installable plugins. Designed for Claude Code / Claude Cowork, with compatibility for Gemini CLI, OpenCode, Cursor, Codex CLI, Kiro.

## 8 Plugins

### 1. pm-product-discovery (13 skills)
brainstorm-ideas-existing, brainstorm-ideas-new, brainstorm-experiments-existing, brainstorm-experiments-new, identify-assumptions-existing, identify-assumptions-new, prioritize-assumptions, prioritize-features, analyze-feature-requests, opportunity-solution-tree, interview-script, summarize-interview, metrics-dashboard
**Commands**: `/discover`, `/brainstorm`, `/triage-requests`, `/interview`, `/setup-metrics`

### 2. pm-product-strategy (12 skills)
product-strategy, startup-canvas, product-vision, value-proposition, lean-canvas, business-model, monetization-strategy, pricing-strategy, swot-analysis, pestle-analysis, porters-five-forces, ansoff-matrix
**Commands**: `/strategy`, `/business-model`, `/value-proposition`, `/market-scan`, `/pricing`

### 3. pm-execution (15 skills)
create-prd, brainstorm-okrs, outcome-roadmap, sprint-plan, retro, release-notes, pre-mortem, stakeholder-map, summarize-meeting, user-stories, job-stories, wwas, test-scenarios, dummy-dataset, prioritization-frameworks
**Commands**: `/write-prd`, `/plan-okrs`, `/transform-roadmap`, `/sprint`, `/pre-mortem`, `/meeting-notes`, `/stakeholder-map`, `/write-stories`, `/test-scenarios`, `/generate-data`

### 4. pm-market-research (7 skills)
user-personas, market-segments, user-segmentation, customer-journey-map, market-sizing, competitor-analysis, sentiment-analysis
**Commands**: `/research-users`, `/competitive-analysis`, `/analyze-feedback`

### 5. pm-data-analytics (3 skills)
sql-queries, cohort-analysis, ab-test-analysis
**Commands**: `/write-query`, `/analyze-cohorts`, `/analyze-test`

### 6. pm-go-to-market (6 skills)
gtm-strategy, beachhead-segment, ideal-customer-profile, growth-loops, gtm-motions, competitive-battlecard
**Commands**: `/gtm`, `/beachhead`, `/battlecard`

### 7. pm-marketing-growth (skills tbd)
marketing-ideas, value-proposition-statements, north-star-metrics, product-naming, positioning

### 8. pm-toolkit (utility)
resume-review, nda-drafting, privacy-policy, grammar-check

## Key Philosophy Quotes

> "Generic AI gives you text. PM Skills Marketplace gives you structure. Each skill encodes a proven PM framework — discovery, assumption mapping, prioritization, strategy — and walks you through it step by step."

> "Never allow customers to design solutions. Prioritize opportunities (problems), not features."

> "Multiple outputs may achieve one outcome; focus on the outcome, not the feature list."

## How Commands Work

Commands chain multiple skills. Example: `/discover` chains: brainstorm-ideas → identify-assumptions → prioritize-assumptions → brainstorm-experiments. After any command completes, it suggests relevant next commands.

## Compatibility

| Tool | Method | What works |
|------|--------|------------|
| Claude Code (CLI) | Clone repo, add to config | All 8 plugins |
| Claude Cowork | GitHub integration: phuryn/pm-skills | All 8 plugins |
| Gemini CLI | Copy to .gemini/skills/ | Skills only |
| OpenCode | Copy to .opencode/skills/ | Skills only |
| Cursor | Copy to .cursor/skills/ | Skills only |
| Codex CLI | Copy to .codex/skills/ | Skills only |
| Kiro | Copy to .kiro/skills/ | Skills only |
