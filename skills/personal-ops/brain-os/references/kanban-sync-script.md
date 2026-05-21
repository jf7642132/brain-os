# kanban-sync.py 脚本参考

## 文件位置

```
<HERMES_SCRIPTS_DIR>/kanban-sync.py
```

## 核心函数

### read_todo_backlog()

读取 todo-backlog.md，返回按优先级分类的项目。

```python
def read_todo_backlog() -> dict:
    """返回 {"H": [...], "M": [...], "L": [...], "done": [...]}"""
```

### write_todo_backlog(items, priority, source, kanban_id)

写入/更新 todo-backlog.md。

```python
def write_todo_backlog(
    items: list,           # 问题文本列表
    priority: str,         # P0/P1/P2/P3 或 high/medium/low
    source: str,           # 来源任务名
    kanban_id: str = ""    # 关联的 Kanban 卡片 ID
) -> bool:
```

### update_todo_from_kanban(kanban_id, status, completed_date, method)

根据 Kanban 卡片状态更新 todo。

```python
def update_todo_from_kanban(
    kanban_id: str,        # Kanban 卡片 ID
    status: str,           # open/in_progress/resolved/wontfix
    completed_date: str = "",  # 完成日期
    method: str = ""       # 处理方式
) -> bool:
```

### generate_todo_id(priority_label, todo_items)

生成唯一 todo ID。

```python
def generate_todo_id(priority_label: str, todo_items: dict) -> str:
    # 返回格式: "H001", "M002", "L003"
```

### parse_output(output_file, task_key)

解析任务输出，提取发现/问题/待办项。

```python
def parse_output(output_file: str, task_key: str) -> list:
    # 返回: [{"text": "...", "severity": "P2", "status": "open", "date": "2026-05-18"}]
```

## 任务配置

脚本中的 TASK_CONFIG 字典定义各任务的解析规则：

```python
TASK_CONFIG = {
    "observer-self-check": {
        "name": "每日观察者自检",
        "tracker": "observer-self-check-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "dialogue-mining": {
        "name": "夜间对话挖掘",
        "tracker": "dialogue-mining-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    # ... 其他任务
}
```

## 优先级映射

| 输入 | 输出 | 说明 |
|------|------|------|
| P0 / high / H | 1 | 高优先级 |
| P1 / medium / M | 2 | 中优先级 |
| P2 / low / L | 3 | 低优先级 |
| P3 | 4 | 可选 |

## 状态映射

| 符号 | 状态 | 说明 |
|------|------|------|
| ⚠️ / 🔴 | open | 新问题 |
| 🟡 / 进行中 | in_progress | 处理中 |
| ✅ / 已完成 / resolved | resolved | 已处理 |
| ❌ / wontfix | wontfix | 不处理 |

## 防重复机制

创建 Kanban 卡片前检查：

1. **ID 重复**：检查 `item_id` 是否已存在于 tracker
2. **内容重复**：检查问题摘要前 30 字符是否已存在于 todo
3. **状态重复**：如果已存在且状态都是 open，跳过

## 输出示例

### --write-todo 模式

```
=== 通用 Kanban 闭环（todo 双向同步）===
任务: observer-self-check
模式: LIVE
子模式: WRITE_TODO（输出 → todo）

📋 步骤 1: 解析任务输出...
   发现项目: 3 个

📝 步骤 2: 写入 todo-backlog.md...
✅ 已写入 todo: H001
✅ 已写入 todo: M001
✅ 已写入 todo: L001

✅ 写入 todo 完成
```

### --read-todo 模式

```
=== 通用 Kanban 闭环（todo 双向同步）===
任务: kanban-manager
模式: LIVE
子模式: READ_TODO（todo → Kanban）

📝 步骤 1: 读取 todo-backlog.md...
   待创建 Kanban 的 todo: 5 个

📌 步骤 2: 创建 Kanban 卡片...
   ✅ H001: 创建卡片 12345
   ✅ M001: 创建卡片 12346
   ...

✅ 完成
```

### --update-todo 模式

```
=== 通用 Kanban 闭环（todo 双向同步）===
任务: kanban-manager
模式: LIVE
子模式: UPDATE_TODO（Kanban → todo）

📝 步骤 1: 更新 todo-backlog.md...
✅ 已更新 todo: H001 → resolved

✅ 完成
```
