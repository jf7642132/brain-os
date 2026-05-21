#!/usr/bin/env python3
"""
Brain OS Kanban 同步工具

将本地 kanban 任务同步到 git 仓库，保持版本历史。
灵感来源于 Karpathy LLM Wiki 概念和 Obsidian-Brain-OS 的 git-backed brain 设计。

用法:
    python kanban-sync.py              # 同步当前状态
    python kanban-sync.py --dry-run    # 预览变更
    python kanban-sync.py --commit     # 直接提交
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 环境变量配置
HERMES_ROOT = os.environ.get("HERMES_ROOT", str(Path.home() / ".hermes"))
HERMES_KNOWLEDGE = os.environ.get("HERMES_KNOWLEDGE", str(Path(HERMES_ROOT) / "knowledge"))
HERMES_TODO_PATH = os.environ.get(
    "HERMES_TODO_PATH",
    str(Path(HERMES_KNOWLEDGE) / "06-context" / "todo-tracking" / "todo-backlog.md")
)
GIT_REPO = os.environ.get("BRAINO_GIT_REPO", str(Path(HERMES_ROOT) / "brain-os"))


def run_cmd(cmd, cwd=None):
    """运行 shell 命令"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr


def parse_todo_backlog(content):
    """解析 todo-backlog.md 内容"""
    tasks = []
    lines = content.split("\n")
    
    for line in lines:
        line = line.strip()
        if line.startswith("- [") and "]" in line:
            # 解析任务行
            parts = line.split("]", 1)
            status = "pending" if parts[0].endswith("[ ]") else "completed" if parts[0].endswith("[x]") else "in_progress"
            if len(parts) > 1:
                task_text = parts[1].strip().lstrip("- ")
                tasks.append({"status": status, "content": task_text})
    
    return tasks


def sync_kanban(dry_run=False, commit=False):
    """同步 kanban 到 git"""
    print("=" * 60)
    print("Brain OS Kanban 同步工具")
    print("=" * 60)
    
    # 检查 todo 文件
    if not Path(HERMES_TODO_PATH).exists():
        print(f"⚠️ 未找到 todo 文件: {HERMES_TODO_PATH}")
        print("请确保已创建 todo-backlog.md")
        return False
    
    # 读取当前状态
    with open(HERMES_TODO_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    tasks = parse_todo_backlog(content)
    print(f"\n📋 当前任务数: {len(tasks)}")
    
    for task in tasks[:5]:  # 显示前 5 个
        status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}.get(task["status"], "❓")
        print(f"  {status_icon} {task['content'][:50]}...")
    
    if len(tasks) > 5:
        print(f"  ... 还有 {len(tasks) - 5} 个任务")
    
    # 检查 git 仓库
    if not Path(GIT_REPO / ".git").exists():
        print(f"\n⚠️ Git 仓库未初始化: {GIT_REPO}")
        print("请运行: git init")
        return False
    
    # 计算变更
    returncode, stdout, stderr = run_cmd("git status --porcelain", cwd=GIT_REPO)
    changes = stdout.strip()
    
    if not changes:
        print("\n✅ 无变更，无需同步")
        return True
    
    print(f"\n📝 检测到变更:")
    for line in changes.split("\n"):
        if line:
            print(f"  {line}")
    
    if dry_run:
        print("\n🔍 预览模式，未执行实际变更")
        return True
    
    # 执行同步
    print("\n🔄 正在同步...")
    
    # git add
    run_cmd("git add -A", cwd=GIT_REPO)
    
    if commit:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        run_cmd(f'git commit -m "kanban sync: {timestamp}"', cwd=GIT_REPO)
        print("✅ 已提交")
    
    # git push (可选)
    push = os.environ.get("BRAINO_AUTO_PUSH", "false").lower() == "true"
    if push:
        run_cmd("git push", cwd=GIT_REPO)
        print("✅ 已推送")
    
    print("\n✅ 同步完成")
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    commit = "--commit" in sys.argv
    
    sync_kanban(dry_run=dry_run, commit=commit)


if __name__ == "__main__":
    main()