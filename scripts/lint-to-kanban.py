#!/usr/bin/env python3
"""
知识库 Lint → Kanban 闭环集成脚本

功能：
1. 运行 Lint 检查，生成报告
2. 将 P0/P1 问题自动创建为 Kanban 卡片
3. 更新问题追踪器
4. 发送通知

用法：
    python lint-to-kanban.py --wiki <KNOWLEDGE_DIR>
    python lint-to-kanban.py --wiki <KNOWLEDGE_DIR> --dry-run
    python lint-to-kanban.py --wiki <KNOWLEDGE_DIR> --fix broken-links
"""

import argparse
import json
import os
import os
import re
from pathlib import Path
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict


# 配置
WIKI_PATH = os.environ.get("HERMES_KNOWLEDGE", str(Path.home() / ".hermes" / "knowledge"))
REPORTS_DIR = f"{WIKI_PATH}/99-系统/lint-reports"
TRACKER_FILE = f"{REPORTS_DIR}/issues-tracker.md"
LINT_SCRIPT = os.environ.get("HERMES_LINT_SCRIPT", "")  # 用户自定义 lint 脚本

# Kanban 配置
KANBAN_ASSIGNEE = "knowledge-ops"  # 知识库运维角色
KANBAN_WORKSPACE = f"dir:{WIKI_PATH}"  # 使用知识库目录作为工作区

# 优先级映射 (数字，越小优先级越高)
PRIORITY_MAP = {
    "P0": 1,
    "P1": 2,
    "P2": 3
}


def run_lint(wiki_path: str) -> dict:
    """运行 Lint 检查"""
    report_path = f"{REPORTS_DIR}/lint-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    
    cmd = [
        "python3", LINT_SCRIPT,
        wiki_path, "--save",
        report_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ Lint 执行失败: {result.stderr}")
        return None
    
    return {"report_path": report_path, "status": "success"}


def parse_lint_report(report_path: str) -> list:
    """解析 lint 报告，提取问题列表"""
    if not Path(report_path).exists():
        return []
    
    content = Path(report_path).read_text(encoding='utf-8')
    issues = []
    today = datetime.now().strftime('%Y%m%d')
    
    # 从 Summary 表格提取问题统计
    fm_match = re.search(r'Missing Frontmatter \| (\d+)', content)
    bl_match = re.search(r'Broken Links \| (\d+)', content)
    or_match = re.search(r'Orphan Pages \| (\d+)', content)
    sz_match = re.search(r'Large Pages.*\| (\d+)', content)
    
    if fm_match:
        count = int(fm_match.group(1))
        issues.append({
            "id": f"FM-{today}-001",
            "title": f"缺失 YAML frontmatter ({count} 个文件)",
            "type": "frontmatter",
            "count": count,
            "severity": "P0",
            "suggestion": "优先为 index.md、核心导航文件、项目文档添加 frontmatter"
        })
    
    if bl_match:
        count = int(bl_match.group(1))
        issues.append({
            "id": f"BL-{today}-001",
            "title": f"断链 ({count} 个)",
            "type": "broken-link",
            "count": count,
            "severity": "P0",
            "suggestion": "修复 wikilinks 指向不存在的文件，统一命名规范"
        })
    
    if or_match:
        count = int(or_match.group(1))
        issues.append({
            "id": f"OR-{today}-001",
            "title": f"孤立页面 ({count} 个)",
            "type": "orphan",
            "count": count,
            "severity": "P1",
            "suggestion": "为重要页面添加入站链接，在 index.md 中添加索引"
        })
    
    if sz_match:
        count = int(sz_match.group(1))
        issues.append({
            "id": f"SIZE-{today}-001",
            "title": f"超大页面 (>200行, {count} 个)",
            "type": "page-size",
            "count": count,
            "severity": "P2",
            "suggestion": "拆分大页面或添加摘要索引"
        })
    
    return issues


def get_existing_tracker_issues() -> dict:
    """读取现有的问题追踪器"""
    if not Path(TRACKER_FILE).exists():
        return {}
    
    content = Path(TRACKER_FILE).read_text(encoding='utf-8')
    issues = {}
    
    # 解析现有问题
    table_pattern = r'\| ([A-Z]+-\d+) \| (.+?) \| (\w+) \| (\d{4}-\d{2}-\d{2}) \| (\w+) \| (.+?) \|'
    
    for match in re.finditer(table_pattern, content):
        issues[match.group(1)] = {
            "title": match.group(2).strip(),
            "type": match.group(3),
            "date": match.group(4),
            "status": match.group(5),
            "suggestion": match.group(6).strip()
        }
    
    return issues


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
        print(f"⚠️ 创建卡片失败: {result.stderr}")
        return None
    
    try:
        data = json.loads(result.stdout)
        return data.get("id")  # 实际字段名是 "id" 而不是 "task_id"
    except json.JSONDecodeError:
        print(f"⚠️ 解析输出失败: {result.stdout}")
        return None


def sync_issues_to_kanban(new_issues: list, existing_issues: dict, dry_run: bool = False) -> dict:
    """同步问题到 Kanban"""
    results = {
        "created": [],
        "updated": [],
        "skipped": []
    }
    
    for issue in new_issues:
        issue_id = issue["id"]
        
        # 检查是否已存在
        if issue_id in existing_issues:
            existing = existing_issues[issue_id]
            
            # 状态变化处理
            if existing.get("status") == "open" and issue.get("status") == "resolved":
                # 问题已修复，创建完成卡片
                body = f"✅ 问题已修复\n\n**问题**: {issue['title']}\n**类型**: {issue['type']}\n**修复建议**: {issue['suggestion']}\n\n---\n*自动同步自 lint 报告*"
                task_id = create_kanban_task(
                    f"完成: {issue['title']}",
                    body,
                    priority=PRIORITY_MAP.get(issue.get("severity", "P1"), 2),
                    dry_run=dry_run
                )
                if task_id:
                    results["updated"].append({"id": issue_id, "task_id": task_id, "action": "resolved"})
            
            elif existing.get("status") == "open" and issue.get("status", "open") == "open":
                # 问题仍存在，跳过
                results["skipped"].append({"id": issue_id, "reason": "already_exists"})
            
            continue
        
        # 新问题，创建卡片
        # 根据 severity 确定优先级
        severity = issue.get("severity", "P1")
        priority = PRIORITY_MAP.get(severity, 2)
        
        body = f"""🔴 新问题发现

**问题**: {issue['title']}
**类型**: {issue['type']}
**数量**: {issue.get('count', 'N/A')}
**严重程度**: {severity}
**修复建议**: {issue['suggestion']}

---
*自动同步自 lint 报告*
*下次 lint 执行时将更新状态*
"""
        
        task_id = create_kanban_task(
            f"[Lint] {issue['title']}",
            body,
            priority=priority,
            dry_run=dry_run
        )
        
        if task_id:
            results["created"].append({"id": issue_id, "task_id": task_id})
    
    return results


def update_tracker(new_issues: list, kanban_results: dict) -> None:
    """更新问题追踪器"""
    # 读取现有内容
    if Path(TRACKER_FILE).exists():
        content = Path(TRACKER_FILE).read_text(encoding='utf-8')
    else:
        content = f"""---
title: 知识库问题追踪
type: tracker
tags: [lint, issues, tracking]
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
---

# 知识库问题追踪器

> 自动追踪 lint 发现的问题，记录修复状态，防止问题被遗忘。

---

## 修复状态说明

| 状态 | 说明 |
|------|------|
| 🔴 open | 新问题，尚未开始修复 |
| 🟡 in_progress | 正在修复中 |
| 🟢 resolved | 已修复，待验证 |
| ⚪ wontfix | 确认不修复（需说明原因） |

---

## 当前未解决问题

> 下次 lint 执行时会自动对比此列表，更新状态。

### 🔴 P0 - 立即修复

| ID | 问题 | 类型 | 发现日期 | 状态 | 修复建议 | Kanban 卡片 |
|----|------|------|----------|------|----------|-------------|

### 🔴 P1 - 本周内

| ID | 问题 | 类型 | 发现日期 | 状态 | 修复建议 | Kanban 卡片 |
|----|------|------|----------|------|----------|-------------|

### 🟡 P2 - 长期优化

| ID | 问题 | 类型 | 发现日期 | 状态 | 修复建议 | Kanban 卡片 |
|----|------|------|----------|------|----------|-------------|

---

## Lint 执行历史

| 日期 | 总问题 | 新增 | 修复 | 未修复 | Kanban 卡片 | 报告 |
|------|--------|------|------|--------|-------------|------|
"""
    
    # 更新执行历史
    today = datetime.now().strftime('%Y-%m-%d')
    history_line = f"| {today} | {len(new_issues)} | {len(kanban_results['created'])} | {len(kanban_results['updated'])} | {len(kanban_results['skipped'])} | {len(kanban_results['created'])} | [lint-report-{today}.md](./lint-report-{today}.md) |\n"
    
    # 在历史表末尾添加
    content = re.sub(
        r'(\| 日期 \|.*?\n\|------\|.*?\n)(.*?\n)*$',
        rf'\1{history_line}',
        content
    )
    
    Path(TRACKER_FILE).write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Lint → Kanban 闭环集成')
    parser.add_argument('--wiki', default=WIKI_PATH, help='知识库路径')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际创建卡片')
    parser.add_argument('--fix', choices=['broken-links', 'frontmatter', 'all'], help='自动修复类型')
    args = parser.parse_args()
    
    print(f"=== Lint → Kanban 闭环 ===")
    print(f"知识库: {args.wiki}")
    print(f"模式: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()
    
    # 1. 运行 Lint
    print("📊 步骤 1: 运行 Lint 检查...")
    lint_result = run_lint(args.wiki)
    if not lint_result:
        print("❌ Lint 执行失败")
        sys.exit(1)
    print(f"✅ 报告已生成: {lint_result['report_path']}")
    
    # 2. 解析报告
    print("\n📋 步骤 2: 解析报告...")
    new_issues = parse_lint_report(lint_result['report_path'])
    print(f"   发现问题: {len(new_issues)} 个")
    
    # 3. 读取现有追踪器
    print("\n📝 步骤 3: 读取现有追踪器...")
    existing_issues = get_existing_tracker_issues()
    print(f"   已有问题: {len(existing_issues)} 个")
    
    # 4. 同步到 Kanban
    print("\n📌 步骤 4: 同步到 Kanban...")
    kanban_results = sync_issues_to_kanban(new_issues, existing_issues, args.dry_run)
    print(f"   新建卡片: {len(kanban_results['created'])} 个")
    print(f"   更新卡片: {len(kanban_results['updated'])} 个")
    print(f"   跳过: {len(kanban_results['skipped'])} 个")
    
    # 5. 更新追踪器
    print("\n📝 步骤 5: 更新追踪器...")
    update_tracker(new_issues, kanban_results)
    print(f"✅ 追踪器已更新: {TRACKER_FILE}")
    
    # 6. 输出摘要
    print("\n" + "="*50)
    print("📊 执行摘要")
    print("="*50)
    print(f"Lint 报告: {lint_result['report_path']}")
    print(f"发现问题: {len(new_issues)} 个")
    print(f"新建 Kanban 卡片: {len(kanban_results['created'])} 个")
    
    if kanban_results['created']:
        print("\n🆕 新建卡片:")
        for item in kanban_results['created']:
            print(f"   - [{item['id']}] {item['task_id']}")
    
    if args.dry_run:
        print("\n⚠️ 这是 DRY RUN，没有实际创建卡片")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
