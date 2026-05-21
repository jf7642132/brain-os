# Path Migration Incident: wiki → knowledge (2026-05-15)

## Summary

On 2026-05-15, the knowledge base directory structure was migrated from `<OLD_KNOWLEDGE_DIR>/` to `<KNOWLEDGE_DIR>/`. This incident document records the migration details and lessons learned.

## Migration Details

| Item | Before | After |
|------|--------|-------|
| Root directory | `<OLD_KNOWLEDGE_DIR>/` | `<KNOWLEDGE_DIR>/` |
| Files migrated | 823 | 823 |
| Git initialized | No | Yes |
| Cron tasks | Old paths | Updated |

## Root Cause

The original `<OLD_KNOWLEDGE_DIR>/` directory was not the intended location. The correct location should have been `<KNOWLEDGE_DIR>/` from the start.

## Impact

1. **Cron tasks**: All cron task templates needed path updates
2. **Skills**: Some skills may still reference old paths
3. **Silent failures**: Scripts running with wrong paths fail silently

## Verification Steps

After any directory structure change:

```bash
# 1. Verify actual directory structure
ls -la <KNOWLEDGE_DIR>/

# 2. Find old path references
grep -r "<OLD_KNOWLEDGE_DIR>" <HERMES_ROOT>/skills/ 2>/dev/null
grep -r "wiki" <KNOWLEDGE_DIR>/.learnings/ 2>/dev/null

# 3. Test cron task execution
# Run a test cron task and verify it completes successfully

# 4. Check git status
cd <KNOWLEDGE_DIR> && git status
```

## Current Path Reference

| Component | Path |
|-----------|------|
| Knowledge base | `<KNOWLEDGE_DIR>/` |
| Session files | `<HERMES_SESSIONS_DIR>/` |
| Session database | `<HERMES_STATE_DB>` |
| Nightly digests | `04-知识库/01-阅读消化/04-摘要汇总/` |
| Integration reports | `04-知识库/99-系统/03-集成报告/` |
| Project briefs | `04-知识库/01-阅读消化/02-主题知识/` |

## Related Files

- `04-知识库/01-阅读消化/04-摘要汇总/nightly-digest-2026-05-15.md` — Migration day digest
- `04-知识库/99-系统/03-整合报告/2026-05-15-文章整合报告.md` — Article integration report

## Lessons Learned

1. **Always verify paths before running scripts** — Don't assume path configuration is correct
2. **Test cron tasks after structural changes** — Silent failures are common
3. **Document path changes in skills** — Skills should reference actual paths, not assumed paths
4. **Use relative paths when possible** — Reduces path drift risk

---

*Document created: 2026-05-16*