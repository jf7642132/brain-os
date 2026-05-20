---
name: hongguo-short-drama-script-writing
category: creative
description: Complete workflow for adapting web novel IP into Hongguo short drama scripts for AI animated series
---

# Hongguo Short Drama Script Writing Workflow

## Overview
Complete workflow for adapting web novel IP into Hongguo short drama scripts for AI animated series (AI 漫剧).

## Project Setup
1. **Register as Screenwriter**: Sign up on Hongguo platform (https://ss.huoguoapp.com/)
2. **Create Project Structure**:
   ```
   /root/.hermes/projects/{project_name}/
   ├── original/      # Original web novel IP files
   ├── script/        # Adapted script drafts
   └── output/        # Final approved scripts
   ```

## Workflow Rules
- **Script Length**: 800-1000 Chinese characters per episode (approx. 3 minutes AI animation)
- **Episode Numbering**: Must be continuous (1, 2, 3...) - NO renumbering
- **Content**: Strictly follow original text, NO original plot additions
- **Ending**: Each episode must end with a suspense hook/cliffhanger
- **Format**: AI animated series (NOT live-action short drama)

## Team Roles
1. **Total Manager (总管家)**: Project organizer, decomposes tasks, coordinates workflow
2. **Scriptwriter Assistant (编剧助理)**: Adapts original text into script format
3. **Proofreader Assistant (核稿助理)**: 
   - Verify content matches original chapter
   - Check continuity with previous episode
   - Ensure Hongguo specifications compliance
   - Confirm no unauthorized additions

## Process
1. **Read Original Text**: Load current chapter from `original/` folder
2. **Scriptwriter Adapts**: Convert to script format with:
   - Scene descriptions
   - Dialogue
   - Action cues
   - Cliffhanger ending
3. **Proofreader Reviews**: 
   - Line-by-line comparison with original
   - Continuity check
   - Format validation
   - Word count verification (800-1000)
4. **User Approval**: Final confirmation only
5. **Archive to Output**: Save approved script to `output/`

## Key Constraints
- NO creative additions beyond original text
- Maintain episode sequence continuity
- Strict word count limits
- Professional script formatting
- Cliffhanger at every episode end

## Tools Used
- `hongguo-short-drama-adaptation` skill for script formatting
- `hongguo-short-drama-delegation` skill for team coordination
- `hongguo-short-drama-requirements` skill for specification reference