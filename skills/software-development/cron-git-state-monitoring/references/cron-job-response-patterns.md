# Cron Job Response Patterns for Hermes Agent

This reference documents the critical response patterns when Hermes Agent runs as a scheduled cron job, based on observed successful implementation patterns.

## Core Principle: Autonomous Execution

When running as a cron job:
- **No user present** - cannot ask questions, request clarification, or wait for follow-up
- **Must execute fully autonomously** - make reasonable decisions where needed
- **Final response is automatically delivered** - system handles delivery to configured destination

## Response Delivery Mechanism

### How It Works
1. Cron job triggers Hermes Agent with a specific task
2. Agent executes the task autonomously
3. Agent's **final response** is automatically delivered to the job's configured destination
4. No manual delivery mechanism needed (do NOT use `send_message`)

### What to Output
```python
# CORRECT: Output final content directly
print("## Task Report")
print("Completed successfully at", timestamp)
print("Details: ...")

# WRONG: Trying to use delivery mechanisms
# message(action=send, target=channel, message=report)
```

## SILENT Mode Implementation

### When to Use SILENT Mode
Use `[SILENT]` when:
1. Task completed successfully **and**
2. There's genuinely **nothing new to report** (no actionable findings)
3. All verification checks passed with expected results

### How to Output SILENT Mode
```python
# CORRECT: Return exactly [SILENT] (nothing else)
return "[SILENT]"

# WRONG: Combining SILENT with content
return "[SILENT] No changes found."

# WRONG: Different format
return "SILENT"
return "[SILENT_MODE]"
return "silent"
```

### SILENT Mode Examples

**For git monitoring:**
```bash
# After comprehensive checks
if [ -z "$git_changes" ] && [ -z "$git_diff" ]; then
  echo "[SILENT]"
  exit 0
fi
```

**For health checks:**
```bash
# If all systems normal
if [ "$errors" -eq 0 ] && [ "$warnings" -eq 0 ]; then
  echo "[SILENT]"
  exit 0
fi
```

## Report Structure Guidelines

### Always Include
1. **Clear title/header** identifying the report type
2. **Check timestamp** when verification occurred
3. **Status summary** (success/failure, changes found/not found)
4. **Action taken** (what was done, if anything)
5. **Verification steps** (brief summary of checks performed)

### Example Report Template
```
## Git State Monitoring Report

**Check Time**: 2026-05-14 16:02

### 1. Status Summary
- Branch: master
- Last Commit: 2026-05-14 14:00
- Changes Found: No
- Action Taken: None required

### 2. Verification Steps
1. git status --porcelain ✓ (clean)
2. git diff HEAD --stat ✓ (no diffs)
3. git diff --name-only ✓ (no changed files)
4. git status -uall ✓ (nothing to commit)
5. File timestamp analysis ✓ (no recent modifications)
```

## Error Handling in Cron Jobs

### Must Handle Errors Gracefully
- Never crash silently
- Always provide error context in report
- Include troubleshooting suggestions when possible

### Error Report Template
```
## Task Execution Failed

**Time**: 2026-05-14 16:02
**Task**: Git state monitoring for /root/wiki

### Error Details
- Error: Permission denied to .git directory
- Command: git status
- Exit Code: 128

### Suggested Resolution
1. Check directory permissions: ls -la /root/wiki/.git/
2. Verify agent has read/write access
3. Consider using sudo or adjusting permissions

### Verification Attempted
- Directory exists: ✓
- Git initialized: ✓
- Navigated successfully: ✓
```

## Decision Making in Autonomous Mode

### When to Proceed vs When to Stop
**Proceed if:**
- Task can be completed with reasonable assumptions
- Missing information has sensible defaults
- Error is recoverable with fallback approach

**Stop and report error if:**
- Critical information missing (e.g., target directory doesn't exist)
- Authentication/authorization failure
- Unrecoverable system error (disk full, network down)

### Making Reasonable Assumptions
```python
# Example: Directory fallback
target_dir = "/root/wiki"
if not os.path.exists(target_dir):
    # Try alternative location
    target_dir = "/home/user/wiki" if os.path.exists("/home/user/wiki") else None
    
if not target_dir:
    return "## Error: Target directory not found"
```

## Testing Cron Job Skills

### Manual Testing Before Deployment
1. Run skill manually to verify output format
2. Test SILENT mode conditions
3. Verify error handling works
4. Check report structure meets requirements

### Integration Testing
```bash
# Simulate cron job execution
cd /root/wiki && hermes run --skill cron-git-state-monitoring

# Capture and review output
OUTPUT=$(cd /root/wiki && hermes run --skill cron-git-state-monitoring 2>&1)
echo "Output: $OUTPUT"
```

## Common Pitfalls and Solutions

### Pitfall 1: Interactive Prompts
**Problem**: Skill waits for user input in cron job
**Solution**: Use default values, skip optional steps, or fail gracefully

### Pitfall 2: Missing Dependencies
**Problem**: Command not found when cron runs (different PATH)
**Solution**: Use absolute paths or set PATH in cron job

### Pitfall 3: Permission Issues
**Problem**: Cron job runs as different user with different permissions
**Solution**: Test with same user context, adjust permissions, or use sudo appropriately

### Pitfall 4: Output Truncation
**Problem**: Long output gets truncated
**Solution**: Keep reports concise, use summaries, link to detailed logs

### Pitfall 5: Timeout Issues
**Problem**: Cron job times out on long operations
**Solution**: Set appropriate timeout, break operations into smaller chunks, monitor execution time

## Performance Considerations

### Keep Execution Fast
- Cron jobs should complete quickly (< 5 minutes ideally)
- Use efficient verification methods
- Cache results when appropriate
- Skip unnecessary operations

### Resource Usage
- Monitor memory and CPU usage
- Avoid spawning many subprocesses
- Clean up temporary files
- Log resource usage for optimization

## Integration with Monitoring

### Success Metrics Tracking
- Record execution time
- Track success/failure rates
- Monitor SILENT vs report frequency
- Alert on abnormal patterns

### Alerting Thresholds
- Consecutive failures > 3 → alert
- Execution time > 10 minutes → warning
- SILENT for > 24h when expected daily changes → investigate

## Compliance and Documentation

### Always Document
- What the cron job does
- When it runs (schedule)
- What outputs to expect
- How to troubleshoot

### Configuration Management
- Store cron job definitions in version control
- Document dependencies and requirements
- Maintain change log for cron job modifications