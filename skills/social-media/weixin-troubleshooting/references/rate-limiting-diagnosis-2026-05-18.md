# iLink Rate Limiting Diagnosis — 2026-05-18

## Problem
Multiple cron jobs sending to Weixin triggered iLink API rate limiting, causing delivery failures.

## Error Pattern
```
ERROR gateway.platforms.weixin: [Weixin] send failed to=o9cq802K: iLink sendmessage rate limited: ret=-2 errcode=None errmsg=rate limited
```

## Root Cause
Two cron jobs scheduled at the same time (Monday 01:00) exceeded iLink's rate limit:
- `1a37493b5d29` — Brain OS 每周知识库审计 (01:00 Mondays)
- `b62a532b3c2b` — Brain OS 周一知识库 Lint (01:00 Mondays)

Additionally, daily tasks at 00:01 and 20:00 contributed to cumulative load.

## Multi-Gateway Confusion
`hermes gateway status --profile dingtalk-worker` showed:
```
⚠ weixin: Weixin bot token already in use (PID 2229653). Stop the other gateway first.
```

**This was a red herring.** The PID 2229653 no longer existed:
```bash
ps aux | grep 2229653  # → "PID 2229653 not found"
```

The `dingtalk-worker` profile has all `WEIXIN_*` vars commented out, so it doesn't load Weixin.

## Resolution: Staggered Cron Schedule

| Job ID | Task | Original | Adjusted |
|--------|------|----------|----------|
| 3cda2159065c | 每日观察者自检 | 00:01 daily | **00:30 daily** |
| 409b522e8c22 | 晚间待办提醒 | 20:00 daily | **20:30 daily** |
| 1a37493b5d29 | 每周知识库审计 | 01:00 Mon | **01:30 Mon** |
| b62a532b3c2b | 周一知识库 Lint | 01:00 Mon | **02:00 Mon** |
| 4616b8bdeafa | 每周计划 | 05:10 Mon | **06:00 Mon** |
| df75453a8904 | 月度总结 | 08:00 1st | **09:00 1st** |

## Commands Used
```bash
# List cron jobs
hermes cron list

# Edit schedule
hermes cron edit <job_id> --schedule "MIN HOUR DOM MON DOW"

# Verify gateway state
cat ~/.hermes/gateway_state.json

# Check for stale PID warnings
ps aux | grep <PID_from_warning>
```

## Key Insight
Rate limiting is caused by **cron job timing**, NOT by multiple gateway instances. Always verify stale PID warnings before assuming gateway conflicts.
