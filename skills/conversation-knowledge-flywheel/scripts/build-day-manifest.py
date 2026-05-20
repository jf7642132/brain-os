#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(os.environ.get('TRANSCRIPT_ROOT', '/Volumes/LIZEYU/Converstions'))


def infer_project(stem: str) -> str:
    parts = stem.split('_')
    if len(parts) >= 2:
        return parts[1]
    return 'unknown'


def infer_agent(stem: str) -> str:
    parts = stem.split('_')
    if parts:
        return parts[0]
    return 'unknown'


def infer_title(stem: str) -> str:
    parts = stem.split('_')
    if len(parts) >= 3:
        return '_'.join(parts[2:]).strip()
    return stem


def main():
    if len(sys.argv) < 2:
        print('Usage: build-day-manifest.py YYYY-MM-DD', file=sys.stderr)
        sys.exit(1)

    date = sys.argv[1]
    day_dir = ROOT / date
    if not day_dir.is_dir():
        print(f'No transcript directory for date: {date}', file=sys.stderr)
        sys.exit(2)

    files = sorted([p for p in day_dir.iterdir() if p.is_file() and p.suffix.lower() in {'.md', '.markdown'}])
    items = []
    for path in files:
        stem = path.stem
        item = {
            'date': date,
            'path': str(path),
            'filename': path.name,
            'agent': infer_agent(stem),
            'project': infer_project(stem),
            'title_hint': infer_title(stem),
            'size_bytes': path.stat().st_size,
            'modified_at': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        }
        items.append(item)

    manifest = {
        'date': date,
        'root': str(day_dir),
        'count': len(items),
        'projects': sorted({item['project'] for item in items}),
        'items': items,
    }

    out = Path(os.environ.get('OUTPUT_ROOT', '/tmp')) / f'conversation-flywheel-{date}-manifest.json'
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(out))


if __name__ == '__main__':
    main()
