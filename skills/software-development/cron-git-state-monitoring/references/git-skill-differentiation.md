# Git-Related Skill Differentiation

This reference clarifies when to use each git-related skill to avoid confusion and ensure proper workflow matching.

## Skill Comparison Matrix

| Skill | Primary Focus | Typical Use Case | Key Operations | Cron Job Friendly |
|-------|--------------|------------------|----------------|-------------------|
| **cron-git-state-monitoring** | Local git state checking and auto-commit for scheduled jobs | Periodic monitoring of wiki/docs repos, documentation updates | `git status`, `git diff`, `git add`, `git commit`, file timestamp analysis | ✅ Yes - designed for cron jobs, supports SILENT mode |
| **github-repo-management** | GitHub API operations and remote repository management | Creating repos, managing releases, configuring webhooks, branch protection | `gh CLI`, GitHub REST API, repository settings, releases, secrets | ❌ No - interactive operations requiring decisions |
| **github-pr-workflow** | Pull request lifecycle management | Code reviews, CI/CD integration, merge strategies | `gh pr create`, `gh pr review`, `gh pr merge`, PR status checks | ⚠️ Sometimes - but usually requires review decisions |
| **github-issues** | Issue tracking and project management | Creating, triaging, labeling, assigning issues | `gh issue create`, `gh issue list`, issue filters, comments | ✅ Yes - for automatic issue creation from other systems |

## When to Use Which Skill

### Use `cron-git-state-monitoring` when:
- You're running as a scheduled cron job (no user interaction)
- You need to check git repository state autonomously
- You want to auto-commit any uncommitted changes
- You need to return `[SILENT]` when no changes found
- You're monitoring wiki directories, documentation repos, or content repositories
- The primary concern is whether changes exist locally that need committing

### Use `github-repo-management` when:
- You need to interact with GitHub API (create repos, manage settings)
- You need to handle releases, tags, or webhooks
- You're configuring repository-level settings
- You need to manage GitHub Actions secrets
- You're working with repository templates or forks

### Use `github-pr-workflow` when:
- You're managing pull requests (creating, reviewing, merging)
- You need to check CI/CD status on PRs
- You're implementing code review workflows
- You need to coordinate with team members on code changes

### Use `github-issues` when:
- You need to create or manage GitHub issues
- You're implementing automated issue tracking
- You need to link issues to PRs or commits
- You're building project management workflows

## Common Workflow Patterns

### Pattern 1: Documentation Auto-Update
```
cron-git-state-monitoring → 
If changes found: commit locally → 
github-pr-workflow → create PR for review
```

### Pattern 2: System Monitoring Integration
```
observer skill → detects issues → 
github-issues → creates ticket → 
cron-git-state-monitoring → ensures report files are committed
```

### Pattern 3: Release Pipeline
```
github-repo-management → creates release → 
cron-git-state-monitoring → commits changelog updates → 
github-pr-workflow → merges release branch
```

## Installation and Authentication Notes

### Authentication Requirements
- **cron-git-state-monitoring**: Only needs local git access (no GitHub token required)
- **github-** skills: Require GitHub authentication via `gh auth login` or `GITHUB_TOKEN`

### Cron Job Configuration
- **cron-git-state-monitoring**: Designed to run fully autonomously, returns `[SILENT]` when appropriate
- **github-** skills: May require interactive authentication or token setup before cron use

## Error Handling Differences

### cron-git-state-monitoring Errors
- Local git not installed
- Repository directory not found
- Permission issues with .git directory
- Git operations failing (merge conflicts, etc.)

### github-repo-management Errors
- GitHub API authentication failures
- Rate limiting (429 errors)
- Repository not found (404)
- Permission issues (403)

## Performance Considerations

### cron-git-state-monitoring
- Minimal network usage (local only)
- Fast execution when no changes
- Can be run frequently (every 15-30 minutes)

### github-repo-management
- Network-dependent (GitHub API calls)
- Subject to API rate limits
- Best for less frequent operations

## Best Practices

1. **Use the right tool for the job**: Don't use GitHub API for simple local git operations
2. **Layer responsibilities**: Local commits first, then remote operations if needed
3. **Handle errors appropriately**: Local git errors vs GitHub API errors require different handling
4. **Consider authentication**: Cron jobs need pre-configured authentication for GitHub skills
5. **Monitor execution**: Track both local git operations and GitHub API usage for cost/rate limit management

## Migration Tips

### From manual git checks to cron-git-state-monitoring
1. Identify repositories needing periodic monitoring
2. Test the skill manually first
3. Set up cron job with appropriate frequency
4. Monitor initial runs for false positives/negatives
5. Adjust verification thresholds as needed

### From script-based to skill-based git operations
1. Replace custom bash scripts with skill calls
2. Standardize on the verification sequence
3. Implement SILENT mode where appropriate
4. Add error handling and reporting
5. Integrate with existing monitoring systems