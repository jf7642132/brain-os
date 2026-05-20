#!/usr/bin/env bash
set -euo pipefail

QMD_BIN="${QMD_BIN_REAL:-qmd}"

if ! command -v "$QMD_BIN" >/dev/null 2>&1; then
  echo "missing:qmd"
  exit 10
fi

if ! "$QMD_BIN" --version >/dev/null 2>&1; then
  echo "broken:version"
  exit 11
fi

TMP_ERR=$(mktemp)
if "$QMD_BIN" collection list >/dev/null 2>"$TMP_ERR"; then
  rm -f "$TMP_ERR"
  echo "healthy"
  exit 0
fi

if grep -q "better-sqlite3.node was compiled against a different Node.js version" "$TMP_ERR" 2>/dev/null; then
  cat "$TMP_ERR" >&2
  rm -f "$TMP_ERR"
  echo "broken:abi-mismatch"
  exit 21
fi

cat "$TMP_ERR" >&2
rm -f "$TMP_ERR"
echo "broken:collection-list"
exit 22
