# Brain OS Open Source Packaging Learnings

Session: 2026-05-18

## Project Details

- **Project**: Brain OS - 一套基于 Karpathy LLM Wiki 概念和 Obsidian-Brain-OS 设计灵感、结合 Hermes Kanban 任务管理的技能体系
- **Repository**: https://github.com/jf7642132/brain-os
- **License**: MIT

## Terminology Correction

**Issue**: Used "git-backed brain" terminology

**Correction**: "git-backed brain" is a design pattern inspired by Karpathy's LLM Wiki:
- A community Helm chart implementation
- A Reddit user's `clawbrain` project
- NOT an official term, but a design pattern

**Fix**: Use descriptive language: "git 驱动持久化设计" (git-driven persistence design)

**Lesson**: Always verify external project terminology before using it as a reference. Search official docs first.

## SVG Diagram Fixes

### Problem
Text overflow outside boxes in `brain-os-architecture-social.svg`

### Root Cause
Original box heights calculated for fewer items:
- Producer box: 180px height, 8 items → overflow
- Consumer box: 180px height, 3 items with 40px each → overflow
- Hub box: 120px height, 5 lines → overflow

### Fix Applied
```
Producer box: 180 → 220px (8 items × 20px + title + padding)
Consumer box: 180 → 220px (3 items × 40px + title + padding)
Hub box: 120 → 160px (5 lines × 20px + title + padding)
```

### Arrow Position Updates
After adjusting box heights, all connecting arrows needed y-coordinate updates:
- Producers → Hub: y 190 → 210
- Hub → Consumers: y 190 → 210
- Hub → Kanban: y 250 → 290

## README Structure Decision

**User preference**: Quick Install section should come BEFORE detailed architecture explanation.

**Reasoning**:
- "What is this" serves readers deciding whether to use
- "Quick Install" serves readers who already decided to use
- Standard open-source layout: value → action → details

**Implementation**:
```
Title + Subtitle
↓
What is this
↓
Quick Install (moved up)
↓
Core Architecture
↓
... rest of docs
```

## Agent Auto-Install Option

**Added to README**:
```markdown
### 方式一：让 Hermes 自动安装（推荐）

直接把仓库地址发给 Hermes，让它自己完成克隆、安装、导入定时任务：

> "安装 brain-os 技能：https://github.com/jf7642132/brain-os"
```

**Why**: Reduces friction for users who prefer agent-assisted workflows over manual CLI steps.

## Commits Made

1. `1ab83ab` - Fix terminology reference
2. `91d719a` - Move quick install section before architecture
3. `91a099f` - Add auto-install option via Hermes Agent
4. `cc23624` - Fix text overflow in architecture diagram