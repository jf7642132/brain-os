#!/usr/bin/env python3
"""
Hermes Agent Backup v3 - Smart backup with exclusions and retry.
Excludes large volatile directories that are easily regenerated.
"""
import os, glob, subprocess, sys
from datetime import datetime

BACKUP_DIR = "/root/hermes-backups"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15
TIMEOUT = 1800  # 30 minutes

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {msg}\n"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True) if LOG_FILE else None
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry.strip())

def run(cmd, timeout=TIMEOUT):
    log(f"Running: {cmd[:200]}...")
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        log(f"Command failed (exit {proc.returncode}): {proc.stderr[:500]}", "WARN")
    return proc

os.makedirs(BACKUP_DIR, exist_ok=True)

log("=" * 60)
log("Hermes Agent Backup Started (Smart Mode)")
log("=" * 60)

# Get source size
rc = run("du -sb /root/.hermes 2>/dev/null | cut -f1", timeout=60)
source_bytes = int(rc.stdout.strip()) if rc.stdout.strip() else 0
log(f"Source size: {source_bytes / (1024*1024):.1f} MB")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"hermes-backup-{timestamp}.tar.gz")

log(f"Backup: {os.path.basename(backup_file)}")

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
log(f"Parallel compression: {'pigz' if use_pigz else 'gzip (single-thread)'}")

start = datetime.now()

if use_pigz:
    cmd = f"tar -cf - -C /root {exclude_str} .hermes | pigz -p $(nproc) > '{backup_file}'"
else:
    cmd = f"tar -czf '{backup_file}' -C /root {exclude_str} .hermes"

rc = run(cmd)
elapsed = (datetime.now() - start).total_seconds()

if rc.returncode != 0 or not os.path.exists(backup_file) or os.path.getsize(backup_file) == 0:
    log("Backup FAILED", "ERROR")
    if os.path.exists(backup_file):
        os.remove(backup_file)
    sys.exit(1)

bsize = os.path.getsize(backup_file)
ratio = (1 - bsize / source_bytes) * 100 if source_bytes > 0 else 0

log(f"Backup created successfully: {os.path.basename(backup_file)}")
log(f"Size: {bsize / (1024*1024):.1f} MB (compression: {ratio:.1f}%)")
log(f"Time: {elapsed:.0f}s")

# Cleanup old backups
log("--- Cleanup ---")
files = glob.glob(os.path.join(BACKUP_DIR, "hermes-backup-*.tar.gz"))
files.sort(key=os.path.getmtime, reverse=True)
log(f"Total backups: {len(files)} (max: {MAX_BACKUPS})")

deleted = 0
freed = 0
if len(files) > MAX_BACKUPS:
    for f in files[MAX_BACKUPS:]:
        sz = os.path.getsize(f)
        os.remove(f)
        deleted += 1
        freed += sz
        log(f"Deleted: {os.path.basename(f)} ({sz / (1024*1024):.1f} MB)")

remaining = glob.glob(os.path.join(BACKUP_DIR, "hermes-backup-*.tar.gz"))
total_sz = sum(os.path.getsize(f) for f in remaining)
if remaining:
    remaining.sort(key=os.path.getmtime, reverse=True)

log(f"Deleted {deleted} backups, freed {freed / (1024*1024):.1f} MB")
log(f"Retained: {len(remaining)} backups, {total_sz / (1024*1024):.1f} MB total")

log("=" * 60)
log("Backup Complete")
log("=" * 60)

# Print summary
print(f"""
BACKUP SUMMARY
{'='*60}
Status: SUCCESS
Backup File: {os.path.basename(backup_file)}
Source Size: {source_bytes / (1024*1024):.1f} MB
Backup Size: {bsize / (1024*1024):.1f} MB
Compression: {ratio:.1f}%
Time: {elapsed:.0f}s
Old Backups Deleted: {deleted} ({freed / (1024*1024):.1f} MB)
Backups Retained: {len(remaining)} ({total_sz / (1024*1024):.1f} MB)
Exclusions: node, checkpoints, state-snapshots, logs, audio_cache, browser_recordings, cache
{'='*60}
""")
