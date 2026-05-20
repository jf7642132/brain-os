# iLink Rate Limiting Diagnosis — 2026-05-18 Session

## Problem
Multiple scheduled cron jobs sending to Weixin hit iLink API rate limits.

## Affected Jobs (2026-05-18)
| Job | Schedule | Last Run | Status |
|-----|----------|----------|--------|
| 晚间待办提醒 | 20:00 daily | 5/17 20:06 | ⚠️ rate limited |
| 每周知识库审计 | 01:00 Monday | 5/18 01:04 | ⚠️ rate limited |
| 每日观察者自检 | 00:01 daily | 5/18 00:05 | ⚠️ rate limited |
| 每周计划 | 05:10 Monday | 5/18 05:12 | ⚠️ rate limited |
| 周一知识库Lint | 01:00 Monday | 5/18 01:02 | ⚠️ rate limited |

## Root Cause Analysis
- **NOT** caused by dual gateway instances
- `gateway status` showed stale warning: `PID 2229653` — verified via `ps aux` that this PID no longer exists
- `dingtalk-worker` profile has all `WEIXIN_*` vars commented out — does NOT load weixin channel
- **Real cause**: Multiple cron jobs trigger at same time (especially Monday 01:00), exceeding iLink send rate limit

## Diagnostic Commands Used
```bash
hermes cron list                    # List all scheduled jobs
hermes gateway status               # Check gateway health (may show stale warnings)
ps aux | grep <PID>                 # Verify if PID actually exists
grep "rate limited" ~/.hermes/logs/gateway.log | tail -20  # Check rate limit errors
cat ~/.hermes/profiles/dingtalk-worker/.env | grep WEIXIN  # Check if weixin is disabled
```

## Resolution
Stagger cron job times to avoid simultaneous weixin deliveries:
- Move Monday 01:00 tasks to 01:30 and 02:00
- Move daily 00:01 task to 00:30

## Key Lesson
When `gateway status` shows "PID already in use" warnings, always verify with `ps aux` before assuming a conflict. Stale PID references can persist in status output after processes have exited.
