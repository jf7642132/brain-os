# Git State Verification Sequence

This reference file captures the exact verification sequence from the successful cron job session, showing how to comprehensively check git state without false positives.

## Complete Verification Command Sequence

### Phase 1: Basic Status Checks
```bash
# 1. Standard status (human readable)
git status

# 2. Porcelain format (programmatic parsing)
git status --porcelain

# 3. Check diffs against HEAD
git diff HEAD --stat

# 4. List changed files specifically
git diff --name-only

# 5. Most detailed status (includes ignored patterns)
git status -uall
```

### Phase 2: Untracked File Detection
```bash
# Check for truly untracked files (excluding .gitignore patterns)
git ls-files --others --exclude-standard

# Check for .gitignore files that might affect detection
find . -type f -name ".gitignore" -exec cat {} \; 2>/dev/null
```

### Phase 3: Recent Modification Analysis
```bash
# Find recently modified markdown/docs files (last 24 hours)
find . -type f -mmin -1440 \
  -name "*.md" -o \
  -type f -mmin -1440 -name "*.txt" -o \
  -type f -mmin -1440 -name "*.json" -o \
  -type f -mmin -1440 -name "*.yaml" -o \
  -type f -mmin -1440 -name "*.yml" | head -15

# More specific: files modified since last commit
LAST_COMMIT_TIME=$(git log -1 --format="%cd" --date=format:"%Y-%m-%d %H:%M")
find . -type f -newermt "$LAST_COMMIT_TIME" \
  -name "*.md" -o \
  -type f -newermt "$LAST_COMMIT_TIME" -name "*.txt" -o \
  -type f -newermt "$LAST_COMMIT_TIME" -name "*.json" -o \
  -type f -newermt "$LAST_COMMIT_TIME" -name "*.yaml" -o \
  -type f -newermt "$LAST_COMMIT_TIME" -name "*.yml" 2>/dev/null | head -10
```

### Phase 4: Historical Context
```bash
# Check recent commit history
git log --oneline -5

# Check specific file commit history
git log --oneline -- ./path/to/file.md

# Get last commit timestamp
git log -1 --format="%cd" --date=format:"%Y-%m-%d %H:%M"
```

### Phase 5: File System State
```bash
# List key file types with modification times
for file in $(find . -type f \
  -name "*.md" -o \
  -name "*.txt" -o \
  -name "*.json" -o \
  -name "*.yaml" -o \
  -name "*.yml" 2>/dev/null | head -30); do
  file_time=$(stat -c "%Y" "$file" 2>/dev/null)
  if [ -n "$file_time" ]; then
    file_date=$(date -d "@$file_time" "+%Y-%m-%d %H:%M" 2>/dev/null)
    echo "$file_date - $file"
  fi
done | sort -r | head -10
```

## Decision Matrix

### When to Return [SILENT]
Return `[SILENT]` when ALL of these are true:
1. `git status --porcelain` is empty
2. `git diff HEAD --stat` is empty
3. `git diff --name-only` is empty
4. `git status -uall` shows "nothing to commit"
5. `git ls-files --others --exclude-standard` is empty

### When to Auto-Commit
Commit when ANY of these are true:
1. `git status --porcelain` returns non-empty output (any lines)
2. `git diff HEAD --stat` shows changed files
3. `git diff --name-only` lists files

AND verify:
- Changes are not already staged (`git diff --cached`)
- Files are not in .gitignore (cross-check with `find .gitignore`)

## Timestamp Pattern Analysis

From the session:
- Last commit: 2026-05-14 14:00
- Current time: 2026-05-14 16:02
- Gap: 2 hours 2 minutes

**Rule of thumb:** If last commit was less than 30 minutes ago, be extra stringent in verification to avoid duplicate commits.

## Common False Positive Scenarios

### 1. Timestamp-Only Changes
Files showing in `find -mmin` but not in `git diff` - these are likely timestamp-only changes.

**Solution:** Always verify with `git diff` before committing.

### 2. .gitignore Patterns
Files that exist but are intentionally ignored.

**Solution:** Check `.gitignore` contents and use `git status -uall` to see them.

### 3. Permission Changes
File permission changes that don't affect content.

**Solution:** `git diff` doesn't show permission changes by default, use `git diff --summary` if needed.

## Report Template

```bash
#!/bin/bash

REPORT_TITLE="Git State Monitoring Report"
CHECK_TIME=$(date "+%Y-%m-%d %H:%M")

git_changes=$(git status --porcelain)
git_diff=$(git diff HEAD --stat)

if [ -z "$git_changes" ] && [ -z "$git_diff" ]; then
  echo "[SILENT]"
  exit 0
fi

echo "## $REPORT_TITLE"
echo ""
echo "**Check Time**: $CHECK_TIME"
echo ""
echo "### 1. Git Status Summary"
echo "- Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "- Last Commit: $(git log -1 --format=\"%cd\" --date=format:\"%Y-%m-%d %H:%M\")"
echo "- Changes Found: Yes"
echo ""
echo "### 2. Changes Detected"
echo '```'
git status
echo '```'
echo ""
echo "### 3. Auto-Commit Action"
echo "Changes have been committed locally."
echo "- Commit Hash: $(git rev-parse --short HEAD)"
echo "- Commit Message: auto: nightly pipeline updates $CHECK_TIME"
echo ""
echo "### 4. Verification Steps Performed"
echo "1. git status --porcelain"
echo "2. git diff HEAD --stat" 
echo "3. git diff --name-only"
echo "4. git status -uall"
echo "5. git ls-files --others"
```

## Integration with Scheduled Cron

Example cron entry:
```
# Check wiki directory every 4 hours
0 */4 * * * cd /root/wiki && /path/to/hermes/agent run --skill cron-git-state-monitoring
```

## Related Patterns

- **Continuous Documentation**: Auto-commit for documentation repos
- **Configuration Drift Detection**: Monitor config files for unauthorized changes  
- **Backup Verification**: Ensure backup scripts are committing their outputs