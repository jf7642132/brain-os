# Cron Terminal `cd` Pitfall — Session Reference

## Problem

In cron jobs, the `cron-git-state-monitoring` skill workflow assumes:

```bash
cd /root/.hermes/knowledge
# ... later in a separate terminal() call ...
git status
```

**This fails** because each `terminal()` invocation spawns a fresh shell. The `cd` from the first call is lost.

## Evidence from Session (2026-05-19)

```
# First call: cd /root/.hermes/knowledge && pwd
# Output: /root/.hermes/knowledge ✓

# Second call: git status
# Output: fatal: not a git repository (or any of the parent directories): .git ✗
```

The `.git` directory EXISTS at `/root/.hermes/knowledge/.git`, but git couldn't find it because the working directory wasn't set.

## Solutions

### Solution 1: Chain Commands (Simplest)

```bash
cd /root/.hermes/knowledge && git status && git status --porcelain && git diff HEAD --stat
```

All commands run in the same shell, so `cd` persists.

### Solution 2: Explicit Git Flags (Most Robust)

```bash
REPO_DIR="/root/.hermes/knowledge"
GIT_DIR="$REPO_DIR/.git"

GIT_DIR="$GIT_DIR" git --git-dir="$GIT_DIR" --work-tree="$REPO_DIR" status
```

Works even if the shell context changes.

### Solution 3: Use `workdir` Parameter

```python
terminal(command="git status", workdir="/root/.hermes/knowledge")
```

The terminal tool sets the working directory for that specific call.

## Recommendation

For cron jobs with multiple verification steps:
- Use **Solution 1** (chained commands) for simple single-call checks
- Use **Solution 2** (explicit flags) for multi-call workflows where you need to run different commands in separate calls
- Use **Solution 3** (`workdir`) when using `execute_code` or programmatically calling terminal

## Why This Matters

The original skill workflow was designed assuming sequential `cd` then `git status` would work. In interactive sessions (single shell), this is fine. In cron jobs (multiple isolated `terminal()` calls), this assumption breaks.

This lesson was discovered during the 2026-05-19 nightly monitoring run and has been patched into the skill's "Edge Cases and Troubleshooting" section.
