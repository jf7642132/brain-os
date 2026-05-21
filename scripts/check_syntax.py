#!/usr/bin/env python3
"""检查 kanban-sync.py 语法"""
import os
scripts_dir = os.environ.get('HERMES_SCRIPTS_DIR', os.path.expanduser('~/.hermes/scripts'))
kanban_sync = os.path.join(scripts_dir, 'kanban-sync.py')
compile(open(kanban_sync).read(), kanban_sync, 'exec')
print('✅ Syntax OK')
