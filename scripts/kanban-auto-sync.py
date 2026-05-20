#!/usr/bin/env python3
"""
Kanban → Todo 自动同步脚本
定期扫描所有 done/resolved 状态的 Kanban 卡片，自动更新 todo-backlog.md
"""

import subprocess
import json
from datetime import datetime

TODO_PATH = "/root/.hermes/knowledge/06-context/todo-tracking/todo-backlog.md"
SCRIPT_PATH = "/root/.hermes/scripts/kanban-sync.py"

def get_done_kanban_tasks():
    """获取所有 done 状态的 Kanban 卡片"""
    result = subprocess.run(
        ['hermes', 'kanban', 'list', '--status', 'done', '--json'],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"⚠️ 获取 Kanban 任务失败: {result.stderr[:200]}")
        return []
    
    try:
        tasks = json.loads(result.stdout)
        return tasks
    except json.JSONDecodeError:
        print(f"⚠️ 解析输出失败: {result.stdout[:200]}")
        return []

def main():
    print(f"=== Kanban → Todo 自动同步 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 获取所有 done 的 Kanban 卡片
    done_tasks = get_done_kanban_tasks()
    print(f"找到 {len(done_tasks)} 个已完成任务")
    
    if not done_tasks:
        print("无已完成任务需要同步")
        return
    
    # 逐个更新 todo
    for task in done_tasks:
        kanban_id = task.get('id')
        if not kanban_id:
            continue
        
        # 检查 todo 中是否已有该 kanban_id
        with open(TODO_PATH, 'r') as f:
            content = f.read()
        
        if kanban_id in content:
            # 检查状态是否已经更新
            for line in content.split('\n'):
                if kanban_id in line and 'resolved' in line:
                    print(f"   ⏭️  {kanban_id} 已同步，跳过")
                    break
            else:
                # 需要更新
                print(f"   📝 更新 {kanban_id} → resolved")
                subprocess.run([
                    'python3', SCRIPT_PATH,
                    '--task', 'kanban-manager', '--update-todo',
                    '--kanban-id', kanban_id, '--status', 'resolved',
                    '--completed-date', datetime.now().strftime('%Y-%m-%d'),
                    '--method', '自动同步'
                ])
        else:
            print(f"   ⚠️  {kanban_id} 不在 todo 中，跳过")
    
    print("\n✅ 自动同步完成")

if __name__ == '__main__':
    main()
