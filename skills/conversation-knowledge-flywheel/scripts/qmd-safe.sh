#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QMD_BIN_REAL="${QMD_BIN_REAL:-qmd}"
export QMD_BIN_REAL
HEALTH="$SCRIPT_DIR/qmd-healthcheck.sh"
REPAIR="$SCRIPT_DIR/qmd-repair.sh"

status="$($HEALTH 2>/tmp/qmd-health.err || true)"

if [[ "$status" == "healthy" ]]; then
  exec "$QMD_BIN_REAL" "$@"
fi

if [[ "$status" == "broken:abi-mismatch" ]]; then
  echo "[qmd-safe] detected ABI mismatch, attempting repair..." >&2
  "$REPAIR" >&2
  status2="$($HEALTH 2>/tmp/qmd-health.err || true)"
  if [[ "$status2" == "healthy" ]]; then
    echo "[qmd-safe] repair succeeded" >&2
    exec "$QMD_BIN_REAL" "$@"
  fi
  echo "[qmd-safe] repair failed: $status2" >&2
  exit 21
fi

echo "[qmd-safe] unhealthy: $status" >&2
exit 22
