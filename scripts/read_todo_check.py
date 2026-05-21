#!/usr/bin/env python3
"""检查 todo 中待创建的待办"""
import os
import sys
sys.path.insert(0, os.environ.get('HERMES_SCRIPTS_DIR', os.path.expanduser('~/.hermes/scripts')))
from kanban_sync import read_todo_backlog, create_kanban_task, update_todo_kanban_id

items = read_todo_backlog()
for priority_label, items_list in [('H', items.get('H', [])), ('M', items.get('M', [])), ('L', items.get('L', []))]:
    label_map = {'H': '高', 'M': '中', 'L': '低'}
    print(f'\n=== {label_map[priority_label]}优先级 ({len(items_list)} 项) ===')
    for i in items_list:
        has_kanban = '✅' if i['kanban_id'] else '❌'
        print(f'  [{i["id"]}] {i["description"][:60]} | kanban_id={i["kanban_id"] or "(空)"} {has_kanban} | status={i["status"]}')
