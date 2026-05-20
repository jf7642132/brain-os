#!/usr/bin/env python3
import os
import sys
from pathlib import Path

if len(sys.argv) < 3:
    print('Usage: render-writer-package.py YYYY-MM-DD OUTPUT_DIR', file=sys.stderr)
    sys.exit(1)

date = sys.argv[1]
outdir = Path(sys.argv[2])
outdir.mkdir(parents=True, exist_ok=True)

notes = sorted(outdir.glob(f'conversation-flywheel-{date}-note-*.md'))
suggestions = outdir / f'conversation-flywheel-{date}-daily-learning-suggestions.md'
package = outdir / f'conversation-flywheel-{date}-writer-package.md'

parts = [f'# Writer Package — {date}', '', '## 写入目标', '', '### 1. Knowledge notes']
for note in notes:
    parts.append(f'- `{note.name}`')
parts += ['', '### 2. Daily suggestions', f'- `{suggestions.name}`', '', '## 写入要求', '', '- 保留 frontmatter', '- 保持 transcript source 路径', '- 写完必须 git commit', '- 以 Obsidian 可见为完成标准', '', '## 本次写入内容', '']
for note in notes:
    parts += [f'---\n## {note.name}\n', note.read_text(encoding='utf-8').strip(), '']
if suggestions.exists():
    parts += [f'---\n## {suggestions.name}\n', suggestions.read_text(encoding='utf-8').strip(), '']
package.write_text('\n'.join(parts), encoding='utf-8')
print(package)
