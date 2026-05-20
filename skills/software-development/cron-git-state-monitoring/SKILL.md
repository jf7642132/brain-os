---
name: cron-git-state-monitoring
description: "Autonomous git repository monitoring and auto-commit for scheduled cron jobs — comprehensive state checking, smart commit triggering, and SILENT response patterns"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cron, git, monitoring, automation, scheduled-jobs, devops]
    related_skills: [github-repo-management, systematic-debugging, subagent-driven-development]
---

# Cron Git State Monitoring

**Use when:** you need to autonomously monitor git repositories as a scheduled cron job, check for uncommitted changes, and auto-commit when finds them.

**Pattern:** This skill encapsulates the complete workflow for Hermes Agent operating as a Review Agent in scheduled cron jobs, where:
- The agent must execute fully autonomously (no user present to ask questions)
- Must make reasonable decisions where needed
- Must return `[SILENT]` when there's genuinely nothing to report
- Must handle git state checking comprehensively to avoid false positives

## Core Principles

1. **Autonomous Execution**: No user interaction possible in cron jobs — make reasonable assumptions and proceed.
2. **Silent Mode**: Return exactly `[SILENT]` (nothing else) when no actionable findings to suppress delivery.
3. **Comprehensive Checking**: Multiple layers of git verification to avoid false positives.
4. **Safe Auto-Commit**: Only commit actual changes, not just timestamp differences.
5. **Informative Reports**: When changes found and committed, provide clear report for review.

## Trigger Conditions

- Running as a scheduled cron job (user not present)
- Task involves checking git repository state
- Need to auto-commit any uncommitted changes
- Working with wiki directories, documentation repos, or content repositories

## Workflow Steps

### 1. Initial Setup and Directory Navigation

**⚠️ Critical Pitfall: `cd` does NOT persist across separate `terminal()` calls in cron jobs**

Each `terminal()` invocation spawns a fresh shell. A `cd` in one call is lost in the next. Use one of these approaches:

**Option A: Chain all commands in a single terminal call (recommended for simple checks)**
```bash
cd /target/repository/path && git status && git status --porcelain && git diff HEAD --stat
```

**Option B: Use explicit `--git-dir` and `--work-tree` flags (recommended for multi-call workflows)**
```bash
# Set these variables for all subsequent git commands
REPO_DIR="/target/repository/path"
GIT_DIR="$REPO_DIR/.git"

# Then use:
GIT_DIR="$GIT_DIR" git --git-dir="$GIT_DIR" --work-tree="$REPO_DIR" status
GIT_DIR="$GIT_DIR" git --git-dir="$GIT_DIR" --work-tree="$REPO_DIR" status --porcelain
```

**Option C: Use `workdir` parameter in terminal() calls**
```python
# In execute_code or when calling terminal with workdir:
terminal(command="git status", workdir="/target/repository/path")
```

### 2. Multi-Layer Git State Verification

Do NOT rely on just `git status`. Use these commands in sequence:

```bash
# Layer 1: Basic status check
git status

# Layer 2: Porcelain format for programmatic checking
git status --porcelain

# Layer 3: Check for actual diffs against HEAD
git diff HEAD --stat

# Layer 4: Check individual file diffs
git diff --name-only

# Layer 5: Check for untracked files (including ignored patterns)
git status -uall

# Layer 6: Check recently modified files (supplemental, not definitive)
find . -type f -mmin -1440 -name "*.md" -o -type f -mmin -1440 -name "*.txt" -o -type f -mmin -1440 -name "*.json" -o -type f -mmin -1440 -name "*.yaml" -o -type f -mmin -1440 -name "*.yml" | head -15
```

### 3. Avoid False Positives Pitfalls

**Pitfall 1:** File modification times ≠ git changes
- Files can have newer timestamps but identical content
- Always check `git diff` not just file timestamps

**Pitfall 2:** .gitignore patterns hiding files
- Use `git ls-files --others --exclude-standard` to see truly untracked files
- Check for .gitignore files that might hide changes

**Pitfall 3:** Already committed recent changes
- Check last commit timestamp: `git log -1 --format="%cd" --date=format:"%Y-%m-%d %H:%M"`
- Compare with current time to avoid duplicate commits in short windows

### 4. Decision Logic for Auto-Commit

Only commit when ALL of these conditions are met:

1. `git status --porcelain` returns non-empty output, OR
2. `git diff HEAD --stat` returns non-empty output, OR  
3. `git diff --name-only` returns non-empty output

AND

4. Changes are NOT already in staging (check `git diff --cached`)
5. Files are NOT in .gitignore (verified via multiple checks)

### 5. Auto-Commit Process

If changes are found:

```bash
# Add all changes (including untracked files)
git add .

# Create informative commit message with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "auto: nightly pipeline updates $TIMESTAMP"

# Optional: Get commit hash for reporting
COMMIT_HASH=$(git rev-parse --short HEAD)
```

### 6. Report Structure

When changes found and committed:

```
## Git State Monitoring Report

**Check Time**: YYYY-MM-DD HH:MM

### 1. Status Summary
- Changes Found: Yes/No
- Files Modified: [list or count]
- Action Taken: [Committed/Silent]

### 2. Commit Details (if committed)
- Commit Hash: abc123
- Commit Message: "auto: nightly pipeline updates YYYY-MM-DD HH:MM"
- Changed Files: [list from git status --porcelain]

### 3. Verification Steps
[Brief summary of checks performed]
```

When no changes found:

```
[SILENT]
```

## SILENT Mode Implementation

**Critical:** In cron jobs, your response is automatically delivered. To suppress delivery when there's truly nothing to report:

```python
# When ALL checks pass with no changes:
return "[SILENT]"
```

**Rules for SILENT:**
- NEVER combine `[SILENT]` with content — it's either a full report or `[SILENT]` alone
- Only use when verification confirms no changes at all
- When in doubt, provide a minimal report rather than silent

## Example Session Pattern

```bash
# Navigate
cd /root/wiki

# Check status (all layers)
git status
git status --porcelain
git diff HEAD --stat
git diff --name-only
git status -uall

# If all clean
echo "[SILENT]"

# If changes found
git add .
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
git commit -m "auto: nightly pipeline updates $TIMESTAMP"

# Generate report
echo "## Git State Monitoring Report"
echo "**Check Time**: $TIMESTAMP"
echo "### 1. Status Summary"
echo "- Changes Found: Yes"
echo "- Action Taken: Committed"
echo "### 2. Commit Details"
echo "- Commit Hash: $(git rev-parse --short HEAD)"
```

## Integration with Other Skills

### With `github-repo-management`
Use `github-repo-management` for advanced GitHub operations, API calls, and repository management. This skill focuses specifically on local git state monitoring for automated jobs.

### With `systematic-debugging`
When encountering git issues or unexpected states, apply the 4-phase debugging methodology from `systematic-debugging`.

### With `subagent-driven-development`
For complex monitoring scenarios, consider delegating different aspects to specialized subagents.

## Edge Cases and Troubleshooting

### 1. `cd` Does Not Persist Across Terminal Calls (CRITICAL)

**Symptom**: `cd /path && git status` works, but separate `terminal("cd /path")` followed by `terminal("git status")` fails with "not a git repository".

**Cause**: Each `terminal()` call spawns a fresh shell. `cd` is lost between calls.

**Fix**:
- **Option A**: Chain commands in a single `terminal()` call: `cd /path && git status`
- **Option B**: Use explicit `--git-dir` and `--work-tree` flags: `GIT_DIR=/path/.git git --git-dir=/path/.git --work-tree=/path status`
- **Option C**: Use `workdir` parameter: `terminal(command="git status", workdir="/path")`

### 2. Detached HEAD State
```bash
git rev-parse --abbrev-ref HEAD
# If returns "HEAD", you're in detached state
git checkout main  # or appropriate branch
```

### 2. Large File Warnings
```bash
# Check for git-lfs or large file issues
git lfs status
```

### 3. Permission Issues
```bash
# Ensure write permissions
ls -la .git/
```

### 4. Recent Commit Check
```bash
# Avoid duplicate commits within short timeframes
LAST_COMMIT=$(git log -1 --format="%cd" --date=format:"%Y-%m-%d %H:%M")
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M")
# If less than 30 minutes, consider suppressing
```

## Quality Gates

Before finalizing:
1. **Verify git state is truly dirty** (not just timestamp differences)
2. **Ensure commit message is informative** with timestamp
3. **Check for any git errors** in command outputs
4. **Confirm SILENT mode only when appropriate**

## References

- `references/git-state-verification-sequence.md` - Complete verification command sequence and decision logic
- `references/git-skill-differentiation.md` - Clarifies when to use this skill vs other git-related skills
- `references/cron-job-response-patterns.md` - Critical patterns for autonomous cron job execution and SILENT mode
- `references/cron-terminal-cd-pitfall.md` - **Critical**: Why `cd` doesn't persist across terminal() calls in cron jobs and how to fix it
- For additional scheduled job patterns and best practices, see cron-related skills in the skill library