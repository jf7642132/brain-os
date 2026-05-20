#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 YYYY-MM-DD" >&2
  exit 1
fi

DATE="$1"
DAY_DIR="$TRANSCRIPT_ROOT/$DATE"

if [[ ! -d "$DAY_DIR" ]]; then
  echo "No transcript directory for date: $DATE" >&2
  exit 2
fi

find "$DAY_DIR" -maxdepth 1 -type f \( -name '*.md' -o -name '*.markdown' \) | sort
