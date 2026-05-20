#!/usr/bin/env python3
"""
通用 Kanban 闭环集成框架（支持 todo 双向同步）

功能：
1. 解析任务输出，提取发现/问题/待办项
2. 自动创建 Kanban 卡片
3. 更新问题追踪器
4. 发送通知
5. **新增**: 写入/更新 todo-backlog.md（双向同步）

用法：
    # 标准模式：解析输出 → Kanban
    python kanban-sync.py --task <task_name> --output <output_file>
    
    # 写入 todo 模式：从 Kanban 同步到 todo
    python kanban-sync.py --task <task_name> --write-todo
    
    # 读取 todo 模式：从 todo 创建 Kanban
    python kanban-sync.py --task <task_name> --read-todo

todo-backlog.md 位置: 06-context/todo-tracking/todo-backlog.md
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
HERMES_ROOT = os.path.expanduser("~/.hermes")
KNOWLEDGE_PATH = os.path.join(HERMES_ROOT, "knowledge")
TRACKERS_DIR = os.path.join(KNOWLEDGE_PATH, "99-system", "trackers")
TODO_PATH = "<HERMES_DIR>/knowledge/06-context/todo-tracking/todo-backlog.md"
KANBAN_ASSIGNEE = "knowledge-ops"
KANBAN_WORKSPACE = f"dir:{KNOWLEDGE_PATH}"

# 优先级映射
PRIORITY_MAP = {
    "P0": 1,
    "P1": 2,
    "P2": 3,
    "P3": 4,
    "high": 1,
    "medium": 2,
    "low": 3,
}

# 反向映射（用于 todo 表格）
PRIORITY_LABEL = {
    1: "H",
    2: "M",
    3: "L",
}

# 任务配置
TASK_CONFIG = {
    "observer-self-check": {
        "name": "每日观察者自检",
        "tracker": "observer-self-check-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "weekly-plan": {
        "name": "每周计划",
        "tracker": "weekly-plan-tracker.md",
        "issue_pattern": r"(-\s*\[?\s*[xX]?[ \]]?\s*.+)",
        "default_severity": "P2",
    },
    "monthly-summary": {
        "name": "月度总结",
        "tracker": "monthly-summary-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "article-integration": {
        "name": "夜间文章整合",
        "tracker": "article-integration-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "dialogue-mining": {
        "name": "夜间对话挖掘",
        "tracker": "dialogue-mining-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "knowledge-amplifier": {
        "name": "夜间知识放大器",
        "tracker": "knowledge-amplifier-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "audit": {
        "name": "每周知识库审计",
        "tracker": "audit-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "lint": {
        "name": "周一知识库 Lint",
        "tracker": "lint-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P1",
    },
    "chronicle": {
        "name": "史官记录",
        "tracker": "chronicle-tracker.md",
        "issue_pattern": r"(-\s*\[?\s*[xX]?[ \]]?\s*.+)",
        "default_severity": "P2",
    },
    "auto-commit": {
        "name": "自动提交巡检",
        "tracker": "auto-commit-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "kanban-manager": {
        "name": "Kanban 管理层",
        "tracker": "kanban-manager-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "daily-brief": {
        "name": "每日早报",
        "tracker": "daily-brief-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "noon-reminder": {
        "name": "午间待办提醒",
        "tracker": "noon-reminder-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
    "evening-reminder": {
        "name": "晚间待办提醒",
        "tracker": "evening-reminder-tracker.md",
        "issue_pattern": r"([⚠️🔴🟡🟢✅❌]\s*.+)",
        "default_severity": "P2",
    },
}


def ensure_tracker_dir():
    """确保追踪器目录存在"""
    Path(TRACKERS_DIR).mkdir(parents=True, exist_ok=True)


def get_tracker_path(task_key: str) -> Path:
    """获取追踪器文件路径"""
    config = TASK_CONFIG.get(task_key, {})
    tracker_name = config.get("tracker", f"{task_key}-tracker.md")
    return Path(TRACKERS_DIR) / tracker_name


# ============================================================
# Todo 双向同步函数
# ============================================================

def read_todo_backlog() -> dict:
    """读取 todo-backlog.md，返回按优先级分类的项目"""
    if not Path(TODO_PATH).exists():
        return {"H": [], "M": [], "L": [], "done": []}
    
    content = Path(TODO_PATH).read_text(encoding='utf-8')
    items = {"H": [], "M": [], "L": [], "done": []}
    
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        
        # 检测章节
        if line.startswith('## 高优先级'):
            current_section = "H"
            continue
        elif line.startswith('## 中优先级'):
            current_section = "M"
            continue
        elif line.startswith('## 低优先级'):
            current_section = "L"
            continue
        elif line.startswith('## 已完成') or line.startswith('## 已解决'):
            current_section = "done"
            continue
        elif line.startswith('## 活跃待办'):
            # 兼容单一章节格式：活跃待办默认为 open/in_progress 状态
            current_section = "active"
            continue
        
        # 解析表格行
        if current_section and line.startswith('|') and not line.startswith('| ID'):
            # 跳过表头分隔行
            if '---' in line:
                continue
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                # 获取状态字段
                status = parts[3] if len(parts) > 3 else ""
                
                # 根据状态分类
                if status in ['open', 'in_progress']:
                    # 活跃待办默认放入 H 分类（后续可由任务调整优先级）
                    items["H"].append({
                        "id": parts[0],
                        "source": parts[1],
                        "description": parts[2],
                        "status": status,
                        "kanban_id": parts[4],
                        "created": parts[5] if len(parts) > 5 else "",
                        "updated": parts[6] if len(parts) > 6 else "",
                        "method": parts[7] if len(parts) > 7 else "",
                        "completed": parts[8] if len(parts) > 8 else "",
                    })
                elif status in ['completed', 'resolved', 'done']:
                    items["done"].append({
                        "id": parts[0],
                        "source": parts[1],
                        "description": parts[2],
                        "status": status,
                        "kanban_id": parts[4],
                        "created": parts[5] if len(parts) > 5 else "",
                        "updated": parts[6] if len(parts) > 6 else "",
                        "method": parts[7] if len(parts) > 7 else "",
                        "completed": parts[8] if len(parts) > 8 else "",
                    })
                elif current_section == "active":
                    # 活跃待办章节中的未分类项
                    items["H"].append({
                        "id": parts[0],
                        "source": parts[1],
                        "description": parts[2],
                        "status": status,
                        "kanban_id": parts[4],
                        "created": parts[5] if len(parts) > 5 else "",
                        "updated": parts[6] if len(parts) > 6 else "",
                        "method": parts[7] if len(parts) > 7 else "",
                        "completed": parts[8] if len(parts) > 8 else "",
                    })
    
    return items


def generate_todo_id(priority_label: str, todo_items: dict) -> str:
    """生成唯一 todo ID"""
    # 处理 P0/P1/P2/P3 格式
    if priority_label.startswith('P'):
        num = int(priority_label[1:])
        if num == 0:
            priority_label = "H"
        elif num <= 2:
            priority_label = "M"
        else:
            priority_label = "L"
    section = todo_items.get(priority_label, todo_items.get("H", []))
    existing_ids = [item["id"] for item in section]
    
    # 找到最大序号
    max_num = 0
    for id in existing_ids:
        try:
            num = int(id[1:])
            max_num = max(max_num, num)
        except:
            pass
    
    return f"{priority_label}{max_num + 1:03d}"


def write_todo_backlog(items: list, priority: str, source: str, kanban_id: str = "", todo_id: str = "") -> bool:
    """写入/更新 todo-backlog.md"""
    if not Path(TODO_PATH).exists():
        print(f"⚠️ todo-backlog.md 不存在: {TODO_PATH}")
        return False
    
    content = Path(TODO_PATH).read_text(encoding='utf-8')
    
    # 如果没传入 todo_id，则生成
    if not todo_id:
        todo_items = read_todo_backlog()
        todo_id = generate_todo_id(priority, todo_items)
    else:
        # 传入 todo_id 时仍需读取 todo_items 用于防重复检查
        todo_items = read_todo_backlog()
    
    # 确定优先级标签
    if priority in ["P0", "high", "H"]:
        section = "高优先级"
        priority_label = "H"
    elif priority in ["P1", "medium", "M", "P2"]:
        section = "中优先级"
        priority_label = "M"
    else:
        section = "低优先级"
        priority_label = "L"
    
    # 检查是否已存在（防重复）
    for item in todo_items.get(priority_label, []):
        if item["description"][:30] == items[0][:30] if items else False:
            print(f"⚠️ 问题已存在，跳过: {item['id']}")
            return False
    
    # 插入新行到表格
    now = datetime.now().strftime('%Y-%m-%d')
    new_row = f"| {todo_id} | {source} | {items[0][:50] if items else 'N/A'} | open | {kanban_id} | {now} | {now} | 待处理 | - |\n"
    
    # 找到对应章节的表格插入位置
    lines = content.split('\n')
    in_section = False
    new_lines = []
    inserted = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if f'## {section}' in line:
            in_section = True
            continue
        
        if in_section and line.startswith('|') and '---' in line:
            # 在表头分隔行后插入（匹配任意格式的表格分隔行）
            new_lines.append(new_row)
            inserted = True
            in_section = False
            break
    
    if not inserted:
        # 如果没找到，追加到文件末尾（不应发生）
        print(f"⚠️ 未找到 {section} 章节，追加到末尾")
        new_lines.append(new_row)
    
    Path(TODO_PATH).write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✅ 已写入 todo: {todo_id}")
    return True


def update_todo_from_kanban(kanban_id: str, status: str, completed_date: str = "", method: str = "") -> bool:
    """根据 Kanban 卡片状态更新 todo"""
    if not Path(TODO_PATH).exists():
        return False
    
    content = Path(TODO_PATH).read_text(encoding='utf-8')
    
    # 查找包含 kanban_id 的行
    for line in content.split('\n'):
        if kanban_id in line:
            # 解析现有行
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                # 更新状态
                parts[3] = status
                if completed_date:
                    parts[8] = completed_date
                if method:
                    parts[7] = method
                
                # 替换行
                new_line = '| ' + ' | '.join(parts) + ' |\n'
                content = content.replace(line, new_line)
                Path(TODO_PATH).write_text(content, encoding='utf-8')
                print(f"✅ 已更新 todo: {parts[0]} → {status}")
                return True
    
    print(f"⚠️ 未找到 kanban_id: {kanban_id}")
    return False


def update_todo_kanban_id(todo_id: str, kanban_id: str) -> bool:
    """更新 todo 中的 Kanban 卡片 ID"""
    if not Path(TODO_PATH).exists():
        return False
    
    content = Path(TODO_PATH).read_text(encoding='utf-8')
    
    # 查找包含 todo_id 的行
    for line in content.split('\n'):
        if todo_id in line:
            # 解析现有行
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 5:
                # 更新 Kanban 卡片 ID
                parts[4] = kanban_id
                # 更新最后更新时间
                parts[6] = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                # 替换行
                new_line = '| ' + ' | '.join(parts) + ' |\n'
                content = content.replace(line, new_line)
                Path(TODO_PATH).write_text(content, encoding='utf-8')
                print(f"   ✅ 已更新 todo {todo_id}: Kanban 卡片 = {kanban_id}")
                return True
    
    print(f"   ⚠️ 未找到 todo_id: {todo_id}")
    return False


def parse_output(output_file: str, task_key: str) -> list:
    """解析任务输出，提取发现/问题/待办项"""
    if not Path(output_file).exists():
        print(f"⚠️ 输出文件不存在: {output_file}")
        return []
    
    content = Path(output_file).read_text(encoding='utf-8')
    config = TASK_CONFIG.get(task_key, {})
    pattern = config.get("issue_pattern", r"([⚠️🔴🟡🟢✅❌]\s*.+)")
    
    items = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 按行解析
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 匹配问题/发现模式
        match = re.search(pattern, line)
        if match:
            text = match.group(1).strip()
            
            # 提取优先级
            severity = config.get("default_severity", "P2")
            if "P0" in text or "紧急" in text or "严重" in text:
                severity = "P0"
            elif "P1" in text or "重要" in text:
                severity = "P1"
            elif "P2" in text or "一般" in text:
                severity = "P2"
            elif "P3" in text or "可选" in text:
                severity = "P3"
            
            # 判断状态
            status = "open"
            if "✅" in text or "已完成" in text or "resolved" in text:
                status = "resolved"
            elif "🟡" in text or "进行中" in text or "in_progress" in text:
                status = "in_progress"
            elif "⚠️" in text or "🔴" in text:
                status = "open"
            
            items.append({
                "text": text,
                "severity": severity,
                "status": status,
                "date": today
            })
    
    return items


def get_existing_tracker_items(task_key: str) -> dict:
    """读取现有追踪器中的项目"""
    tracker_path = get_tracker_path(task_key)
    if not tracker_path.exists():
        return {}
    
    content = tracker_path.read_text(encoding='utf-8')
    items = {}
    
    # 解析追踪器中的项目
    # 格式: | ID | 内容 | 状态 | 日期 |
    pattern = r'\| ([A-Z]+-\d+) \| (.+?) \| (\w+) \| (\d{4}-\d{2}-\d{2}) \|'
    for match in re.finditer(pattern, content):
        items[match.group(1)] = {
            "text": match.group(2).strip(),
            "status": match.group(3),
            "date": match.group(4)
        }
    
    return items


def create_kanban_task(title: str, body: str, priority: int = 2,
                       assignee: str = KANBAN_ASSIGNEE, dry_run: bool = False) -> str | None:
    """创建 Kanban 卡片"""
    if dry_run:
        print(f"  [DRY RUN] 创建卡片: {title}")
        return None
    
    cmd = [
        "hermes", "kanban", "create",
        title,
        "--body", body,
        "--assignee", assignee,
        "--workspace", KANBAN_WORKSPACE,
        "--priority", str(priority),
        "--json"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ 创建卡片失败: {result.stderr[:200]}")
        return None
    
    try:
        data = json.loads(result.stdout)
        return data.get("id")
    except json.JSONDecodeError:
        print(f"⚠️ 解析输出失败: {result.stdout[:200]}")
        return None


def sync_to_kanban(items: list, existing_items: dict, task_key: str, dry_run: bool = False) -> dict:
    """同步项目到 Kanban"""
    results = {
        "created": [],
        "updated": [],
        "skipped": []
    }
    
    config = TASK_CONFIG.get(task_key, {})
    task_name = config.get("name", task_key)
    
    for item in items:
        # 生成唯一 ID
        item_id = f"{task_key[:3].upper()}-{datetime.now().strftime('%Y%m%d')}-{len(existing_items) + len(results['created']) + 1:03d}"
        
        # 检查是否已存在
        if item_id in existing_items:
            existing = existing_items[item_id]
            if existing.get("status") == "open" and item.get("status") == "open":
                results["skipped"].append({"id": item_id, "reason": "already_exists"})
            continue
        
        # 创建/更新卡片
        severity = item.get("severity", "P2")
        priority = PRIORITY_MAP.get(severity, 2)
        
        body = f"""🔍 {task_name} 发现

**内容**: {item['text']}
**严重程度**: {severity}
**状态**: {item['status']}
**日期**: {item['date']}

---
*自动同步自任务输出*
*下次执行时将更新状态*
"""
        
        title = f"[{task_name}] {item['text'][:50]}"
        if len(item['text']) > 50:
            title += "..."
        
        task_id = create_kanban_task(title, body, priority, dry_run=dry_run)
        
        if task_id:
            results["created"].append({"id": item_id, "task_id": task_id, "item": item})
    
    return results


def update_tracker(items: list, kanban_results: dict, task_key: str) -> None:
    """更新问题追踪器"""
    ensure_tracker_dir()
    tracker_path = get_tracker_path(task_key)
    config = TASK_CONFIG.get(task_key, {})
    task_name = config.get("name", task_key)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 读取或创建追踪器
    if tracker_path.exists():
        content = tracker_path.read_text(encoding='utf-8')
    else:
        content = f"""---
title: {task_name} 追踪器
type: tracker
tags: [kanban, tracking, {task_key}]
created: {today}
updated: {today}
---

# {task_name} 追踪器

> 自动追踪任务发现的问题/发现项，记录状态，防止遗漏。

---

## 修复状态说明

| 状态 | 说明 |
|------|------|
| 🔴 open | 新问题，尚未开始处理 |
| 🟡 in_progress | 正在处理中 |
| 🟢 resolved | 已处理，待验证 |
| ⚪ wontfix | 确认不处理（需说明原因） |

---

## 当前未处理项

> 下次任务执行时会自动对比此列表，更新状态。

| ID | 内容 | 严重程度 | 状态 | 日期 |
|----|------|----------|------|------|

---

## 已处理项历史

> 记录已处理的项目，用于验证效果。

| ID | 内容 | 处理日期 | 备注 |
|----|------|----------|------|
| - | - | - | 暂无 |

---

*此文件由 {task_name} 任务自动更新。*
"""
    
    # 更新内容（简化版，实际应更智能地更新表格）
    # 这里只是添加执行记录
    log_entry = f"\n## 执行记录\n\n| 日期 | 发现数 | 新建卡片 | 状态 |\n|------|--------|----------|------|\n| {today} | {len(items)} | {len(kanban_results['created'])} | 完成 |\n"
    
    # 如果文件末尾没有执行记录，添加
    if "## 执行记录" not in content:
        content += log_entry
        tracker_path.write_text(content, encoding='utf-8')
        print(f"✅ 追踪器已更新: {tracker_path}")


def main():
    parser = argparse.ArgumentParser(description='通用 Kanban 闭环（支持 todo 双向同步）')
    parser.add_argument('--task', required=True, help='任务名称 (如 observer-self-check)')
    parser.add_argument('--output', help='任务输出文件路径（标准模式）')
    parser.add_argument('--write-todo', action='store_true', help='写入 todo 模式：从输出写入 todo-backlog.md')
    parser.add_argument('--read-todo', action='store_true', help='读取 todo 模式：从 todo 创建 Kanban 卡片')
    parser.add_argument('--update-todo', action='store_true', help='更新 todo 模式：Kanban 状态变更回写 todo')
    parser.add_argument('--kanban-id', help='Kanban 卡片 ID（--update-todo 模式需要）')
    parser.add_argument('--status', help='新状态 (open/in_progress/resolved/wontfix，--update-todo 模式需要)')
    parser.add_argument('--completed-date', help='完成日期')
    parser.add_argument('--method', help='处理方式')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际创建卡片')
    parser.add_argument('--assignee', default=KANBAN_ASSIGNEE, help='卡片分配人')
    parser.add_argument('--priority', default='P2', help='默认优先级 (P0/P1/P2/P3)')
    
    args = parser.parse_args()
    
    print(f"=== 通用 Kanban 闭环（todo 双向同步）===")
    print(f"任务: {args.task}")
    print(f"模式: {'DRY RUN' if args.dry_run else 'LIVE'}")
    
    # 获取任务配置
    config = TASK_CONFIG.get(args.task, {})
    task_name = config.get("name", args.task)
    
    # 模式判断
    if args.update_todo:
        print(f"子模式: UPDATE_TODO（Kanban → todo）")
    elif args.write_todo:
        print(f"子模式: WRITE_TODO（输出 → todo）")
    
    # ========== READ_TODO 模式 ==========
    if args.read_todo:
        print("📋 步骤 1: 读取 todo-backlog.md...")
        todo_items = read_todo_backlog()
        
        # 获取任务名称
        config = TASK_CONFIG.get(args.task, {})
        task_name = config.get("name", args.task)
        
        # 统计待创建卡片数量
        open_items = todo_items.get("H", []) + todo_items.get("M", []) + todo_items.get("L", [])
        # 过滤掉已有 Kanban 卡片的
        pending_items = [item for item in open_items if not item.get("kanban_id")]
        
        print(f"   待创建 Kanban 的 todo: {len(pending_items)} 个")
        
        if not pending_items:
            print("   无待办需要创建 Kanban 卡片")
            return 0
        
        print("📌 步骤 2: 创建 Kanban 卡片...")
        for item in pending_items:
            kanban_id = create_kanban_task(
                title=f"[{task_name}] {item['description'][:60]}",
                body=f"来源: `{args.task}`\n\n原始待办 ID: {item['id']}\n\n问题描述: {item['description']}",
                assignee=args.assignee,
                priority=PRIORITY_MAP.get(args.priority, 2),
                dry_run=args.dry_run
            )
            
            if kanban_id and not args.dry_run:
                # 更新 todo 中的 Kanban 卡片 ID
                update_todo_kanban_id(item['id'], kanban_id)
        
        print("\n✅ 读取 todo 并创建 Kanban 完成")
        return 0
    else:
        print(f"子模式: STANDARD（输出 → Kanban → tracker）")
    
    print()
    
    # 检查任务配置
    if args.task not in TASK_CONFIG:
        print(f"⚠️ 未知任务: {args.task}")
        print(f"可用任务: {', '.join(TASK_CONFIG.keys())}")
        print("\n如需添加新任务，请编辑脚本中的 TASK_CONFIG 字典。")
        return 1
    
    config = TASK_CONFIG.get(args.task, {})
        
    # ========== WRITE_TODO 模式 ==========
    if args.write_todo:
        if not args.output:
            print("⚠️ --write-todo 模式需要 --output 参数")
            return 1
        
        print("📋 步骤 1: 解析任务输出...")
        items = parse_output(args.output, args.task)
        print(f"   发现项目: {len(items)} 个")
        
        print("📝 步骤 2: 写入 todo-backlog.md...")
        # 先读取一次 todo 状态，用于生成唯一 ID
        todo_items = read_todo_backlog()
        
        # 按优先级分组，批量写入同一章节
        from collections import defaultdict
        items_by_priority = defaultdict(list)
        todo_ids_by_priority = defaultdict(list)
        
        for item in items:
            priority_label = "H" if item['severity'] in ["P0", "high", "H"] else ("M" if item['severity'] in ["P1", "medium", "M", "P2"] else "L")
            todo_id = generate_todo_id(item['severity'], todo_items)
            todo_ids_by_priority[priority_label].append(todo_id)
            if priority_label not in todo_items:
                todo_items[priority_label] = []
            todo_items[priority_label].append({"id": todo_id})
            items_by_priority[priority_label].append(item)
        
        # 批量写入每个优先级章节
        for priority_label, section_items in items_by_priority.items():
            section_name = {"H": "高优先级", "M": "中优先级", "L": "低优先级"}.get(priority_label, "低优先级")
            ids = todo_ids_by_priority[priority_label]
            
            # 一次性读取文件并插入所有行
            content = Path(TODO_PATH).read_text(encoding='utf-8')
            now = datetime.now().strftime('%Y-%m-%d')
            
            # 生成所有新行
            new_rows = []
            for i, item in enumerate(section_items):
                todo_id = ids[i]
                new_row = f"| {todo_id} | `{args.task[:8]}` {task_name} | {item['text'][:50]} | open | | {now} | {now} | 待处理 | - |\n"
                new_rows.append(new_row)
            
            # 找到章节并插入所有行
            lines = content.split('\n')
            new_lines = []
            in_section = False
            inserted = False
            
            for line in lines:
                new_lines.append(line)
                if f'## {section_name}' in line:
                    in_section = True
                    continue
                if in_section and line.startswith('|') and '---' in line and not inserted:
                    new_lines.extend(new_rows)
                    inserted = True
                    in_section = False
            
            if not inserted:
                print(f"⚠️ 未找到 {section_name} 章节，追加到末尾")
                new_lines.append('\n')
                new_lines.extend(new_rows)
            
            Path(TODO_PATH).write_text('\n'.join(new_lines), encoding='utf-8')
            for todo_id in ids:
                print(f"✅ 已写入 todo: {todo_id}")
        
        print("\n✅ 写入 todo 完成")
        return 0
    
    # ========== UPDATE_TODO 模式 ==========
    # ========== UPDATE_TODO 模式 ==========
    if args.update_todo:
        if not args.kanban_id:
            print("⚠️ --update-todo 模式需要 --kanban-id 参数")
            return 1
        if not args.status:
            print("⚠️ --update-todo 模式需要 --status 参数 (open/in_progress/resolved/wontfix)")
            return 1
        
        print(f"📝 步骤 1: 更新 todo-backlog.md...")
        success = update_todo_from_kanban(args.kanban_id, args.status, args.completed_date, args.method)
        
        if success:
            print(f"✅ 已更新 todo 状态: {args.status}")
        else:
            print(f"⚠️ 未找到 kanban_id: {args.kanban_id}")
        return 0

    # ========== READ_TODO 模式 ==========
    if args.read_todo:
        print("📝 步骤 1: 读取 todo-backlog.md...")
        todo_items = read_todo_backlog()
        
        open_items = []
        for priority, items in todo_items.items():
            if priority == "done":
                continue
            for item in items:
                if item.get("status") == "open" and not item.get("kanban_id"):
                    open_items.append({
                        "priority": priority,
                        "item": item
                    })
        
        print(f"   待创建 Kanban 的 todo: {len(open_items)} 个")
        
        print("📌 步骤 2: 创建 Kanban 卡片...")
        for entry in open_items:
            item = entry["item"]
            priority = entry["priority"]
            
            title = f"[{task_name}] {item['description'][:50]}"
            body = f"""🔍 从 todo-backlog.md 同步

**内容**: {item['description']}
**来源**: {item['source']}
**优先级**: {priority}

---
*自动同步自 todo-backlog.md*
"""
            task_id = create_kanban_task(title, body, PRIORITY_MAP.get(priority, 2), dry_run=args.dry_run)
            
            if task_id:
                # 更新 todo 中的 kanban_id
                update_todo_from_kanban(task_id, "in_progress")
                print(f"   ✅ {item['id']}: 创建卡片 {task_id}")
        
        return 0
    
    # ========== 标准模式 ==========
    print("📋 步骤 1: 解析任务输出...")
    if not args.output:
        print("⚠️ 标准模式需要 --output 参数")
        return 1
    
    items = parse_output(args.output, args.task)
    print(f"   发现项目: {len(items)} 个")
    
    # 步骤 2: 读取现有追踪器
    print("📝 步骤 2: 读取现有追踪器...")
    existing_items = get_existing_tracker_items(args.task)
    print(f"   已有项目: {len(existing_items)} 个")
    
    # 步骤 3: 同步到 Kanban
    print("📌 步骤 3: 同步到 Kanban...")
    kanban_results = sync_to_kanban(items, existing_items, args.task, args.dry_run)
    print(f"   新建卡片: {len(kanban_results['created'])} 个")
    print(f"   更新卡片: {len(kanban_results['updated'])} 个")
    print(f"   跳过: {len(kanban_results['skipped'])} 个")
    
    # 步骤 3b: 写入 todo（新增）
    if kanban_results['created']:
        print("📝 步骤 3b: 写入 todo-backlog.md...")
        for result in kanban_results['created']:
            write_todo_backlog(
                items=[result['item']['text']],
                priority=result['item']['severity'],
                source=f"`{args.task[:8]}` {task_name}",
                kanban_id=result['task_id']
            )
    
    # 步骤 4: 更新追踪器
    print("📝 步骤 4: 更新追踪器...")
    update_tracker(items, kanban_results, args.task)
    
    # 摘要
    print()
    print("=" * 50)
    print("📊 执行摘要")
    print("=" * 50)
    print(f"任务输出: {args.output}")
    print(f"发现项目: {len(items)} 个")
    print(f"新建 Kanban 卡片: {len(kanban_results['created'])} 个")
    print(f"写入 todo: {len(kanban_results['created'])} 个")
    
    if kanban_results['created']:
        print("\n🆕 新建卡片:")
        for item in kanban_results['created']:
            print(f"   - [{item['id']}] {item['task_id']}: {item['item']['text'][:50]}...")
    
    if args.dry_run:
        print("\n⚠️ 这是 DRY RUN，没有实际创建卡片")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
