# Kanban Sync Pattern for Article Integration

## Purpose

When the article integration pipeline discovers issues requiring human follow-up, use `kanban-sync.py` to create structured todo items and Kanban cards.

## Usage

### Step 1: Write findings to temp file

```bash
cat > /tmp/article-integration-findings-YYYYMMDD.md << 'EOF'
# Article Integration Findings YYYY-MM-DD

## P1: Issue Title

**问题**: Description of the issue.

**影响**: Impact analysis.

**建议**: Recommended actions.

**待办**:
- [ ] Action item 1
- [ ] Action item 2

---

*生成时间: YYYY-MM-DD HH:00*
EOF
```

### Step 2: Run kanban-sync.py

```bash
python ~/.hermes/scripts/kanban-sync.py --write-todo --task article-integration --output /tmp/article-integration-findings-YYYYMMDD.md
```

### Step 3: Verify output

The script will:
1. Parse findings from the temp file
2. Generate todo IDs
3. Write to `todo-backlog.md`
4. For P0 issues, create Kanban cards

## Important Rules

- **Never edit todo-backlog.md directly** — always use kanban-sync.py as the single writer
- **P0 issues get Kanban cards** — high-priority issues should be visible in the Kanban board
- **P1/P2 issues go to todo-backlog** — lower priority items tracked in backlog

## Common Findings Patterns

### Article backlog accumulation
```markdown
## P1: 外贸风险预警日报积压

**问题**: X篇外贸风险预警日报积压在文章笔记目录中超过Y天，未进入整合流程。

**影响**: 
- 知识库中缺少这些日报的结构化整合
- 无法在 topic-map 中建立关联

**建议**:
1. 确认这些日报是否仍有价值（若已过时，建议归档）
2. 若需保留，建议补充整合并添加 `chemical-trade` 标签
3. 检查上游数据采集管道是否正常

**待办**:
- [ ] 确认X篇外贸风险预警日报是否仍需整合
- [ ] 若需保留，补充整合并添加标签
- [ ] 若已过时，归档处理
```

### Task timeout
```markdown
## P1: 25国供需平衡分析任务超时

**问题**: 任务报告状态仍为 "In Progress"，但预计完成时间已超时Z天。

**影响**:
- 任务规划已建立，但实际执行结果未知
- 无法生成市场机会评分

**建议**:
1. 检查 ProductAgent 执行进度
2. 若未完成，重新分配任务
3. 若已完成，补充执行结果报告

**待办**:
- [ ] 检查 ProductAgent 执行进度
- [ ] 若未完成，重新分配任务
- [ ] 若已完成，补充执行结果报告
```

## Troubleshooting

### Script not found
Ensure `~/.hermes/scripts/kanban-sync.py` exists:
```bash
ls -la ~/.hermes/scripts/kanban-sync.py
```

### No todos created
Check the findings file format — the script expects specific markdown structure with `## P1:` or `## P0:` headers.

### Duplicate todos
The script should not create duplicates. If duplicates appear, check if the findings file was run multiple times.
