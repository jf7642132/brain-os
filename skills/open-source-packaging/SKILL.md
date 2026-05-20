---
name: open-source-packaging
category: devops
version: 1.0.0
description: Packaging internal tools/projects for public release on GitHub/GitLab
---

# Open Source Project Packaging

Packaging internal tools/projects for public release on GitHub/GitLab.

## Trigger Conditions

- User wants to open-source an internal project
- Creating or updating README.md for public release
- Creating architecture diagrams for documentation
- Adding installation instructions for multiple platforms

## Workflow

### 1. README Structure (Standard Order)

```
Title + Subtitle (one-line value proposition)
↓
What is this (brief explanation, 2-3 sentences)
↓
Quick Install (immediately actionable, before deep details)
↓
Core Architecture (diagrams + explanation)
↓
Core Components (detailed breakdown)
↓
Running Logic / Usage
↓
Configuration
↓
Comparison with alternatives
↓
License
↓
Acknowledgments
```

**Key principle**: Users who decide to use should see installation immediately. Don't bury it after 10KB of documentation.

### 2. SVG Architecture Diagrams

When creating SVG diagrams with text boxes:

**Common pitfall: Text overflow outside boxes**

Fix pattern:
1. Calculate required height: `title_height + (items × item_spacing) + padding`
2. Set box height to match (or add 20-40px buffer)
3. Adjust all y-coordinates for text elements to fit within new height
4. Update arrow positions to connect at new box boundaries (center y-axis)

Example calculation for 8 items with 20px spacing:
- Title: 25px
- Items: 8 × 20px = 160px
- Padding: 20px
- Total: ~205px → use 220px for safety

### 3. Terminology Verification

Before using terms that reference external projects:
- Search official docs of referenced project
- Verify the term exists officially
- If unofficial, use descriptive language instead (e.g., "git 驱动持久化设计" instead of "git-backed brain")

### 4. Agent Auto-Install Option

For skills/tools that can be installed by an AI agent:

```markdown
### 方式一：让 [Agent Name] 自动安装（推荐）

直接把仓库地址发给 [Agent Name]，让它自己完成克隆、安装、导入定时任务：

> "[安装指令]：https://github.com/username/repo"

### 方式二：手动安装

```bash
# 手动步骤
```
```

This reduces friction for users who prefer agent-assisted workflows.

## Pitfalls

- **Don't delete useful sections** - "Quick Install" and "What is this" serve different readers (action vs understanding)
- **Don't use unofficial terminology** - verify before claiming something is "official"
- **SVG boxes need proper height calculation** - don't guess, calculate based on content
- **Arrow positions must match box boundaries** - after adjusting box heights, update all connecting arrows

## Verification Steps

- [ ] README structure follows standard order
- [ ] Quick install section is visible before detailed docs
- [ ] SVG diagrams have no text overflow (check all boxes)
- [ ] All external references are verified against official docs
- [ ] Agent auto-install option included (if applicable)

## Reference Files

- [references/brain-os-learnings.md](references/brain-os-learnings.md) - Session-specific learnings from Brain OS open-source packaging (2026-05-18)