#!/usr/bin/env python3
"""
从史官记录中提取待办事项

从 Chronicle Agent 生成的史官记录文件中提取待办事项，写入 todo-backlog.md。

触发条件：
- 史官记录文件包含"未解决"或"决策"部分
- 用户要求"提取史官记录中的待办"
- 作为 Brain OS P2 阶段任务运行

输出：
- todo-backlog.md (待办列表)
- dialogue-mining-tracker.md (提取日志)

分类体系：bug | config | deploy | docs | feature | general | meeting | ops | research | test
状态体系：待执行 | 待确认 | 进行中 | 阻塞 | 已解决
"""

import re
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 配置
KNOWLEDGE_DIR = Path("<KNOWLEDGE_DIR>")
CHRONICLE_DIR = KNOWLEDGE_DIR / "03-个人运营" / "05-频道历史"
TODO_BACKLOG = KNOWLEDGE_DIR / "04-知识库" / "01-阅读消化" / "04-摘要汇总" / "todo-backlog.md"
TRACKER_FILE = KNOWLEDGE_DIR / "04-知识库" / "01-阅读消化" / "04-摘要汇总" / "dialogue-mining-tracker.md"

# 分类关键词
CATEGORY_KEYWORDS = {
    'bug': ['bug', '错误', '故障', '异常', '修复', 'fix', 'error'],
    'config': ['配置', 'config', '设置', 'setting', '参数'],
    'deploy': ['部署', 'deploy', '发布', '上线', 'release'],
    'docs': ['文档', 'docs', '文档化', '写文档', 'document'],
    'feature': ['功能', 'feature', '新特性', '开发', 'implement'],
    'general': ['一般', 'general', '其他', 'misc'],
    'meeting': ['会议', 'meeting', '讨论', 'sync', '对齐'],
    'ops': ['运维', 'ops', '监控', '维护', 'monitor', '运维'],
    'research': ['研究', 'research', '调研', '分析', 'investigate'],
    'test': ['测试', 'test', '验证', 'check', 'verify'],
}

# 状态关键词
STATUS_KEYWORDS = {
    '待执行': ['需要', '应该', '必须', 'todo', '待办', 'todo:', 'TODO'],
    '待确认': ['确认', '确认一下', 'verify', 'check if', '待确认'],
    '进行中': ['进行中', 'in progress', 'doing', '正在'],
    '阻塞': ['阻塞', 'blocked', '卡住', '等待', 'pending'],
    '已解决': ['完成', 'done', '已解决', 'fixed', 'resolved'],
}

# 行动关键词（用于识别待办）
ACTION_KEYWORDS = [
    '需要', '应该', '必须', '要', '应该要', '需要完成', '需要修复',
    'todo', 'TODO', '待办', '待完成', '待处理',
    '创建', '部署', '生成', '修复', '更新', '优化', '调整',
    '实现', '开发', '编写', '设计', '调研', '分析',
]


def classify_category(text):
    """根据文本内容分类"""
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return 'general'


def classify_status(text):
    """根据文本内容判断状态"""
    text_lower = text.lower()
    for status, keywords in STATUS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return status
    return '待执行'


def extract_todos_from_file(filepath):
    """从史官记录文件中提取待办事项"""
    todos = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取"未解决"部分
    unresovled_match = re.search(r'## 未解决\s*\n(.*?)(?=## |$)', content, re.DOTALL)
    if unresovled_match:
        unresovled_text = unresovled_match.group(1)
        # 按行分割，提取有效待办
        for line in unresovled_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('- [ ]'):
                # 检查是否包含行动关键词
                if any(kw in line for kw in ACTION_KEYWORDS):
                    todos.append({
                        'content': line,
                        'category': classify_category(line),
                        'status': classify_status(line),
                        'source': filepath.name,
                        'section': '未解决',
                    })
    
    # 提取"决策"部分
    decision_match = re.search(r'## 决策\s*\n(.*?)(?=## |$)', content, re.DOTALL)
    if decision_match:
        decision_text = decision_match.group(1)
        for line in decision_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('- [ ]'):
                if any(kw in line for kw in ACTION_KEYWORDS):
                    todos.append({
                        'content': line,
                        'category': classify_category(line),
                        'status': classify_status(line),
                        'source': filepath.name,
                        'section': '决策',
                    })
    
    return todos


def deduplicate_todos(todos):
    """去重待办事项"""
    seen = set()
    unique_todos = []
    for todo in todos:
        # 使用内容前50字符作为去重键
        key = todo['content'][:50].strip()
        if key and key not in seen:
            seen.add(key)
            unique_todos.append(todo)
    return unique_todos


def write_todo_backlog(todos):
    """写入 todo-backlog.md"""
    # 确保目录存在
    TODO_BACKLOG.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成内容
    lines = [
        "# Todo Backlog",
        "",
        f"**最后更新**: {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 待办列表",
        "",
    ]
    
    # 按分类分组
    by_category = {}
    for todo in todos:
        cat = todo['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(todo)
    
    for category in ['bug', 'config', 'deploy', 'docs', 'feature', 'ops', 'research', 'test', 'meeting', 'general']:
        if category in by_category:
            lines.append(f"### {category}")
            lines.append("")
            for todo in by_category[category]:
                status_icon = {
                    '待执行': '⏳',
                    '待确认': '❓',
                    '进行中': '🔄',
                    '阻塞': '🚫',
                    '已解决': '✅',
                }.get(todo['status'], '⏳')
                lines.append(f"- {status_icon} [{todo['status']}] {todo['content']}")
                lines.append(f"  - 来源: {todo['source']} ({todo['section']})")
            lines.append("")
    
    with open(TODO_BACKLOG, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return len(todos)


def write_tracker(entries):
    """写入提取日志"""
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        "# Dialogue Mining Tracker",
        "",
        f"**最后更新**: {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 提取记录",
        "",
    ]
    
    for entry in entries:
        lines.append(f"- **{entry['time']}**: 从 `{entry['file']}` 提取 {entry['count']} 个待办")
    
    with open(TRACKER_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def main():
    """主函数"""
    now = datetime.now(timezone(timedelta(hours=8)))
    
    # 查找最近的史官记录文件
    chronicle_files = sorted(CHRONICLE_DIR.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not chronicle_files:
        print("未找到史官记录文件")
        return 0
    
    # 提取待办
    all_todos = []
    entries = []
    
    for filepath in chronicle_files[:5]:  # 最多处理5个文件
        todos = extract_todos_from_file(filepath)
        if todos:
            all_todos.extend(todos)
            entries.append({
                'time': now.strftime('%Y-%m-%d %H:%M'),
                'file': filepath.name,
                'count': len(todos),
            })
            print(f"从 {filepath.name} 提取 {len(todos)} 个待办")
    
    # 去重
    unique_todos = deduplicate_todos(all_todos)
    print(f"\n去重后: {len(unique_todos)} 个待办")
    
    if unique_todos:
        # 写入 todo-backlog
        count = write_todo_backlog(unique_todos)
        print(f"已写入 {count} 个待办到 todo-backlog.md")
        
        # 写入 tracker
        write_tracker(entries)
        print(f"已更新 dialogue-mining-tracker.md")
    
    return len(unique_todos)


if __name__ == '__main__':
    sys.exit(main())
