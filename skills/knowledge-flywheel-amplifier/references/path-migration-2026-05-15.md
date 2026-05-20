# Path Migration Incident — 2026-05-15

## Background

On 2026-05-15, the knowledge directory structure was migrated from `/root/wiki/` to `/root/.hermes/knowledge/`. This was a 823-file migration that affected:

- All skill path references
- All cron task paths
- All nightly pipeline stage outputs

## Impact on Knowledge Flywheel Amplifier

### Before Migration
```
/root/wiki/03-知识库/01-阅读消化/04-摘要汇总/nightly-digest-YYYY-MM-DD.md
/root/wiki/03-知识库/99-系统/03-集成报告/YYYY-MM-DD/knowledge-amplifier-report-YYYY-MM-DD.md
```

### After Migration
```
/root/.hermes/knowledge/04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-YYYY-MM-DD.md
/root/.hermes/knowledge/04-知识库/99-系统/03-集成报告/YYYY-MM-DD/knowledge-amplifier-report-YYYY-MM-DD.md
```

Note: The directory number changed from `03-知识库` to `04-知识库` as part of the reorganization.

## Verification Steps

After any path migration, verify:

1. **Skill references updated**:
   ```bash
   grep -r "03-知识库" /root/.hermes/skills/ 2>/dev/null
   # Should return nothing (or only in historical references)
   ```

2. **Cron tasks updated**:
   ```bash
   grep -r "wiki" /root/.hermes/cron/ 2>/dev/null
   # Should return nothing (or only in historical references)
   ```

3. **Git history confirms migration**:
   ```bash
   cd /root/.hermes/knowledge && git log --oneline --since="2026-05-14"
   ```

## Lessons Learned

1. **Path migrations cascade** — A single directory rename affects skills, cron tasks, and all downstream processes
2. **Silent failures are dangerous** — Cron tasks with wrong paths may fail silently without obvious error
3. **Skills need proactive updates** — Skills are not automatically updated when paths change; they must be patched manually
4. **Verification is essential** — After migration, run verification commands to catch orphaned references

## Related Skills Requiring Update

After the 2026-05-15 migration, the following skills needed path updates:

| Skill | Old Path | New Path | Status |
|-------|----------|----------|--------|
| knowledge-flywheel-amplifier | `03-知识库/...` | `04-知识库/...` | ✅ Updated |
| article-notes-integration | `03-知识库/...` | `04-知识库/...` | ⏳ Pending |
| conversation-knowledge-mining | `03-知识库/...` | `04-知识库/...` | ⏳ Pending |

## Cross-Reference

- Migration executed during: 2026-05-15 22:44 (see `nightly-digest-2026-05-15.md` Stage B)
- Related pattern: `结构重构→路径适配` in knowledge-flywheel-amplifier pattern library