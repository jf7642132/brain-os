#!/usr/bin/env python3
"""
Chronicle → Kanban 自动同步

功能：
1. 扫描最新的史官（Chronicle Agent）输出报告
2. 从"未解决"表格提取待办事项
3. 自动创建 Kanban 卡片（含结构化 body / 来源追溯）
4. 更新 todo-backlog.md（含 Kanban 卡片 ID）
5. 使用 tracker 文件去重，避免重复创建

用法：
    # 标准模式：扫描最新报告并创建卡片
    python chronicle-to-kanban.py
    
    # 指定历史文件
    python chronicle-to-kanban.py --file 2026-05-19-10.md
    
    # 预览模式（不创建卡片）
    python chronicle-to-kanban.py --dry-run
    
    # 全量重扫（强制重新处理所有文件）
    python chronicle-to-kanban.py --full-rescan
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
import os
from pathlib import Path
from collections import defaultdict

# ── 路径配置 ──────────────────────────────────────────────────
KNOWLEDGE = Path(os.environ.get("HERMES_KNOWLEDGE", Path.home() / ".hermes" / "knowledge"))
CHANNEL_HISTORY_DIR = KNOWLEDGE / "09-personal-ops" / "05-channel-history"
CHANNEL_HISTORY_LEGACY_DIR = KNOWLEDGE / "09-personal-ops" / "05-频道历史"
TODO_PATH = KNOWLEDGE / "06-context" / "todo-tracking" / "todo-backlog.md"
TRACKER_PATH = KNOWLEDGE / "99-system" / "trackers" / "chronicle-tracker.md"

# Kanban 配置
KANBAN_ASSIGNEE = "dingtalk-worker"
KANBAN_WORKSPACE = f"dir:{KNOWLEDGE}"

# ── 函数 ──────────────────────────────────────────────────────


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_sorted_report_files() -> list[Path]:
    """获取排序后的所有史官报告文件（最新在前）"""
    files = []
    if CHANNEL_HISTORY_DIR.exists():
        files.extend(sorted(CHANNEL_HISTORY_DIR.glob("*.md"), reverse=True))
    if CHANNEL_HISTORY_LEGACY_DIR.exists():
        for f in sorted(CHANNEL_HISTORY_LEGACY_DIR.glob("*.md"), reverse=True):
            if f not in files:
                files.append(f)
    return files


def parse_unsolved_table(content: str) -> list[dict]:
    """
    从史官报告的"未解决"表格段落中提取待办。

    表格格式（来自史官报告）:
        | 分类 | 内容 | 状态 | 来源 |
        |------|------|------|------|
        | ops | 示例待办事项 | 待执行 | 系统运维 |

    返回:
        [{category, content_text, status, source, source_section}]
    """
    todos = []
    lines = content.split("\n")

    in_unsolved = False
    headers_seen = False
    col_index = {}  # 表头列名 → 列索引

    for line in lines:
        s = line.strip()

        # 进入"未解决"段
        if s.startswith("## 未解决") or s.startswith("## 待办"):
            in_unsolved = True
            headers_seen = False
            col_index = {}
            continue

        # 离开了"未解决"段（进入下一个 ## 标题）
        if in_unsolved and s.startswith("## ") and not s.startswith("## 未解决") and not s.startswith("## 待办"):
            in_unsolved = False
            continue

        # 跳过非表格行
        if not in_unsolved:
            continue
        if not s.startswith("|"):
            continue
        if "--" in s:  # |---| 分隔行
            continue

        # 解析表头
        parts = [p.strip() for p in s.split("|")[1:-1]]
        if not headers_seen:
            # 第一行数据行 → 识别表头
            mapping = {}
            for i, h in enumerate(parts):
                h = h.lower()
                if "分类" in h or "类别" in h:
                    mapping["category"] = i
                elif "内容" in h or "问题" in h or "任务" in h or "描述" in h:
                    mapping["content"] = i
                elif "状态" in h:
                    mapping["status"] = i
                elif "来源" in h:
                    mapping["source"] = i
            if mapping:
                headers_seen = True
                col_index = mapping
            continue

        # 如果是表头行（内容很短，基本都是列名），跳过
        if len(parts) >= 3 and all(len(p) < 10 for p in parts[:3]):
            continue

        # 数据行
        def safe_get(col_name: str) -> str:
            idx = col_index.get(col_name)
            if idx is not None and idx < len(parts):
                return parts[idx].strip()
            return ""

        content_text = safe_get("content")
        if not content_text or len(content_text) < 8:
            continue  # 空行过滤

        todos.append({
            "category": safe_get("category") or "general",
            "content_text": content_text,
            "status": safe_get("status") or "待执行",
            "source": safe_get("source") or "史官记录",
        })

    return todos


def parse_list_items(content: str) -> list[dict]:
    """
    备选解析：当表格格式不可用时，从"未解决"段落的列表项中提取。
    
    列表格式:
        - 关注USTR 301关税复审进展，评估对美出口成本影响
        - 关注USMCA供应链溯源审查，准备溯源数据
    """
    todos = []
    lines = content.split("\n")
    in_unsolved = False

    for line in lines:
        s = line.strip()
        if s.startswith("## 未解决") or s.startswith("## 待办"):
            in_unsolved = True
            continue
        if in_unsolved and s.startswith("## "):
            in_unsolved = False
            continue
        if not in_unsolved:
            continue

        # 列表项
        if s.startswith("- ") or s.startswith("* "):
            text = s[2:].strip()
            if len(text) >= 10 and len(text) <= 300:
                todos.append({
                    "category": classify_text(text),
                    "content_text": text,
                    "status": "待执行",
                    "source": "史官记录",
                })

    return todos


def classify_text(text: str) -> str:
    """简单分类"""
    t = text.lower()
    if any(k in t for k in ["关税", "贸易", "制裁", "合规", "政策", "法规"]):
        return "policy"
    if any(k in t for k in ["erp", "系统", "部署", "服务器", "线上", "上线"]):
        return "ops"
    if any(k in t for k in ["bug", "错误", "修复", "fix", "异常"]):
        return "bug"
    if any(k in t for k in ["开发", "功能", "实现", "feature"]):
        return "feature"
    if any(k in t for k in ["调研", "研究", "评估", "分析"]):
        return "research"
    return "general"


def read_tracker() -> set[str]:
    """读取已处理的待办指纹（去重用）。返回指纹集合。"""
    if not TRACKER_PATH.exists():
        return set()
    content = TRACKER_PATH.read_text(encoding="utf-8")
    fingerprints = set()
    for line in content.split("\n"):
        line = line.strip()
        if line and line.startswith("- `"):
            # 格式: - `fingerprint|kanban_id|...`
            fp = line.split("`")[1]
            fingerprints.add(fp)
    return fingerprints


def make_fingerprint(todo: dict) -> str:
    """对待办内容生成唯一指纹（前 80 字符 + 来源）"""
    text = todo["content_text"].strip()[:80]
    source = todo["source"].strip()[:30]
    return f"{text}||{source}"


def append_tracker(new_entries: list[tuple[str, str, str]]):
    """向 tracker 追加新记录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines_to_add = []
    for fingerprint, kanban_id, todo_text in new_entries:
        lines_to_add.append(f"- `{fingerprint}` → `{kanban_id}` ({todo_text[:60]})")

    new_section = f"\n## {timestamp}\n"
    if TRACKER_PATH.exists():
        content = TRACKER_PATH.read_text(encoding="utf-8")
        # 在当前时间前插入
        lines = content.split("\n")
        insert_pos = len(lines)
        for i, line in enumerate(lines):
            if "## " in line:
                insert_pos = i
        # 插入在第一个 ## 后面（即已有的最新条目之前）
        new_content = "\n".join(lines[:insert_pos]) + "\n" + new_section + "\n".join(lines_to_add) + "\n" + "\n".join(lines[insert_pos:])
        TRACKER_PATH.write_text(new_content, encoding="utf-8")
    else:
        # 创建新 tracker
        content = f"""# Chronicle Agent 待办 → Kanban 追踪器

> 自动记录史官待办向 Kanban 同步的历史。
> 每次执行 chronicle-to-kanban.py 时自动更新。

---

{new_section}
"""
        TRACKER_PATH.write_text(content, encoding="utf-8")


def record_sync_history(file_path: Path, todo_count: int, kanban_ids: list[str]):
    """在 tracker 中记录本次同步"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    ids_str = ", ".join(kanban_ids)
    line = f"- {timestamp} | {file_path.name} | {todo_count} 项 | Kanban: {ids_str}\n"
    
    if TRACKER_PATH.exists():
        content = TRACKER_PATH.read_text(encoding="utf-8")
        content += line
        TRACKER_PATH.write_text(content, encoding="utf-8")
    else:
        content = f"# Chronicle Agent 待办 → Kanban 追踪器\n\n{line}"
        TRACKER_PATH.write_text(content, encoding="utf-8")


def create_kanban(title: str, body: str, priority: int = 2,
                  assignee: str = KANBAN_ASSIGNEE, dry_run: bool = False) -> str | None:
    """调用 hermes kanban create 创建卡片"""
    if dry_run:
        log(f"  [DRY RUN] 创建卡片: {title}")
        return f"dry-run-{hash(title) % 100000:05d}"

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
        log(f"❌ 创建卡片失败: {result.stderr[:300]}")
        return None

    try:
        data = json.loads(result.stdout)
        return data.get("id")
    except json.JSONDecodeError:
        log(f"⚠️ 解析输出失败: {result.stdout[:300]}")
        return None


def update_todo_backlog(todos: list[dict], kanban_ids: list[str], dry_run: bool = False):
    """更新 todo-backlog.md"""
    if not TODO_PATH.exists():
        log(f"⚠️ todo-backlog.md 不存在: {TODO_PATH}")
        return False

    content = TODO_PATH.read_text(encoding="utf-8")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.now().strftime("%Y-%m-%d")

    # 构建新行
    new_rows = []
    for i, (t, kanban_id) in enumerate(zip(todos, kanban_ids)):
        desc = t["content_text"][:60]
        source = t["source"]
        new_rows.append(
            f"| auto-{today}-{i+1:03d} | 史官({t.get('source_file', 'auto')}) | {desc} | open | {kanban_id} | {today} | {now} | 自动 | - |"
        )

    if not new_rows:
        return False

    # 找到高优先级表格的末尾并插入
    lines = content.split("\n")
    new_lines = []
    in_high = False
    after_separator = False
    inserted = False
    for line in lines:
        new_lines.append(line)
        if "## 高优先级" in line:
            in_high = True
            after_separator = False
            continue
        if in_high and not inserted:
            # 找到表头分隔行（|---|---|---|）
            if "---" in line and "|" in line:
                after_separator = True
                continue
            # 分隔行后的第一行数据之后插入新行
            if after_separator:
                # 在现有数据行之前插入新行
                if line.strip().startswith("|"):
                    for nr in new_rows:
                        new_lines.append(nr)
                    new_lines.append(line)
                    inserted = True
                    in_high = False
                    continue
                else:
                    # 没有现有数据，直接插入
                    for nr in new_rows:
                        new_lines.append(nr)
                    inserted = True
                    in_high = False

    if not inserted:
        # fallback: 追加到文件末尾
        new_lines.append("\n## 高优先级 （自动追加）\n")
        new_lines.append("\n| ID | 来源 | 问题描述 | 状态 | Kanban 卡片 | 创建时间 | 最后更新 | 处理方式 | 完成时间 |\n")
        new_lines.append("|----|------|----------|------|-------------|----------|----------|----------|----------|\n")
        for nr in new_rows:
            new_lines.append(nr + "\n")

    TODO_PATH.write_text("\n".join(new_lines), encoding="utf-8")
    log(f"✅ todo-backlog.md 已更新，追加 {len(new_rows)} 行")
    return True


def scan_and_sync(specific_file: str | None = None, dry_run: bool = False, full_rescan: bool = False):
    """主流程：扫描史官报告 → 提取待办 → 创建 Kanban 卡片 → 更新 todo"""
    log("=" * 60)
    log("Chronicle → Kanban 自动同步")
    log(f"模式: {'DRY RUN' if dry_run else 'LIVE'}")
    log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log("=" * 60)

    # 1. 获取文件列表
    if specific_file:
        # 检查两个目录
        files = list(Path(".").glob(specific_file))
        if not files:
            files = list(CHANNEL_HISTORY_DIR.glob(specific_file))
        if not files:
            files = list(CHANNEL_HISTORY_LEGACY_DIR.glob(specific_file))
        if not files:
            log(f"❌ 文件未找到: {specific_file}")
            return
        files = [files[0]]
    else:
        files = get_sorted_report_files()
        if not files:
            log("❌ 未找到史官报告文件")
            return
        # 默认只处理最新的报告（有内容的）
        files = files[:5]
    
    log(f"扫描 {len(files)} 个文件")

    # 2. 读取已处理指纹
    existing_fingerprints = read_tracker() if not full_rescan else set()
    log(f"已有指纹: {len(existing_fingerprints)} 个")

    # 3. 解析每个文件
    all_todos = []
    for filepath in files:
        if not filepath.exists():
            log(f"  跳过（不存在）: {filepath}")
            continue
        content = filepath.read_text(encoding="utf-8")
        
        # 尝试表格解析
        todos = parse_unsolved_table(content)
        if not todos:
            # fallback: 列表解析
            todos = parse_list_items(content)
        
        if todos:
            for t in todos:
                t["source_file"] = filepath.name
            log(f"  {filepath.name}: {len(todos)} 条待办")
            all_todos.extend(todos)
        else:
            log(f"  {filepath.name}: 无待办")

    # 4. 去重
    unique_todos = []
    seen = set()
    for t in all_todos:
        fp = make_fingerprint(t)
        if fp not in seen and (full_rescan or fp not in existing_fingerprints):
            seen.add(fp)
            unique_todos.append(t)

    log(f"\n去重后新增: {len(unique_todos)} 条")
    if not unique_todos:
        log("✅ 无新增待办，跳过")
        return

    # 5. 创建 Kanban 卡片
    log("\n📌 创建 Kanban 卡片...")
    kanban_results = []
    for i, todo in enumerate(unique_todos):
        title = f"[史官] {todo['content_text'][:80]}"
        if len(title) > 120:
            title = title[:117] + "..."

        # 根据分类决定优先级
        category = todo.get("category", "general")
        priority = 2  # 默认 P2
        if category in ("policy", "ops", "bug"):
            priority = 1  # P1
        if "高风险" in todo["content_text"] or "紧急" in todo["content_text"]:
            priority = 1

        body = f"""**来源**: Chronicle Agent 扫描报告
**源文件**: {todo.get('source_file', 'N/A')}
**分类**: {category}
**内容**: {todo['content_text']}
**原始状态**: {todo['status']}
**原始来源**: {todo['source']}

---
*自动创建自 chronicle-to-kanban.py*
*创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"""

        assignee = KANBAN_ASSIGNEE
        # 系统运维相关任务给 default profile
        if "trade" in str(todo.get("source", "")).lower() or "贸易" in todo["content_text"] or "关税" in todo["content_text"]:
            assignee = "knowledge-ops"

        kanban_id = create_kanban(
            title=title,
            body=body,
            priority=priority,
            assignee=assignee,
            dry_run=dry_run,
        )

        if kanban_id:
            kanban_results.append((kanban_id, todo, make_fingerprint(todo)))
            log(f"  ✅ [{i+1}/{len(unique_todos)}] {kanban_id}: {title[:60]}...")
        else:
            log(f"  ❌ [{i+1}/{len(unique_todos)}] 创建失败: {title[:60]}...")

    if not kanban_results:
        log("⚠️ 所有卡片创建失败")
        return

    # 6. 更新 tracker
    if not dry_run:
        log("\n📝 更新 tracker...")
        for kanban_id, todo, fp in kanban_results:
            # append to tracker
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_entry = f"- `{fp}` → `{kanban_id}` ({todo['content_text'][:60]})  [{timestamp}]\n"
            
            if TRACKER_PATH.exists():
                content = TRACKER_PATH.read_text(encoding="utf-8")
                content += new_entry
                TRACKER_PATH.write_text(content, encoding="utf-8")
            else:
                content = f"""# Chronicle Agent 待办 → Kanban 追踪器

> 自动记录史官待办向 Kanban 同步的历史。

---

## {datetime.now().strftime('%Y-%m-%d')}

{new_entry}
"""
                TRACKER_PATH.write_text(content, encoding="utf-8")
        log(f"✅ tracker 已更新: {len(kanban_results)} 条")

        # 7. 更新 todo-backlog.md
        log("\n📋 更新 todo-backlog.md...")
        todos_for_backlog = [kr[1] for kr in kanban_results]
        kanban_ids_for_backlog = [kr[0] for kr in kanban_results]
        update_todo_backlog(todos_for_backlog, kanban_ids_for_backlog)
    else:
        log("\n📝 [DRY RUN] 跳过 tracker 和 todo 更新")

    # 8. 输出摘要
    log("\n" + "=" * 60)
    log("📊 执行摘要")
    log("=" * 60)
    log(f"扫描文件: {len(files)}")
    log(f"原始待办: {len(all_todos)}")
    log(f"新增待办: {len(unique_todos)}")
    log(f"创建卡片: {len(kanban_results)}")
    if not dry_run:
        for kid, todo, _ in kanban_results:
            log(f"  - {kid}: {todo['content_text'][:60]}")
    else:
        log("  [DRY RUN - 未实际创建]")
    if TRACKER_PATH.exists():
        log(f"Tracker: {TRACKER_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Chronicle → Kanban 自动同步")
    parser.add_argument("--file", "-f", help="指定处理单个报告文件")
    parser.add_argument("--dry-run", "-n", action="store_true", help="预览模式，不实际创建卡片")
    parser.add_argument("--full-rescan", action="store_true", help="全量重扫：忽略已有指纹")
    args = parser.parse_args()

    scan_and_sync(
        specific_file=args.file,
        dry_run=args.dry_run,
        full_rescan=args.full_rescan
    )


if __name__ == "__main__":
    sys.exit(main())
