#!/usr/bin/env python3
"""Weekly knowledge base audit — run via cron or on-demand.

Usage:
    python3 kb-audit.py              # Full audit to stdout
    python3 kb-audit.py --json       # JSON output for programmatic use
    python3 kb-audit.py --report     # Write markdown report to kb index

Environment:
    KB = /root/.hermes/knowledge (hardcoded)
"""
import json, re, os, sys
from collections import defaultdict
from datetime import date

KB = "/root/.hermes/knowledge"

def collect_files():
    files = []
    files = []
    for root, dirs, fnames in os.walk(KB):
        if '.git' in dirs:
            dirs.remove('.git')
        for fn in fnames:
            if fn.endswith('.md'):
                rel = os.path.relpath(os.path.join(root, fn), KB)
                if rel.startswith('./'):
                    rel = rel[2:]
                files.append(rel)
    files.sort()
    return files

def build_maps(files):
    basename_map = defaultdict(list)
    title_to_path = {}
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        basename_map[base].append(f)
        title_to_path[os.path.splitext(f)[0]] = f
    return basename_map, title_to_path

def check_frontmatter(files):
    no_fm = []
    broken = []
    valid = 0
    for f in files:
        fp = os.path.join(KB, f)
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read(5000)
        except:
            no_fm.append((f, "unreadable"))
            continue
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            no_fm.append((f, "no_yaml"))
            continue
        end_idx = None
        for i in range(1, min(len(lines), 60)):
            if lines[i].strip() == '---':
                end_idx = i
                break
        if end_idx is None:
            broken.append((f, "no_closing"))
            continue
        yaml_block = lines[1:end_idx]
        if not any(': ' in line for line in yaml_block) and any(l.strip() for l in yaml_block):
            broken.append((f, "yaml_empty"))
            continue
        valid += 1
    return valid, no_fm, broken

def check_links(files, title_to_path, basename_map):
    obsidian_links = defaultdict(list)
    obsidian_broken = defaultdict(list)
    md_links = defaultdict(list)

    for f in files:
        fp = os.path.join(KB, f)
        try:
            with open(fp, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except:
            continue
        # Obsidian [[wikilink]]
        for link in re.findall(r'\[\[([^\]]+?)(?:\|[^\]]*)?\]\]', content):
            target = link.strip()
            obsidian_links[f].append(target)
            found = False
            for c in [target, target + '.md']:
                if c in title_to_path:
                    found = True; break
                if os.path.splitext(os.path.basename(c))[0] in basename_map:
                    found = True; break
            if not found:
                obsidian_broken[f].append(target)
        # Markdown relative links
        for text, url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content):
            if url.endswith('.md') and not url.startswith('http') and not url.startswith('#'):
                resolved = os.path.normpath(os.path.join(os.path.dirname(f), url))
                if resolved not in files:
                    md_links[f].append((text, url, resolved))
    return obsidian_links, obsidian_broken, md_links

def find_orphans(files, obsidian_links, title_to_path, basename_map):
    inbound_graph = defaultdict(set)
    for src, targets in obsidian_links.items():
        for tgt in targets:
            found_path = None
            if tgt in title_to_path:
                found_path = title_to_path[tgt]
            else:
                base = os.path.splitext(os.path.basename(tgt))[0]
                if base in basename_map:
                    found_path = basename_map[base][0]
            if found_path and found_path != src:
                inbound_graph[found_path].add(src)

    exempt_patterns = [
        r'/index\.md$', r'/README\.md$',
        r'/00-收件箱/',
        r'/05-系统配置/提示词/',
        r'/05-系统配置/模板/',
        r'/05-系统配置/SCHEMA\.md$', r'/05-系统配置/log\.md$',
        r'/01-项目/02-红果短剧改编/.*/script/',
        r'/01-项目/02-红果短剧改编/.*/original/',
        r'/01-项目/02-红果短剧改编/.*/assistant_configs/',
        r'/03-个人运营/05-频道历史/',
        r'/04-知识库/99-系统/03-(整合|集成)报告/',
        r'/04-知识库/99-系统/01-索引/',
        r'/04-知识库/01-阅读消化/04-摘要汇总/',
        r'/04-知识库/03-整合报告/',
        r'/99-系统/',
        r'/08-归档/',
        r'/05-系统配置/observer/',
    ]
    orphans = []
    for f in files:
        if any(re.search(p, f) for p in exempt_patterns):
            continue
        if f in inbound_graph and len(inbound_graph[f]) > 0:
            continue
        orphans.append(f)
    return orphans

def find_dupes(files):
    base_dupes = defaultdict(list)
    for f in files:
        base = os.path.splitext(os.path.basename(f))[0]
        base_dupes[base].append(f)
    return {k: v for k, v in base_dupes.items() if len(v) > 1}

def run_audit():
    files = collect_files()
    total = len(files)
    basename_map, title_to_path = build_maps(files)
    valid_fm, no_fm, broken_fm = check_frontmatter(files)
    obsidian_links, obsidian_broken, md_broken = check_links(files, title_to_path, basename_map)
    orphans = find_orphans(files, obsidian_links, title_to_path, basename_map)
    dupes = find_dupes(files)

    # File sizes
    small = []
    large = []
    for f in files:
        try:
            sz = os.path.getsize(os.path.join(KB, f))
            if sz < 50: small.append((f, sz))
            elif sz > 500 * 1024: large.append((f, sz // 1024))
        except: pass

    return {
        "date": date.today().isoformat(),
        "total_files": total,
        "valid_frontmatter": valid_fm,
        "missing_frontmatter": len(no_fm),
        "broken_frontmatter": len(broken_fm),
        "missing_frontmatter_categories": dict(
            (k, len(v)) for k, v in
            sorted(defaultdict(list, {f.split('/')[0]: no_fm for f, _ in no_fm}).items())
        ),
        "broken_wikilinks_total": sum(len(v) for v in obsidian_broken.values()),
        "broken_wikilinks": {k: v for k, v in sorted(obsidian_broken.items()) if v},
        "broken_md_links_total": sum(len(v) for v in md_broken.values()),
        "broken_md_links": {k: [(t, u) for t, u, r in v] for k, v in sorted(md_broken.items()) if v},
        "orphan_notes": len(orphans),
        "orphan_notes_by_category": dict(
            (k, len(v)) for k, v in
            sorted(defaultdict(list, {f.split('/')[0]: f for f in orphans}).items())
        ),
        "small_files": [(f, s) for f, s in small],
        "large_files": [(f, s) for f, s in large],
        "duplicate_basenames": len(dupes),
    }

if __name__ == '__main__':
    result = run_audit()
    if '--json' in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif '--report' in sys.argv:
        path = os.path.join(KB, "04-知识库/99-系统/01-索引",f"weekly-audit-{date.today().isoformat()}.md")
        lines = [
            f"# 知识库周度审计报告 — {date.today().isoformat()}",
            "",
            f"**Markdown 文件总数**: {result['total_files']}",
            "",
            "## 摘要",
            "| 问题类型 | 数量 |",
            "|----------|:----:|",
            f"| 有效 YAML 前置元数据 | {result['valid_frontmatter']} |",
            f"| 缺失 YAML | {result['missing_frontmatter']} |",
            f"| 断链 (wikilinks) | {result['broken_wikilinks_total']} |",
            f"| 断链 (相对路径) | {result['broken_md_links_total']} |",
            f"| 孤儿笔记 | {result['orphan_notes']} |",
            f"| 重复文件名 | {result['duplicate_basenames']} |",
        ]
        with open(path, 'w') as fh:
            fh.write('\n'.join(lines))
        print(f"Report written to {path}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))