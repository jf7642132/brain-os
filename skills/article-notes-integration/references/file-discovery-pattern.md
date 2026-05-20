# File Discovery Pattern for 24-Hour Window

When scanning for articles updated in the last 24 hours:

## Epoch-Based Comparison (Recommended)

```bash
window_start=$(date -d "24 hours ago" +%s)
find /path/to/article-notes -name "*.md" -type f -exec stat --format='%Y %n' {} \; | \
  while read mtime path; do
    if [ "$mtime" -ge "$window_start" ]; then echo "$path"; fi
  done
```

## Alternative: Using find -printf

```bash
current_epoch=$(date +%s)
window_start=$((current_epoch - 86400))
find /path/to/article-notes -name "*.md" -type f -printf '%T@ %p\n' | \
  awk -v start="$window_start" '$1 > start {print $2}'
```

## Cross-Reference with Pipeline Times

1. Check if file timestamps align with known cron run times
2. If all files are older than 24 hours, verify the pipeline is running correctly
3. Note: File modification times may be set to historical dates during batch operations

## Check Multiple Directories

Adapt based on knowledge base structure:

### English-style
- `00-raw/articles/`
- `02-concepts/<domain>/01-article-notes/`
- `04-queries/daily/02-article-integration/`

### Chinese-style
- `03-知识库/02-工作整理/01-文章笔记/`
- `03-知识库/01-阅读消化/01-领域知识/`
- `03-知识库/01-阅读消化/02-主题知识/`
- `03-知识库/01-阅读消化/03-模式提炼/`

### Discovery Commands
```bash
# Find all article-related directories
find /root/.hermes/knowledge -type d \( -name "*article*" -o -name "*文章*" \) 2>/dev/null

# Find all integration-related directories
find /root/.hermes/knowledge -type d \( -name "*integration*" -o -name "*整合*" \) 2>/dev/null

# Find all digest-related directories
find /root/.hermes/knowledge -type d \( -name "*digest*" -o -name "*摘要*" \) 2>/dev/null
```

## When No New Articles Found

1. Report the last known update time from existing files
2. Note if this is unusual for the pipeline
3. Check if user activity patterns explain the gap
4. Consider using `[SILENT]` if truly nothing to report
5. **Important**: If empty for >7 days, flag as potential pipeline issue

## Timestamp Verification

```bash
# Get file modification time
stat -c "%Y %n" file.md

# Get current epoch
date +%s

# Calculate hours since modification
echo "scale=2; ($(date +%s) - $file_epoch) / 3600" | bc
```

## Knowledge Base Structure Variations

⚠️ Different knowledge base implementations may use different directory structures. Always scan first to identify which structure is in use before assuming paths.

| Purpose | English-style | Chinese-style |
|---------|--------------|---------------|
| Article notes source | `00-raw/articles/` | `03-知识库/02-工作整理/01-文章笔记/` |
| Domain-specific notes | `02-concepts/<domain>/01-article-notes/` | `03-知识库/02-工作整理/<domain>/` |
| Integration reports | `99-system/03-integration-reports/` | `03-知识库/99-系统/03-整合报告/` |
| Nightly digest | `04-queries/daily/04-summary/` | `03-知识库/01-阅读消化/04-摘要/` |
| Topic index | `99-system/01-indexes/` | `03-知识库/99-系统/01-索引/` |