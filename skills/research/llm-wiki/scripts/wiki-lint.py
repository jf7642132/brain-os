#!/usr/bin/env python3
"""
Wiki Lint Script - Automated health check for LLM Wiki knowledge bases.

Usage:
    python wiki-lint.py [WIKI_PATH] [--save]

If WIKI_PATH is not provided, uses $WIKI_PATH env var or defaults to ~/wiki.
--save saves the report to 99-system/lint-reports/lint-report-YYYY-MM-DD.md
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def scan_wiki(wiki_path: str) -> dict:
    """Scan wiki directory and collect all markdown files."""
    all_files = {}
    
    for root, dirs, files in os.walk(wiki_path):
        # Skip .git and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, wiki_path)
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    all_files[rel_path] = {
                        'content': content,
                        'path': full_path,
                        'lines': content.count('\n') + 1,
                        'chars': len(content)
                    }
                except Exception as e:
                    print(f"  Warning: Could not read {rel_path}: {e}", file=sys.stderr)
    
    return all_files


def check_frontmatter(all_files: dict, skip_patterns: list) -> list:
    """Check for missing YAML frontmatter."""
    missing = []
    fm_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    
    for rel_path, info in all_files.items():
        if any(s in rel_path for s in skip_patterns):
            continue
        if not fm_pattern.match(info['content']):
            missing.append(rel_path)
    
    return missing


def check_broken_links(all_files: dict) -> tuple:
    """Check for broken wikilinks and build inbound link map."""
    wikilink_pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^]]+)?\]\]')
    broken_links = []
    inbound_links = defaultdict(int)
    
    for rel_path, info in all_files.items():
        links = wikilink_pattern.findall(info['content'])
        for link in links:
            target = link.strip()
            # Skip external links
            if target.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            
            # Try to find matching file
            found = False
            target_lower = target.lower()
            for existing in all_files.keys():
                existing_lower = existing.lower()
                # Fuzzy match: target in path or path ends with target
                if target_lower in existing_lower or existing_lower.endswith(target_lower):
                    inbound_links[existing] += 1
                    found = True
                    break
            
            if not found:
                broken_links.append({'file': rel_path, 'link': target})
    
    return broken_links, inbound_links


def find_orphan_pages(all_files: dict, inbound_links: dict, skip_patterns: list) -> list:
    """Find pages with no inbound links."""
    wiki_pages = [
        p for p in all_files.keys() 
        if not any(s in p for s in skip_patterns)
    ]
    linked_files = set(inbound_links.keys())
    orphans = [p for p in wiki_pages if p not in linked_files]
    return orphans


def find_large_pages(all_files: dict, threshold: int = 200) -> list:
    """Find pages exceeding line threshold."""
    large = []
    for rel_path, info in all_files.items():
        if info['lines'] > threshold:
            large.append({
                'file': rel_path,
                'lines': info['lines'],
                'chars': info['chars']
            })
    large.sort(key=lambda x: x['lines'], reverse=True)
    return large


def generate_report(wiki_path: str, stats: dict, issues: dict) -> str:
    """Generate markdown lint report."""
    report = f"""# Wiki Lint Report

> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> Wiki Path: `{wiki_path}`

---

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {stats['total_files']} |
| Total Lines | {stats['total_lines']:,} |
| Total Characters | {stats['total_chars']:,} |
| Missing Frontmatter | {issues['missing_fm_count']} |
| Broken Links | {issues['broken_links_count']} |
| Orphan Pages | {issues['orphan_count']} |
| Large Pages (>200 lines) | {issues['large_count']} |

---

## Issues

### 1. Missing Frontmatter ({issues['missing_fm_count']} files)

"""
    
    if issues['missing_fm']:
        report += "Files without YAML frontmatter:\n\n"
        for f in issues['missing_fm'][:20]:
            report += f"- `{f}`\n"
        if len(issues['missing_fm']) > 20:
            report += f"\n... and {len(issues['missing_fm']) - 20} more\n"
    else:
        report += "✅ All files have frontmatter.\n"
    
    report += f"""
### 2. Broken Links ({issues['broken_links_count']} links)

"""
    
    if issues['broken_links']:
        report += "Wikilinks pointing to non-existent files:\n\n"
        for item in issues['broken_links'][:15]:
            report += f"- `{item['file']}` → `[[{item['link']}]]`\n"
        if len(issues['broken_links']) > 15:
            report += f"\n... and {len(issues['broken_links']) - 15} more\n"
    else:
        report += "✅ No broken links found.\n"
    
    report += f"""
### 3. Orphan Pages ({issues['orphan_count']} pages)

Pages with no inbound wikilinks:\n\n"""
    
    if issues['orphans']:
        for p in issues['orphans'][:20]:
            report += f"- `{p}`\n"
        if len(issues['orphans']) > 20:
            report += f"\n... and {len(issues['orphans']) - 20} more\n"
    else:
        report += "✅ All pages have inbound links.\n"
    
    report += f"""
### 4. Large Pages ({issues['large_count']} pages >200 lines)

Pages exceeding 200 lines (candidates for splitting):\n\n"""
    
    if issues['large_pages']:
        report += "| File | Lines | Characters |\n|------|-------|------------|\n"
        for item in issues['large_pages'][:10]:
            report += f"| `{item['file']}` | {item['lines']} | {item['chars']:,} |\n"
        if len(issues['large_pages']) > 10:
            report += f"\n... and {len(issues['large_pages']) - 10} more\n"
    else:
        report += "✅ No pages exceed 200 lines.\n"
    
    report += """
---

## Recommendations

### Priority 0 (Immediate)
1. Fix broken links in index.md and other navigation files
2. Add frontmatter to core files (index.md, SCHEMA.md, log.md)

### Priority 1 (This Week)
3. Add frontmatter to important business pages
4. Add inbound links to orphaned important pages

### Priority 2 (Long-term)
5. Split pages exceeding 500 lines
6. Establish naming conventions
7. Run lint weekly to catch issues early

---

*Generated by wiki-lint.py*
"""
    
    return report


def main():
    # Determine wiki path
    if len(sys.argv) > 1:
        wiki_path = sys.argv[1]
    else:
        wiki_path = os.environ.get('WIKI_PATH', os.path.expanduser('~/wiki'))
    
    # Normalize path
    wiki_path = os.path.abspath(os.path.expanduser(wiki_path))
    
    if not os.path.isdir(wiki_path):
        print(f"Error: Wiki path not found: {wiki_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning wiki at: {wiki_path}", file=sys.stderr)
    
    # Skip patterns for system/template files
    skip_patterns = [
        'README.md', 'TEMPLATE', '.git/', 'lint-reports/', 
        'cron/', '提示词/', 'node_modules/', '.obsidian/'
    ]
    
    # Run checks
    print("  Scanning files...", file=sys.stderr)
    all_files = scan_wiki(wiki_path)
    
    print(f"  Found {len(all_files)} markdown files", file=sys.stderr)
    
    print("  Checking frontmatter...", file=sys.stderr)
    missing_fm = check_frontmatter(all_files, skip_patterns)
    
    print("  Checking broken links...", file=sys.stderr)
    broken_links, inbound_links = check_broken_links(all_files)
    
    print("  Finding orphan pages...", file=sys.stderr)
    orphans = find_orphan_pages(all_files, inbound_links, skip_patterns)
    
    print("  Finding large pages...", file=sys.stderr)
    large_pages = find_large_pages(all_files)
    
    # Compile results
    stats = {
        'total_files': len(all_files),
        'total_lines': sum(f['lines'] for f in all_files.values()),
        'total_chars': sum(f['chars'] for f in all_files.values()),
    }
    
    issues = {
        'missing_fm': missing_fm,
        'missing_fm_count': len(missing_fm),
        'broken_links': broken_links,
        'broken_links_count': len(broken_links),
        'orphans': orphans,
        'orphan_count': len(orphans),
        'large_pages': large_pages,
        'large_count': len(large_pages),
    }
    
    # Generate report
    report = generate_report(wiki_path, stats, issues)
    
    # Output
    print(report)
    
    # Save to file if requested
    if len(sys.argv) > 2 and sys.argv[2] == '--save':
        reports_dir = os.path.join(wiki_path, '99-系统', 'lint-reports')
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, f'lint-report-{datetime.now().strftime("%Y-%m-%d")}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}", file=sys.stderr)


if __name__ == '__main__':
    main()