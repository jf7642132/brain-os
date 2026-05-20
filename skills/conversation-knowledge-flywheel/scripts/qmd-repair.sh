#!/usr/bin/env bash
set -euo pipefail

QMD_DIR="${QMD_DIR:-/opt/homebrew/lib/node_modules/@tobilu/qmd}"
cd "$QMD_DIR"

echo "[repair] pwd=$PWD"
echo "[repair] node=$(node -v)"
echo "[repair] rebuilding better-sqlite3 for current node ABI..."

npm rebuild better-sqlite3 --foreground-scripts

echo "[repair] done"
