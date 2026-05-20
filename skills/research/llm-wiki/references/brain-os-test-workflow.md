# Brain OS 测试工作流

> 参考日期: 2026-05-19
> 来源: Brain OS 项目测试验证

---

## 正确的测试流程

**CRITICAL**: 测试顺序必须遵循数据流方向：

```
生产者 → todo → Kanban 管理层 → Kanban → todo → 消费者 → 报告
```

### 第一步：生产者 → todo

**目标**: 验证生产者任务能正确写入 todo-backlog.md

**操作**:
1. 手动创建测试待办（或触发生产者任务）
2. 验证 todo-backlog.md 内容格式正确
3. 检查待办字段完整性（ID、来源、描述、状态、时间戳）

**验证命令**:
```bash
# 检查待办数量
grep -c '^[a-f0-9-]\{36\}' todo-backlog.md

# 检查字段完整性
head -20 todo-backlog.md
```

**预期结果**:
- 待办格式正确（UUID 格式 ID）
- 所有字段完整
- 状态为 `open` 或 `in_progress`

### 第二步：todo → Kanban 管理层

**目标**: 验证 kanban-sync.py 能正确读取 todo 并创建 Kanban 卡片

**操作**:
1. 执行 `kanban-sync.py --read-todo`
2. 验证 Kanban 卡片创建成功
3. 验证 todo 中的 Kanban 卡片 ID 字段已更新

**验证命令**:
```bash
# 读取 todo 并创建卡片
python3 ~/.hermes/scripts/kanban-sync.py --task kanban-manager --read-todo

# 验证 todo 更新
grep 't_[a-f0-9]\{8\}' todo-backlog.md

# 验证 Kanban 卡片
hermes kanban list
```

**预期结果**:
- 输出显示"待创建 Kanban 的 todo: N 个"
- Kanban 卡片创建成功，返回卡片 ID
- todo-backlog.md 中对应待办的 Kanban 卡片字段已更新

### 第三步：todo → 消费者 → 报告

**目标**: 验证消费者任务能正确读取 todo 并生成报告

**操作**:
1. 触发消费者任务（如每日早报）
2. 检查输出报告是否包含待办信息
3. 验证报告格式和内容完整性

**验证命令**:
```bash
# 触发消费者任务
hermes cron run <job-id>

# 检查输出文件
ls -la 09-personal-ops/01-每日简报/

# 验证报告内容
grep -i 'todo\|待办' 09-personal-ops/01-每日简报/*.md
```

**预期结果**:
- 报告包含待办概览表格
- 报告包含优先级建议
- 报告引用了 todo-backlog.md 中的数据

---

## 常见错误

| 错误 | 原因 | 修复 |
|------|------|------|
| 测试顺序颠倒 | 先触发消费者再验证 todo | 严格按照数据流方向测试 |
| --read-todo 无输出 | 任务配置未更新 | 在 TASK_CONFIG 中添加任务 |
| 卡片创建失败 | priority 类型错误 | 使用 PRIORITY_MAP.get() 转换 |
| todo 未更新卡片 ID | 缺少 update_todo_kanban_id() | 添加该函数 |
| 读取 0 个待办 | 章节格式不兼容 | 添加对"## 活跃待办"的兼容 |

---

## 手动触发测试示例

```bash
# 1. 创建测试待办
echo "| $(uuidgen) | manual-test | 测试待办 | open | | $(date '+%Y-%m-%d %H:%M') | $(date '+%Y-%m-%d %H:%M') | | |" >> todo-backlog.md

# 2. 触发 Kanban 管理层
python3 ~/.hermes/scripts/kanban-sync.py --task kanban-manager --read-todo

# 3. 验证 todo 更新
grep 't_[a-f0-9]\{8\}' todo-backlog.md

# 4. 触发消费者任务
hermes cron run <consumer-job-id>

# 5. 检查报告
cat 09-personal-ops/01-每日简报/$(date '+%Y-%m-%d').md
```

---

## 自动化测试脚本

```bash
#!/bin/bash
# test-brain-os.sh - Brain OS 数据流闭环测试

set -e

WIKI_PATH="${WIKI_PATH:-/root/.hermes/knowledge}"
TODO_PATH="$WIKI_PATH/06-context/todo-tracking/todo-backlog.md"
SCRIPTS_PATH="$HOME/.hermes/scripts"

echo "=== Brain OS 数据流闭环测试 ==="

# 第一步：生产者 → todo
echo "\n[1/3] 生产者 → todo"
TEST_ID=$(uuidgen)
echo "| $TEST_ID | auto-test | 自动化测试待办 | open | | $(date '+%Y-%m-%d %H:%M') | $(date '+%Y-%m-%d %H:%M') | | |" >> "$TODO_PATH"
echo "✅ 测试待办已创建: $TEST_ID"

# 第二步：todo → Kanban
echo "\n[2/3] todo → Kanban"
KANBAN_ID=$(python3 "$SCRIPTS_PATH/kanban-sync.py" --task kanban-manager --read-todo 2>/dev/null | grep -o 't_[a-f0-9]\{8\}' | tail -1)
if [ -z "$KANBAN_ID" ]; then
    echo "❌ Kanban 卡片创建失败"
    exit 1
fi
echo "✅ Kanban 卡片已创建: $KANBAN_ID"

# 验证 todo 更新
if grep -q "$KANBAN_ID" "$TODO_PATH"; then
    echo "✅ todo 已更新 Kanban 卡片 ID"
else
    echo "❌ todo 未更新 Kanban 卡片 ID"
    exit 1
fi

# 第三步：todo → 消费者 → 报告
echo "\n[3/3] todo → 消费者 → 报告"
# 跳过自动触发，等待定时任务

echo "\n=== 测试完成 ==="
echo "测试待办 ID: $TEST_ID"
echo "Kanban 卡片 ID: $KANBAN_ID"
echo "请等待定时任务验证完整闭环"
```
