#!/usr/bin/env python3
"""Cleanup old hermes backups - keep 15 most recent, delete rest."""
import os, glob
from datetime import datetime

BACKUP_DIR = "/root/hermes-backups"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15

def log_msg(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())

# Get all tar.gz files sorted by modification time (newest first)
files = glob.glob(os.path.join(BACKUP_DIR, "*.tar.gz"))
# Filter out test files
files = [f for f in files if "test" not in os.path.basename(f)]
files.sort(key=os.path.getmtime, reverse=True)

log_msg(f"Total backup files found: {len(files)}")
log_msg(f"Keeping: {MAX_BACKUPS}")

if len(files) <= MAX_BACKUPS:
    log_msg("No cleanup needed")
else:
    to_delete = files[MAX_BACKUPS:]
    freed = 0
    for f in to_delete:
        sz = os.path.getsize(f)
        os.remove(f)
        freed += sz
        log_msg(f"Deleted: {os.path.basename(f)} ({sz / (1024*1024):.1f} MB)")
    log_msg(f"Deleted {len(to_delete)} backups, freed {freed / (1024*1024):.1f} MB")

# Final count
remaining = glob.glob(os.path.join(BACKUP_DIR, "*.tar.gz"))
remaining = [f for f in remaining if "test" not in os.path.basename(f)]
total_sz = sum(os.path.getsize(f) for f in remaining)
print(f"\nRemaining backups: {len(remaining)}")
print(f"Total backup size: {total_sz / (1024*1024):.1f} MB")
print("Newest:", os.path.basename(remaining[0]) if remaining else "N/A")
print("Oldest:", os.path.basename(remaining[-1]) if remaining else "N/A")
