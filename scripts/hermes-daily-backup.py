#!/usr/bin/env python3
"""
Hermes Daily Backup - Fast pigz + tar pipeline with integrity check and rotation.
Excludes large/regenerable dirs. Keeps 15 most recent backups.
Handles all naming conventions found in the backup directory.
"""
import os, glob, subprocess, sys, re
from datetime import datetime

BACKUP_DIR = "/root/hermes-backups"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15
TIMEOUT = 1800  # 30 minutes

# All backup files matching any hermes naming convention
BACKUP_GLOB_PATTERNS = [
    "hermes_backup_*.tar.gz",
    "hermes-backup_*.tar.gz",
    "hermes-backup-*.tar.gz",
    "hermes_backup_*.zip",
]

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry.strip())

def run(cmd, timeout=TIMEOUT):
    log(f"Running: {cmd[:200]}...")
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        log(f"Command failed (exit {proc.returncode}): {proc.stderr[:500]}", "WARN")
    return proc

def collect_all_backups():
    """Collect all backup files across all naming conventions."""
    all_files = []
    for pattern in BACKUP_GLOB_PATTERNS:
        all_files.extend(glob.glob(os.path.join(BACKUP_DIR, pattern)))
    # Deduplicate and sort by mtime (newest first)
    all_files = sorted(set(all_files), key=os.path.getmtime, reverse=True)
    return all_files

# --- Start ---
os.makedirs(BACKUP_DIR, exist_ok=True)

log("=" * 60)
log("Hermes Daily Backup Started")
log("=" * 60)

# Get source size (best effort, don't block on timeout)
source_bytes = 0
rc = run("du -sb /root/.hermes 2>/dev/null | cut -f1", timeout=120)
if rc.stdout and rc.stdout.strip():
    try:
        source_bytes = int(rc.stdout.strip())
    except (ValueError, TypeError):
        pass
if source_bytes > 0:
    log(f"Source size: {source_bytes / (1024*1024):.1f} MB")
else:
    log("Source size: N/A (size check timed out or failed, proceeding anyway)")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_filename = f"hermes_backup_{timestamp}.tar.gz"
backup_file = os.path.join(BACKUP_DIR, backup_filename)

log(f"Backup file: {backup_filename}")

# Exclude large easily-regenerated dirs
excludes = [
    "--exclude=.hermes/node",
    "--exclude=.hermes/checkpoints",
    "--exclude=.hermes/state-snapshots",
    "--exclude=.hermes/logs",
    "--exclude=.hermes/audio_cache",
    "--exclude=.hermes/browser_recordings",
    "--exclude=.hermes/cache",
    "--exclude=.hermes/venvs",
    "--exclude=*.tmp",
    "--exclude=*.log",
    "--exclude=__pycache__",
    "--exclude=.git",
    "--exclude=node_modules",
]
exclude_str = " ".join(excludes)

# Check for pigz
rc_pigz = run("which pigz 2>/dev/null", timeout=10)
use_pigz = bool(rc_pigz.stdout.strip())
log(f"Compression: {'pigz (parallel)' if use_pigz else 'gzip (single-thread)'}")

start = datetime.now()

if use_pigz:
    cmd = f"tar -cf - -C /root {exclude_str} .hermes | pigz -p $(nproc) > '{backup_file}'"
else:
    cmd = f"tar -czf '{backup_file}' -C /root {exclude_str} .hermes"

rc_bkp = run(cmd)
elapsed = (datetime.now() - start).total_seconds()

# Check backup file
if not os.path.exists(backup_file) or os.path.getsize(backup_file) == 0:
    log("Backup file creation FAILED - file missing or empty", "ERROR")
    if os.path.exists(backup_file):
        os.remove(backup_file)
    sys.exit(1)

bsize = os.path.getsize(backup_file)

# Integrity check
log("Verifying backup integrity...")
rc_verify = run(f"gzip -t '{backup_file}'", timeout=30)
if rc_verify.returncode != 0:
    log("Integrity check FAILED - backup is corrupted", "ERROR")
    os.remove(backup_file)
    sys.exit(1)
log("Integrity check: PASSED")

if source_bytes > 0 and bsize > 0:
    ratio = (1 - bsize / source_bytes) * 100
else:
    ratio = 0.0
log(f"Backup created: {backup_filename}")
log(f"Size: {bsize / (1024*1024):.1f} MB (compression: {ratio:.1f}%)")
log(f"Time: {elapsed:.0f}s")

# --- Cleanup old backups ---
log("--- Cleanup ---")
all_backups = collect_all_backups()
log(f"Total backups found: {len(all_backups)} (max to {MAX_BACKUPS})")

deleted = 0
freed = 0
if len(all_backups) > MAX_BACKUPS:
    for f in all_backups[MAX_BACKUPS:]:
        sz = os.path.getsize(f)
        try:
            os.remove(f)
            deleted += 1
            freed += sz
            log(f"Deleted: {os.path.basename(f)} ({sz / (1024*1024):.1f} MB)")
        except OSError as e:
            log(f"Failed to delete {os.path.basename(f)}: {e}", "WARN")

remaining = collect_all_backups()
total_sz = sum(os.path.getsize(f) for f in remaining)

log(f"Deleted: {deleted}, freed {freed / (1024*1024):.1f} MB")
log(f"Retained: {len(remaining)} backups, {total_sz / (1024*1024):.1f} MB total")

log("=" * 60)
log("Backup Complete")
log("=" * 60)

# Print final summary
print(f"""
{'='*60}
BACKUP SUMMARY
{'='*60}
Status:     SUCCESS
File:       {backup_filename}
Source:     {source_bytes / (1024*1024):.1f} MB
Backup:     {bsize / (1024*1024):.1f} MB
Compress:   {ratio:.1f}%
Duration:   {elapsed:.0f}s
Integrity:  PASSED
Deleted:    {deleted} backups ({freed / (1024*1024):.1f} MB)
Retained:   {len(remaining)} backups ({total_sz / (1024*1024):.1f} MB)
Log:        {LOG_FILE}
{'='*60}
""")