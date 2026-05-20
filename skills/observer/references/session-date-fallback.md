# Session Date Fallback Implementation

When running as a cron job, use this Python implementation for session date fallback:

```python
from datetime import datetime, timedelta

today_date = datetime.now().strftime("%Y%m%d")
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")

today_sessions = [f for f in os.listdir(sessions_dir) if f.startswith(today_date) and f.endswith('.jsonl')]

if not today_sessions:
    # Fallback to yesterday's sessions
    today_sessions = [f for f in os.listdir(sessions_dir) if f.startswith(yesterday_date) and f.endswith('.jsonl')]
    report_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
else:
    report_date = datetime.now().strftime("%Y-%m-%d")
```

This prevents false negatives when cron runs before sessions are created for the day.