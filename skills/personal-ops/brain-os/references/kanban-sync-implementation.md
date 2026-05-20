# kanban-sync.py 实现参考

## 核心函数

### read_todo_backlog(todo_path)

读取 todo 中 open 状态的待办，用于 Kanban 管理层创建卡片。

```python
def read_todo_backlog(todo_path: Path) -> list[dict]:
    """读取 todo 中 open 状态的待办"""
    todos = []
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for line in content.split('\n'):
        if '| ' in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                status = parts[3] if len(parts) > 3 else ""
                if "open" in status.lower():
                    todos.append({
                        'id': parts[0],
                        'source': parts[1],
                        'description': parts[2],
                        'status': status,
                        'kanban_id': parts[4],
                        'created': parts[5],
                        'updated': parts[6],
                        'method': parts[7],
                        'completed': parts[8],
                    })
    return todos
```

### write_todo_backlog(todo_path, problem_summary, source_task, priority)

写入 todo（防重复），用于生产者任务。

```python
def write_todo_backlog(todo_path: Path, problem_summary: str, source_task: str, priority: str) -> str:
    """写入 todo（防重复）"""
    # 1. 检查是否已存在相同问题
    existing = find_duplicate(todo_path, problem_summary, source_task)
    if existing:
        return existing['id']  # 返回已存在的 ID
    
    # 2. 生成唯一 ID
    todo_id = generate_todo_id(priority, todo_path)
    
    # 3. 写入 todo
    new_entry = f"| {todo_id} | `{source_task}` | {problem_summary} | open | - | {datetime.now().strftime('%Y-%m-%d')} | {datetime.now().strftime('%Y-%m-%d')} | - | - |\n"
    
    # 根据优先级插入到对应区域
    # H: 高优先级区域
    # M: 中优先级区域
    # L: 低优先级区域
    
    return todo_id
```

### update_todo_from_kanban(todo_path, kanban_id, new_status, completed_date=None, method=None)

根据 Kanban 状态更新 todo，用于回写闭环。

```python
def update_todo_from_kanban(todo_path: Path, kanban_id: str, new_status: str, 
                           completed_date: str = None, method: str = None) -> bool:
    """根据 Kanban 状态更新 todo"""
    with open(todo_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if kanban_id in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                # 更新状态
                parts[3] = new_status
                # 更新完成时间
                if completed_date:
                    parts[8] = completed_date
                # 更新处理方式
                if method:
                    parts[7] = method
                # 更新最后更新时间
                parts[6] = datetime.now().strftime('%Y-%m-%d')
                
                # 重新组合行
                new_line = '| ' + ' | '.join(parts) + ' |\n'
                lines[i] = new_line
                break
    
    with open(todo_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True
```

## 防重复机制

```python
def find_duplicate(todo_path: Path, problem_summary: str, source_task: str) -> dict | None:
    """检查 todo 中是否已存在相同问题"""
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for line in content.split('\n'):
        if '| ' in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 3:
                existing_desc = parts[2] if len(parts) > 2 else ""
                existing_source = parts[1] if len(parts) > 1 else ""
                
                # 检查问题摘要相似度
                if problem_summary[:20] in existing_desc[:20]:
                    # 检查来源任务
                    if source_task in existing_source:
                        return {
                            'id': parts[0],
                            'status': parts[3],
                            'kanban_id': parts[4],
                        }
    return None
```

## 优先级生成 ID

```python
def generate_todo_id(priority: str, todo_path: Path) -> str:
    """生成唯一 ID（H001, M001, L001...）"""
    with open(todo_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计该优先级下已存在的最大序号
    max_num = 0
    for line in content.split('\n'):
        if '| ' in line and '---' not in line:
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) > 0:
                todo_id = parts[0]
                if todo_id.startswith(priority):
                    try:
                        num = int(todo_id[1:])
                        max_num = max(max_num, num)
                    except ValueError:
                        pass
    
    return f"{priority}{max_num + 1:03d}"
```

## 命令行参数

```python
import argparse

parser = argparse.ArgumentParser(description='Kanban 双向同步工具')
parser.add_argument('--task', required=True, help='任务名称')
parser.add_argument('--write-todo', action='store_true', help='输出 → todo')
parser.add_argument('--read-todo', action='store_true', help='todo → Kanban')
parser.add_argument('--update-todo', action='store_true', help='Kanban → todo')
parser.add_argument('--output', help='任务输出文件路径')
parser.add_argument('--kanban-id', help='Kanban 卡片 ID')
parser.add_argument('--status', help='新状态 (open/in_progress/resolved/wontfix)')
parser.add_argument('--completed-date', help='完成日期')
parser.add_argument('--method', help='处理方式')
parser.add_argument('--dry-run', action='store_true', help='预览模式')

args = parser.parse_args()
```

## 使用示例

```bash
# 生产者模式：输出 → todo
python3 kanban-sync.py --task observer-self-check --write-todo --output observer-output.md

# 管理层模式：todo → Kanban
python3 kanban-sync.py --task kanban-manager --read-todo

# 回写模式：Kanban → todo
python3 kanban-sync.py --task kanban-manager --update-todo --kanban-id t_a3268cfc --status resolved --completed-date 2026-05-18 --method "自动修复"

# 预览模式
python3 kanban-sync.py --task test --write-todo --dry-run
```
