---
name: daily-briefing
category: productivity
description: Generate a daily briefing from the knowledge base todo-backlog, summarize yesterday's work, suggest priorities, and commit the report.
---

# Daily Briefing Skill

Generate a daily briefing from the knowledge base todo-backlog, summarize yesterday's work, suggest priorities, and commit the report.

## When to Use
- Each morning (or scheduled) to produce a daily status report for personal ops.
- When you need to update the `03-个人运营/01-每日简报/` directory with a new markdown file.

## Steps
1. **Determine Today's Date**
   - Run `date +%Y-%m-%d` to get `YYYY-MM-DD`.

2. **Read the Todo Backlog**
   - Read `<KNOWLEDGE_DIR>/03-个人运营/03-待办跟进/todo-backlog.md`.
   - Extract any tasks due today (if any) or note that the backlog is empty.

3. **Summarize Yesterday's Work**
   - Use `git log --since="yesterday 00:00:00" --until="yesterday 23:59:59" --oneline` in the knowledge repo to list commits.
   - Optionally filter for auto‑generated scans vs manual work.

4. **Write the Briefing File**
   - Create `<KNOWLEDGE_DIR>/03-个人运营/01-每日简报/YYYY-MM-DD.md` with sections:
     - # 驾驶舱简报 - YYYY-MM-DD
     - ## 今日待办跟进（来自 todo-backlog.md）
     - ## 昨日完成工作（YYYY-MM-DD）
     - ## 今日优先级建议
     - ## 行动项
   - Fill in the content gathered above.

5. **Commit to Git**
   - `cd <KNOWLEDGE_DIR>`
   - `git add 03-个人运营/01-每日简报/YYYY-MM-DD.md`
   - `git commit -m "auto: 驾驶舱简报 YYYY-MM-DD"`
   - (Optional) `git push` if remote is configured.

## Pitfalls
- Forgetting to read the todo-backlog before writing may overwrite a sibling subagent's changes. Always read the file first if concurrent edits are possible.
- The git commit message should match the exact format used by other automated jobs for consistency.
- If the todo-backlog uses a different path, adjust accordingly.

## References
- See `references/daily-briefing-example.md` for a concrete example of a generated briefing.