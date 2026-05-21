#!/usr/bin/env python3
"""
夜间流水线发现项自动写入 todo-backlog.md

功能：
1. 解析流水线输出文件，提取问题/发现/待办项
2. 自动追加到 todo-backlog.md（支持两种格式：列表式和表格式）
3. 生成唯一 todo ID，防重复
4. 支持 dry-run 模式

用法：
    # 从输出文件写入 todo
    python write-todo-from-output.py --output <output_file> --source <source_name> [--priority P1|P2|P3]

    # 直接传入待办内容
    python write-todo-from-output.py --items "问题描述1" "问题描述2" --source "conversation-flywheel"

    # Dry-run 模式（不实际写入）
    python write-todo-from-output.py --output report.md --dry-run

todo-backlog.md 位置: ~/.hermes/todo-backlog.md
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 配置
HERMES_ROOT = os.path.expanduser("~/.hermes")
TODO_PATH = os.environ.get("HERMES_TODO_PATH", os.path.expanduser("~/.hermes/todo-backlog.md"))

# 优先级映射
PRIORITY_MAP = {
    "P0": ("H", "🔴"),
    "P1": ("M", "🟡"),
    "P2": ("L", "🟢"),
    "P3": ("L", "⚪"),
    "high": ("H", "🔴"),
    "medium": ("M", "🟡"),
    "low": ("L", "🟢"),
}

# 反解析模式：从文本中提取优先级
PRIORITY_RE = re.compile(r'\b(P0|P1|P2|P3|high|medium|low|紧急|重要|一般|可选)\b', re.IGNORECASE)
STATUS_RE = re.compile(r'\b(open|in_progress|blocked|待执行|待确认|阻塞|进行中|已完成|resolved|done)\b', re.IGNORECASE)


def detect_todo_format(content: str) -> str:
    """检测 todo-backlog.md 的格式类型"""
    if '| ID |' in content or '|---|' in content:
        return "table"
    elif re.search(r'^- \[obs-\d+\]', content, re.MULTILINE):
        return "list"
    elif re.search(r'^### \[', content, re.MULTILINE):
        return "detail"
    return "list"  # 默认


def extract_items_from_output(output_file: str) -> list:
    """从流水线输出文件中提取问题/发现/待办项"""
    content = Path(output_file).read_text(encoding='utf-8')
    items = []
    today = datetime.now().strftime('%Y-%m-%d')

    # 模式1: 带 emoji 标记的问题行
    emoji_pattern = re.compile(r'^\s*([⚠️🔴🟡🟢✅❌🆕])\s*(.+)$', re.MULTILINE)
    for match in emoji_pattern.finditer(content):
        emoji = match.group(1)
        text = match.group(2).strip()
        # 跳过明显的非问题行
        if any(skip in text.lower() for skip in ['success', '完成', 'passed', '✅ 任务']):
            continue
        items.append({
            "text": text,
            "emoji": emoji,
            "date": today,
            "raw_line": match.group(0)
        })

    # 模式2: "问题:" / "发现:" / "待办:" 开头的段落
    section_pattern = re.compile(r'^\s*(?:问题|发现|待办|需要|建议|TODO|todo)\s*[:：]\s*(.+)$', re.MULTILINE)
    for match in section_pattern.finditer(content):
        text = match.group(1).strip()
        if len(text) > 10:  # 过滤太短的
            items.append({
                "text": text,
                "emoji": "⚠️",
                "date": today,
                "raw_line": match.group(0)
            })

    # 模式3: 带方括号的待办项 [ ] 或 [x]
    todo_pattern = re.compile(r'^\s*-\s*\[([ xX])\]\s*(.+)$', re.MULTILINE)
    for match in todo_pattern.finditer(content):
        checked = match.group(1).strip().lower() == 'x'
        text = match.group(2).strip()
        if not checked and len(text) > 10:
            items.append({
                "text": text,
                "emoji": "🟡",
                "date": today,
                "raw_line": match.group(0)
            })

    # 模式4: 带文本标记的行（[WARN], [CRITICAL], [TODO], [ACTION] 等）
    tag_pattern = re.compile(r'^\s*-\s*\[(WARN|WARNING|CRITICAL|TODO|ACTION|FIX|BUG|ISSUE|风险|问题|阻塞|建议|需要|待办)\]\s*(.+)$', re.MULTILINE)
    for match in tag_pattern.finditer(content):
        tag = match.group(1).lower()
        text = match.group(2).strip()
        if len(text) > 10:
            # 根据标签映射 emoji
            emoji_map = {
                'warn': '🔴', 'warning': '🔴', 'critical': '🔴',
                'todo': '🟡', 'action': '🟡', 'fix': '🟡',
                'bug': '🔴', 'issue': '🟡', '风险': '🔴',
                '问题': '🟡', '阻塞': '🔴', '建议': '🟢',
                '需要': '🟡', '待办': '🟡',
            }
            items.append({
                "text": text,
                "emoji": emoji_map.get(tag, '🟡'),
                "date": today,
                "raw_line": match.group(0)
            })

    # 模式5: 带有问题关键词的 bullet 项（不依赖标记）
    kw_pattern = re.compile(r'^\s*-\s+(.+)$', re.MULTILINE)
    keyword_set = {'风险', '问题', '阻塞', '故障', '需要', '应该', '建议', '待办',
                   '修复', '优化', '升级', '迁移', '配置', '审计', '确认',
                   '排查', '处理', '解决', '更新', '引入', '限制', '告警',
                   '错误', '失败', '超时', '过期', '轮换'}
    for match in kw_pattern.finditer(content):
        text = match.group(1).strip()
        if len(text) > 15:
            found_kw = [kw for kw in keyword_set if kw in text]
            if found_kw:
                items.append({
                    "text": text,
                    "emoji": "🟡",
                    "date": today,
                    "raw_line": match.group(0),
                    "keyword_match": found_kw
                })

    # 去重（基于经过清洗的文本前40字符）
    seen = set()
    unique_items = []
    for item in items:
        # 清洗文本：去掉 [TAG] 前缀
        text = item["text"]
        text = re.sub(r'^\[(WARN|WARNING|CRITICAL|TODO|ACTION|FIX|BUG|ISSUE|风险|问题|阻塞|建议|需要|待办)\]\s*', '', text, flags=re.IGNORECASE).strip()
        text = re.sub(r'^[⚠️🔴🟡🟢✅❌🆕]\s*', '', text).strip()
        key = text[:40]
        if key not in seen:
            seen.add(key)
            item["text"] = text  # 使用清洗后的文本
            unique_items.append(item)

    return unique_items


def generate_todo_id(todo_items: dict, priority_label: str) -> str:
    """生成唯一 todo ID"""
    section = todo_items.get(priority_label, [])
    existing_ids = [item.get("id", "") for item in section]

    max_num = 0
    for id in existing_ids:
        if id.startswith(priority_label):
            try:
                num = int(id[len(priority_label):])
                max_num = max(max_num, num)
            except ValueError:
                pass

    return f"{priority_label}{max_num + 1:03d}"


def parse_priority_and_status(text: str, default_priority: str = "P2") -> tuple:
    """从文本中解析优先级和状态"""
    severity = default_priority
    status = "open"

    # 解析优先级
    match = PRIORITY_RE.search(text)
    if match:
        val = match.group(1).lower()
        if val in ["紧急", "p0"]:
            severity = "P0"
        elif val in ["重要", "p1"]:
            severity = "P1"
        elif val in ["一般", "p2"]:
            severity = "P2"
        elif val in ["可选", "p3"]:
            severity = "P3"
        elif val == "high":
            severity = "P0"
        elif val == "medium":
            severity = "P1"
        elif val == "low":
            severity = "P2"

    # 解析状态
    if any(kw in text for kw in ["阻塞", "blocked", "🔴"]):
        status = "blocked"
    elif any(kw in text for kw in ["进行中", "in_progress", "🟡"]):
        status = "in_progress"
    elif any(kw in text for kw in ["已完成", "resolved", "done", "✅"]):
        status = "completed"
    elif any(kw in text for kw in ["待确认"]):
        status = "pending_confirm"
    elif any(kw in text for kw in ["待执行"]):
        status = "pending_exec"

    return severity, status


def read_todo_backlog() -> dict:
    """读取 todo-backlog.md，返回结构化数据"""
    if not Path(TODO_PATH).exists():
        return {"H": [], "M": [], "L": [], "done": [], "format": "unknown"}

    content = Path(TODO_PATH).read_text(encoding='utf-8')
    fmt = detect_todo_format(content)
    items = {"H": [], "M": [], "L": [], "done": [], "format": fmt}

    if fmt == "list":
        # 列表格式: - [obs-001] 🔴 **标题** (类型, 状态)
        pattern = re.compile(r'^- \[([A-Z]+\d+)\]\s*(🔴|🟡|🟢|⚪)\s*\*\*(.+?)\*\*\s*\((.+?),\s*(.+?)\)', re.MULTILINE)
        for match in pattern.finditer(content):
            item_id = match.group(1)
            emoji = match.group(2)
            desc = match.group(3)
            typ = match.group(4)
            status = match.group(5)

            priority_label = "H" if emoji == "🔴" else ("M" if emoji == "🟡" else "L")
            if status in ["completed", "done", "已解决"]:
                items["done"].append({"id": item_id, "description": desc, "status": status, "type": typ})
            else:
                items[priority_label].append({"id": item_id, "description": desc, "status": status, "type": typ})

    elif fmt == "detail":
        # 详细格式: ### [状态] 标题
        pattern = re.compile(r'^### \[(.+?)\]\s*(.+)$', re.MULTILINE)
        current = None
        for match in pattern.finditer(content):
            status = match.group(1)
            title = match.group(2)
            current = {"id": "", "description": title, "status": status, "type": "detail"}
            # 读取后续行获取优先级
            lines = content[match.end():].split('\n')
            for line in lines[:10]:
                if line.startswith('- **优先级**:'):
                    p = line.split(':', 1)[1].strip()
                    if p == "高":
                        items["H"].append(current)
                    elif p == "中":
                        items["M"].append(current)
                    else:
                        items["L"].append(current)
                    break
            current = None

    return items


def write_todo_list_format(items: list, source: str, dry_run: bool = False) -> list:
    """以列表格式写入 todo-backlog.md"""
    if not Path(TODO_PATH).exists():
        print(f"⚠️ todo-backlog.md 不存在: {TODO_PATH}")
        return []

    content = Path(TODO_PATH).read_text(encoding='utf-8')
    todo_items = read_todo_backlog()
    created = []

    for item in items:
        severity, status = parse_priority_and_status(item["text"])
        priority_label, emoji = PRIORITY_MAP[severity]

        # 检查重复
        desc_short = item["text"][:30]
        for existing in todo_items.get(priority_label, []):
            if existing.get("description", "")[:30] == desc_short:
                print(f"⚠️ 问题已存在，跳过: {existing.get('id', 'unknown')}")
                continue

        todo_id = generate_todo_id(todo_items, priority_label)
        created.append({"id": todo_id, "text": item["text"], "severity": severity, "status": status})

        new_entry = f"- [{todo_id}] {emoji} **{item['text'][:80]}** ({source}, {status})\n"

        if dry_run:
            print(f"  [DRY RUN] 待写入: [{todo_id}] {emoji} {item['text'][:60]}...")
            continue

        # 在 "# Todo Backlog" 标题后、日期分隔线前插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        insert_idx = None

        for i, line in enumerate(lines):
            if line.strip() == "# Todo Backlog":
                insert_idx = i + 1  # 在 # Todo Backlog 之后
                new_lines.append(line)
            elif insert_idx is not None and not inserted and line.startswith('# 待办事项'):
                # 在当前行之前插入（即：在现有列表项之后、日期标题之前）
                new_lines.append(new_entry)
                inserted = True
                new_lines.append(line)
            else:
                new_lines.append(line)

        if not inserted:
            # 追加到 # Todo Backlog 后
            for i, line in enumerate(new_lines):
                if line.strip() == "# Todo Backlog":
                    new_lines.insert(i + 1, "")
                    new_lines.insert(i + 2, new_entry)
                    break

        Path(TODO_PATH).write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"✅ 已写入 todo: [{todo_id}] {emoji} {item['text'][:60]}...")

    return created


def write_todo_detail_format(items: list, source: str, date_str: str, dry_run: bool = False) -> list:
    """以详细格式追加到当日待办区块"""
    if not Path(TODO_PATH).exists():
        print(f"⚠️ todo-backlog.md 不存在: {TODO_PATH}")
        return []

    content = Path(TODO_PATH).read_text(encoding='utf-8')
    created = []

    for item in items:
        severity, status = parse_priority_and_status(item["text"])
        priority_label, emoji = PRIORITY_MAP[severity]
        todo_id = f"obs-{generate_todo_id(read_todo_backlog(), priority_label)[1:]}"

        created.append({"id": todo_id, "text": item["text"], "severity": severity, "status": status})

        detail_block = f"""
### [{status}] {item['text'][:60]}
- **问题**: {item['text']}
- **优先级**: {"高" if severity in ["P0", "P1"] else "中" if severity == "P2" else "低"}
- **类型**: {source}
- **状态**: {status}
- **建议操作**: 人工审查并处理
"""

        if dry_run:
            print(f"  [DRY RUN] 待追加详细区块: [{todo_id}] {item['text'][:60]}...")
            continue

        # 找到当日区块（# 待办事项 — YYYY-MM-DD）
        date_header = f"# 待办事项 — {date_str}"
        if date_header in content:
            # 追加到当日区块末尾（下一个 ## 或文件末尾之前）
            parts = content.split(date_header)
            if len(parts) >= 2:
                rest = parts[1]
                # 找到下一个顶级标题
                next_header_match = re.search(r'\n\n# ', rest)
                if next_header_match:
                    insert_pos = next_header_match.start() + 1
                    new_content = parts[0] + date_header + rest[:insert_pos] + detail_block + rest[insert_pos:]
                else:
                    new_content = content + detail_block
                Path(TODO_PATH).write_text(new_content, encoding='utf-8')
        else:
            # 创建新的当日区块
            new_section = f"""

# 待办事项 — {date_str}

## 夜间流水线发现

{detail_block.strip()}
"""
            Path(TODO_PATH).write_text(content + new_section, encoding='utf-8')

        print(f"✅ 已追加详细区块: [{todo_id}] {item['text'][:60]}...")

    return created


def main():
    parser = argparse.ArgumentParser(description='夜间流水线发现项自动写入 todo-backlog.md')
    parser.add_argument('--output', help='流水线输出文件路径')
    parser.add_argument('--items', nargs='+', help='直接传入待办项文本')
    parser.add_argument('--source', default='nightly-pipeline', help='来源名称（用于 todo 标记）')
    parser.add_argument('--priority', default='P2', choices=['P0', 'P1', 'P2', 'P3'], help='默认优先级')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际写入')
    parser.add_argument('--format', choices=['auto', 'list', 'detail'], default='auto', help='输出格式')

    args = parser.parse_args()

    # 收集待办项
    items = []
    if args.output:
        items = extract_items_from_output(args.output)
        if not items:
            print(f"⚠️ 从 {args.output} 中未提取到任何待办项")
            sys.exit(0)
        print(f"📋 从输出文件中提取到 {len(items)} 个待办项:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item['text'][:80]}...")
    elif args.items:
        for text in args.items:
            items.append({"text": text, "emoji": "⚠️", "date": datetime.now().strftime('%Y-%m-%d')})
    else:
        parser.print_help()
        sys.exit(1)

    # 确定格式
    fmt = args.format
    if fmt == "auto":
        fmt = detect_todo_format(Path(TODO_PATH).read_text() if Path(TODO_PATH).exists() else "")

    date_str = datetime.now().strftime('%Y-%m-%d')

    print(f"\n📝 目标文件: {TODO_PATH}")
    print(f"📐 格式: {fmt}")
    print(f"🔢 待办项数量: {len(items)}")
    print(f"🏷️ 来源: {args.source}")
    print(f"⚡ Dry-run: {args.dry_run}")
    print()

    if fmt in ["list", "unknown"]:
        created = write_todo_list_format(items, args.source, args.dry_run)
    else:
        created = write_todo_detail_format(items, args.source, date_str, args.dry_run)

    print(f"\n✅ 共处理 {len(created)} 个待办项")
    if args.dry_run:
        print("⚠️ Dry-run 模式，未实际写入文件")


if __name__ == '__main__':
    main()
