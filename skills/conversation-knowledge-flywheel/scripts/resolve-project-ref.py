#!/usr/bin/env python3
"""
Resolve a project name / alias to a stable project_ref and brief path.

Usage:
    resolve-project-ref.py <project-name>
    resolve-project-ref.py --list

Reads Brain-side 05-PROJECTS/*/project-brief.md frontmatter to build
an alias → project_ref mapping dynamically.

Exit codes:
    0  match found, prints JSON: {"project_ref": "...", "brief_path": "..."}
    1  no match found, prints JSON: {"project_ref": null, "brief_path": null}
    2  usage error
"""
import json
import os
import re
import sys
from pathlib import Path

BRAIN_ROOT = Path(os.environ.get("BRAIN_ROOT", "{{BRAIN_PATH}}"))
PROJECTS_DIR = BRAIN_ROOT / "05-PROJECTS"


def parse_frontmatter(text: str) -> dict:
    """Extract YAML frontmatter fields we care about (project_ref, aliases)."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end]
    result = {}
    # project_ref: value
    m = re.search(r"^project_ref:\s*(.+)$", fm, re.MULTILINE)
    if m:
        result["project_ref"] = m.group(1).strip()
    # aliases as YAML list
    aliases = []
    in_aliases = False
    for line in fm.splitlines():
        if re.match(r"^aliases\s*:", line):
            in_aliases = True
            continue
        if in_aliases:
            item = re.match(r"^\s+-\s+(.+)$", line)
            if item:
                aliases.append(item.group(1).strip())
            elif line and not line.startswith(" "):
                in_aliases = False
    result["aliases"] = aliases
    return result


def build_mapping() -> dict[str, tuple[str, Path]]:
    """Return {alias_lower: (project_ref, brief_path)} for all projects."""
    mapping: dict[str, tuple[str, Path]] = {}
    if not PROJECTS_DIR.is_dir():
        return mapping
    for brief in PROJECTS_DIR.glob("*/project-brief.md"):
        fm = parse_frontmatter(brief.read_text(encoding="utf-8"))
        ref = fm.get("project_ref")
        if not ref:
            continue
        # The directory name itself is a valid alias
        slug = brief.parent.name
        for alias in [slug, ref] + fm.get("aliases", []):
            mapping[alias.lower()] = (ref, brief)
    return mapping


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve-project-ref.py <project-name> | --list", file=sys.stderr)
        sys.exit(2)

    mapping = build_mapping()

    if sys.argv[1] == "--list":
        seen = set()
        for alias, (ref, brief) in sorted(mapping.items()):
            if ref not in seen:
                print(json.dumps({"project_ref": ref, "brief_path": str(brief)}, ensure_ascii=False))
                seen.add(ref)
        return

    query = sys.argv[1].lower()
    if query in mapping:
        ref, brief = mapping[query]
        print(json.dumps({"project_ref": ref, "brief_path": str(brief)}, ensure_ascii=False))
        sys.exit(0)
    else:
        print(json.dumps({"project_ref": None, "brief_path": None}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
