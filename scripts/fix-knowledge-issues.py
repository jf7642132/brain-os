#!/usr/bin/env python3
"""
知识库问题自动修复脚本

修复类型:
1. 断链修复 - 尝试自动匹配可能的正确文件名
2. Frontmatter 添加 - 为缺失 frontmatter 的文件添加基础元数据

用法:
    python fix-knowledge-issues.py --wiki <KNOWLEDGE_DIR> --fix broken-links
    python fix-knowledge-issues.py --wiki <KNOWLEDGE_DIR> --fix frontmatter
    python fix-knowledge-issues.py --wiki <KNOWLEDGE_DIR> --fix all
"""

import argparse
import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def find_files(wiki_path: str, pattern: str = "*.md") -> list:
    """查找所有 markdown 文件"""
    return list(Path(wiki_path).glob(f"**/{pattern}"))


def extract_wikilinks(content: str) -> list:
    """提取内容中的所有 wikilinks"""
    return re.findall(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]', content)


def find_possible_match(wiki_path: str, link_text: str) -> str | None:
    """尝试找到链接指向的可能文件"""
    # 直接匹配
    for f in find_files(wiki_path):
        if f.stem == link_text or f.name == link_text:
            return str(f.relative_to(wiki_path))
    
    # 模糊匹配（忽略大小写、空格、特殊字符）
    normalized = re.sub(r'[-_\s]+', '', link_text.lower())
    for f in find_files(wiki_path):
        stem_normalized = re.sub(r'[-_\s]+', '', f.stem.lower())
        if normalized in stem_normalized or stem_normalized in normalized:
            return str(f.relative_to(wiki_path))
    
    return None


def fix_broken_links(wiki_path: str, report_path: str = None) -> dict:
    """修复断链"""
    results = {
        'total_links': 0,
        'broken_links': 0,
        'fixed_links': 0,
        'details': []
    }
    
    all_files = find_files(wiki_path)
    file_map = {f.stem: f for f in all_files}
    
    for file_path in all_files:
        content = file_path.read_text(encoding='utf-8')
        links = extract_wikilinks(content)
        results['total_links'] += len(links)
        
        modified = False
        new_content = content
        
        for link_text, display_text in links:
            # 检查链接是否存在
            target_path = Path(wiki_path) / (link_text + '.md')
            if not target_path.exists():
                results['broken_links'] += 1
                
                # 尝试找到可能的匹配
                possible = find_possible_match(wiki_path, link_text)
                if possible:
                    # 替换链接
                    old_link = f'[[{link_text}]]'
                    new_link = f'[[{possible}]]'
                    if display_text:
                        old_link = f'[[{link_text}|{display_text}]]'
                        new_link = f'[[{possible}|{display_text}]]'
                    
                    new_content = new_content.replace(old_link, new_link)
                    results['fixed_links'] += 1
                    results['details'].append({
                        'file': str(file_path.relative_to(wiki_path)),
                        'original': link_text,
                        'fixed_to': possible
                    })
                    modified = True
        
        if modified:
            file_path.write_text(new_content, encoding='utf-8')
    
    # 保存报告
    if report_path:
        report = f"""# 断链修复报告

> 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 修复结果

| 指标 | 数值 |
|------|------|
| 总链接数 | {results['total_links']} |
| 断链数 | {results['broken_links']} |
| 已修复 | {results['fixed_links']} |
| 未修复 | {results['broken_links'] - results['fixed_links']} |

## 修复详情

"""
        for d in results['details']:
            report += f"- `{d['file']}`: `{d['original']}` → `{d['fixed_to']}`\n"
        
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(report, encoding='utf-8')
    
    return results


def add_frontmatter(wiki_path: str, files_pattern: str = None, dry_run: bool = False) -> dict:
    """为文件添加 frontmatter"""
    results = {
        'total_files': 0,
        'missing_fm': 0,
        'added_fm': 0,
        'details': []
    }
    
    if files_pattern:
        files = list(Path(wiki_path).glob(files_pattern))
    else:
        files = find_files(wiki_path)
    
    results['total_files'] = len(files)
    
    for file_path in files:
        content = file_path.read_text(encoding='utf-8')
        
        # 检查是否已有 frontmatter
        if content.startswith('---'):
            continue
        
        results['missing_fm'] += 1
        
        # 生成 frontmatter
        rel_path = str(file_path.relative_to(wiki_path))
        title = file_path.stem.replace('-', ' ').replace('_', ' ').title()
        
        # 根据路径推断 type
        if '01-项目' in rel_path:
            ftype = 'project'
        elif '04-知识库' in rel_path or '03-个人运营' in rel_path:
            ftype = 'concept'
        elif '02-工作产出' in rel_path:
            ftype = 'summary'
        else:
            ftype = 'note'
        
        # 推断 tags
        tags = []
        if False:  # 保留空判断，移除特定领域过滤
            tags.append('chemical-trade')
        if False:  # 保留空判断
            tags.append('short-drama')
        if 'lint' in rel_path or 'audit' in rel_path:
            tags.append('system')
        
        fm = f"""---
title: {title}
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
type: {ftype}
tags: {json.dumps(tags)}
---

"""
        
        if not dry_run:
            new_content = fm + content
            file_path.write_text(new_content, encoding='utf-8')
        
        results['added_fm'] += 1
        results['details'].append({
            'file': rel_path,
            'title': title,
            'type': ftype
        })
    
    return results


def main():
    parser = argparse.ArgumentParser(description='知识库问题自动修复')
    parser.add_argument('--wiki', required=True, help='知识库路径')
    parser.add_argument('--fix', choices=['broken-links', 'frontmatter', 'all'], 
                        default='all', help='修复类型')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际修改')
    parser.add_argument('--report-dir', default=None, help='报告输出目录')
    
    args = parser.parse_args()
    
    report_dir = args.report_dir or f"{args.wiki}/99-系统/lint-reports"
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    print(f"=== 知识库问题修复 ===")
    print(f"知识库: {args.wiki}")
    print(f"修复类型: {args.fix}")
    print(f"Dry run: {args.dry_run}")
    print()
    
    if args.fix in ['broken-links', 'all']:
        print("🔗 修复断链...")
        results = fix_broken_links(
            args.wiki, 
            report_path=f"{report_dir}/broken-links-fix-{date_str}.md"
        )
        print(f"   总链接: {results['total_links']}")
        print(f"   断链: {results['broken_links']}")
        print(f"   已修复: {results['fixed_links']}")
        print()
    
    if args.fix in ['frontmatter', 'all']:
        print("📝 添加 frontmatter...")
        results = add_frontmatter(args.wiki, dry_run=args.dry_run)
        print(f"   总文件: {results['total_files']}")
        print(f"   缺失 frontmatter: {results['missing_fm']}")
        print(f"   已添加: {results['added_fm']}")
        if args.dry_run:
            print("   (dry run - 未实际修改)")
        print()
    
    print("✅ 修复完成")


if __name__ == '__main__':
    main()
