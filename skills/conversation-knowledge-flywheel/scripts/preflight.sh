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

TRANSCRIPT_OK=0
QMD_OK=0

if [[ -d "$DAY_DIR" ]]; then
  TRANSCRIPT_OK=1
fi

if "$QMD_HEALTHCHECK" >/dev/null 2>&1; then
  QMD_OK=1
fi

cat <<EOF
transcript_root=$TRANSCRIPT_ROOT
transcript_day=$DAY_DIR
transcript_ok=$TRANSCRIPT_OK
qmd_ok=$QMD_OK
EOF

if [[ "$TRANSCRIPT_OK" -eq 1 && "$QMD_OK" -eq 1 ]]; then
  exit 0
fi
exit 2
