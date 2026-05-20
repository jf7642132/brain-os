#!/usr/bin/env python3
"""从史官记录中提取高质量待办事项（从"未解决"和"决策"部分）"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

KNOWLEDGE_ROOT = Path("/root/.hermes/knowledge")
TRANSCRIPTS_DIR = KNOWLEDGE_ROOT / "00-raw" / "transcripts" / "频道历史"
TODO_FILE = KNOWLEDGE_ROOT / "06-context" / "待办跟进" / "todo-backlog.md"
TRACKER_FILE = KNOWLEDGE_ROOT / "99-system" / "trackers" / "dialogue-mining-tracker.md"

# 状态关键词
STATUS_MAP = {
    "已解决": ["解决", "完成", "搞定", "OK", "ok", "已修复", "已更新", "已同步", "已备份", "已迁移", "已重构", "已清理", "成功"],
    "进行中": ["进行中", "正在", "尝试", "研究", "探索", "开发", "实现中"],
    "阻塞": ["阻塞", "卡住", "无法", "不能", "失败", "报错", "错误", "问题", "困难", "需要帮助", "等待"],
    "待确认": ["确认", "验证", "测试", "检查", "核实", "待定", "需要确认"],
}

# 分类关键词
CATEGORY_KEYWORDS = {
    "bug": ["bug", "错误", "报错", "修复", "fix", "异常", "崩溃", "失败"],
    "feature": ["feature", "功能", "新增", "添加", "实现", "开发", "支持"],
    "refactor": ["refactor", "重构", "优化", "改进", "性能", "清理", "整理"],
    "docs": ["docs", "文档", "说明", "注释", "README"],
    "test": ["test", "测试", "验证", "检查", "确认"],
    "config": ["config", "配置", "设置", "环境变量", "参数", "调整"],
    "deploy": ["deploy", "部署", "上线", "发布", "迁移", "同步"],
    "research": ["research", "研究", "调研", "学习", "探索", "了解"],
    "meeting": ["meeting", "会议", "讨论", "沟通", "协调"],
    "ops": ["运维", "监控", "日志", "备份", "恢复", "重启"],
}

def is_noise_line(line):
    """判断是否为噪音行"""
    s = line.strip()
    if not s:
        return True
    if s.startswith("# "):
        return True
    if re.match(r"^#{2,6}\s", s):
        return True
    if s.startswith("```"):
        return True
    if s.startswith("|"):
        return True
    if s.startswith(">"):
        return True
    if len(s) < 5:
        return True
    return False

def classify_todo(text):
    text_lower = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return cat
    return "general"

def determine_status(text):
    for status, keywords in STATUS_MAP.items():
        for kw in keywords:
            if kw in text:
                return status
    return "待执行"

def parse_transcript(filepath):
    """从史官记录中提取待办"""
    todos = []
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split("\n")
    current_date = None
    in_unsolved = False
    in_decision = False
    
    for i, line in enumerate(lines):
        s = line.strip()
        
        # 检查日期
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
        if date_match:
            current_date = date_match.group(1)
            continue
        
        # 检测区域
        if "## 未解决" in s or "## 待办" in s or "## 遗留" in s:
            in_unsolved = True
            continue
        if "## 决策" in s:
            in_decision = True
            continue
        if s.startswith("## ") and "未解决" not in s and "决策" not in s:
            in_unsolved = False
            in_decision = False
            continue
        
        # 跳过噪音
        if is_noise_line(line):
            continue
        
        # 从"未解决"部分提取
        if in_unsolved:
            # 列表项
            if s.startswith("- ") or s.startswith("* "):
                text = s[2:].strip()
                if len(text) >= 10 and len(text) <= 200:
                    todos.append({
                        "source_file": filepath.name,
                        "source_date": current_date,
                        "line_num": i + 1,
                        "text": text,
                        "status": "阻塞",  # 未解决的问题默认为阻塞
                        "category": classify_todo(text),
                    })
            # 普通行
            elif len(s) >= 10 and len(s) <= 200 and not s.startswith("#"):
                todos.append({
                    "source_file": filepath.name,
                    "source_date": current_date,
                    "line_num": i + 1,
                    "text": s,
                    "status": "阻塞",
                    "category": classify_todo(s),
                })
        
        # 从"决策"部分提取需要跟进的
        elif in_decision:
            # 编号列表
            match = re.match(r"^(\\d+)\\.\\s*(.+)", s)
            if match:
                text = match.group(2).strip()
                # 检查是否是需要后续跟进的决策
                if any(kw in text for kw in ["等待", "待", "需要", "后续", "之后", "接下来"]):
                    todos.append({
                        "source_file": filepath.name,
                        "source_date": current_date,
                        "line_num": i + 1,
                        "text": text,
                        "status": "待确认",
                        "category": classify_todo(text),
                    })
    
    return todos

def deduplicate_todos(todos):
    """去重"""
    seen = set()
    unique = []
    for t in todos:
        key = t["text"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique

def generate_todo_id(index):
    return f"TODO-20260518-{index:03d}"

def write_to_todo_file(todos):
    """写入 todo-backlog.md"""
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 删除旧的史官记录部分
    lines = content.split("\n")
    new_lines = []
    skip_until_empty = False
    for line in lines:
        if "## 史官记录待办" in line:
            skip_until_empty = True
            continue
        if skip_until_empty:
            if line.strip() == "":
                skip_until_empty = False
                continue
            if not line.startswith("|") and not line.startswith("##"):
                skip_until_empty = False
                new_lines.append(line)
                continue
            continue
        new_lines.append(line)
    
    content = "\n".join(new_lines)
    
    # 准备新内容
    new_section = f"\n## 史官记录待办 ({len(todos)} 条) - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n| ID | 来源任务 | 问题描述 | 状态 | Kanban 卡片 | 创建时间 | 最后更新 | 处理方式 | 完成时间 |\n|----|----------|----------|------|-------------|----------|----------|----------|----------|\n"
    
    for i, t in enumerate(todos):
        new_section += f"| {generate_todo_id(i+1)} | 史官记录({t['source_file']}) | {t['text'][:100]} | {t['status']} | - | 2026-05-18 | 2026-05-18 | 待处理 | - |\n"
    
    # 插入到"## 高优先级"之后
    if "## 高优先级" in content:
        lines = content.split("\n")
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if "## 高优先级" in line and not inserted:
                # 添加表格内容直到空行
                while i + 1 < len(lines) and (lines[i + 1].startswith("|") or lines[i + 1].startswith("||") or lines[i + 1].strip() == ""):
                    i += 1
                    new_lines.append(lines[i])
                new_lines.append("")
                new_lines.append(new_section)
                new_lines.append("")
                inserted = True
        content = "\n".join(new_lines) if inserted else content + new_section
    else:
        content = content.rstrip("\n") + new_section
    
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def update_tracker(count):
    """更新 tracker"""
    tracker_path = TRACKER_FILE
    if not tracker_path.exists():
        return
    
    with open(tracker_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    record = f"- {timestamp}: 史官记录待办提取完成，共 {count} 条新待办\n"
    
    if "## 待办提取记录" not in content:
        content += f"\n\n## 待办提取记录\n\n{record}"
    else:
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if "## 待办提取记录" in line:
                new_lines.append("")
                new_lines.append(record)
                break
        content = "\n".join(new_lines)
    
    with open(tracker_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("=" * 60)
    print("史官记录待办提取（未解决 + 决策）")
    print("=" * 60)
    
    files = sorted(TRANSCRIPTS_DIR.glob("*.md"))
    print(f"发现 {len(files)} 个史官记录文件")
    
    all_todos = []
    for filepath in files:
        todos = parse_transcript(filepath)
        all_todos.extend(todos)
    
    print(f"提取到 {len(all_todos)} 条待办事项")
    
    unique_todos = deduplicate_todos(all_todos)
    print(f"去重后 {len(unique_todos)} 条")
    
    categories = defaultdict(int)
    statuses = defaultdict(int)
    for t in unique_todos:
        categories[t["category"]] += 1
        statuses[t["status"]] += 1
    
    print("\n分类统计:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print("\n状态统计:")
    for status, count in sorted(statuses.items()):
        print(f"  {status}: {count}")
    
    write_to_todo_file(unique_todos)
    update_tracker(len(unique_todos))
    
    print(f"\n✅ 完成")

if __name__ == "__main__":
    sys.exit(main())