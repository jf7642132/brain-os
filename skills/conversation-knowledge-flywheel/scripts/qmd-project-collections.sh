#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 YYYY-MM-DD" >&2
  exit 1
fi

DATE="$1"
MANIFEST="${OUTPUT_ROOT}/conversation-flywheel-${DATE}-manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Manifest not found: $MANIFEST" >&2
  exit 2
fi

# Parse manifest and group by project
python3 - <<'PY' "$MANIFEST"
import json, sys
from collections import defaultdict
manifest_path = sys.argv[1]
with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
projects = defaultdict(list)
for item in data.get('items', []):
    projects[item.get('project') or 'unknown'].append(item['path'])
for project, paths in sorted(projects.items()):
    print(f'PROJECT\t{project}\t{len(paths)}')
    for p in paths:
        print(f'FILE\t{p}')
PY

echo
echo "=== QMD Collection Setup ==="

# Check QMD health before proceeding
if ! "$QMD_HEALTHCHECK" >/dev/null 2>&1; then
  echo "[DEGRADED] qmd unavailable/unhealthy — skipping vector recall layer" >&2
  exit 0
fi

# For each project group, create/refresh a QMD collection and run recall
python3 - <<'PY' "$MANIFEST" "$DATE"
import json, sys, subprocess, os
from collections import defaultdict
from pathlib import Path

manifest_path = sys.argv[1]
date = sys.argv[2]

with open(manifest_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

projects = defaultdict(list)
for item in data.get('items', []):
    projects[item.get('project') or 'unknown'].append(item['path'])

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"[WARN] Command failed: {cmd}", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
    return result

for project, paths in sorted(projects.items()):
    if not paths:
        continue
    collection = f"flywheel-{date}-{project}"
    qmd_bin = os.environ.get('QMD_BIN', 'qmd')

    print(f"\n--- Project: {project} ({len(paths)} files) ---")

    # Use a per-project temporary collection root to avoid one-day shared-directory collisions
    tmp_root = Path(os.environ.get('OUTPUT_ROOT', '/tmp')) / f"qmd-flywheel-{date}-{project}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    import shutil
    for p in paths:
        src = Path(p)
        dst = tmp_root / src.name
        if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
    dir_path = str(tmp_root)

    check = run(f'"{qmd_bin}" collection list 2>/dev/null | grep -q "{collection}"', check=False)
    if check.returncode != 0:
        print(f"  Adding collection: {collection}")
        result = run(f'"{qmd_bin}" collection add "{dir_path}" --name "{collection}"')
        if result.returncode != 0:
            print(f"  [WARN] Could not add collection, skipping embed for {project}", file=sys.stderr)
            continue
    else:
        print(f"  Collection already exists: {collection}")

    # Re-index
    print("  Updating index...")
    run(f'"{qmd_bin}" update -c "{collection}"')

    # Generate embeddings
    print("  Embedding...")
    run(f'"{qmd_bin}" embed -c "{collection}"')

    print(f"  Collection {collection} ready for query.")
PY

echo
echo "=== QMD collections ready. Run queries with: ==="
echo "  $QMD_BIN query \"<your query>\" -c flywheel-${DATE}-<project>"
