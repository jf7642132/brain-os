#!/usr/bin/env bash
# Shared configuration for conversation-knowledge-flywheel scripts.
# Source this file at the top of each script:
#   source "$(dirname "$0")/config.sh"

TRANSCRIPT_ROOT="${TRANSCRIPT_ROOT:-/Volumes/LIZEYU/Converstions}"
BRAIN_ROOT="${BRAIN_ROOT:-/tmp/brain-os-test/vault}"
OUTPUT_ROOT="${OUTPUT_ROOT:-/tmp}"
SCRIPT_DIR_REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QMD_BIN_REAL="${QMD_BIN_REAL:-qmd}"
QMD_BIN="${QMD_BIN:-$SCRIPT_DIR_REAL/qmd-safe.sh}"
QMD_HEALTHCHECK="${QMD_HEALTHCHECK:-$SCRIPT_DIR_REAL/qmd-healthcheck.sh}"
