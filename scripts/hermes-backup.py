#!/usr/bin/env python3
"""
Hermes Agent Backup Script
Creates a compressed backup of /root/.hermes, keeping max 15 most recent backups.
Excludes large cache directories that can be regenerated.
"""

import os
import tarfile
import gzip
from datetime import datetime
import subprocess

BACKUP_DIR = "/root/hermes-backups"
SOURCE_DIR = "/root/.hermes"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15

# Directories to exclude (large cache/regenerable directories)
EXCLUDE_DIRS = [
    '.hermes/hermes-agent/',      # 3.2 GB - agent runtime cache
    '.hermes/state-snapshots/',   # 1.86 GB - state snapshots
    '.hermes/node/',              # 507 MB - node modules cache
    '.hermes/checkpoints/',       # 623 MB - model checkpoints
    '.hermes/projects/',          # 638 MB - project files (may want to keep)
    '.hermes/audio_cache/',       # Audio cache
    '.hermes/image_cache/',       # Image cache
    '.hermes/sandboxes/',         # Sandboxes
    '.hermes/pastes/',            # Paste storage
]

def log(message):
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(log_entry)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log: {e}")

def get_size(path):
    """Get directory size in bytes"""
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
    except:
        pass
    return total

def should_exclude(arcname):
    """Check if path should be excluded"""
    for exclude in EXCLUDE_DIRS:
        if arcname.startswith(exclude) or arcname == exclude.rstrip('/'):
            return True
    return False

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"hermes_backup_{timestamp}.tar.gz")

log("=== Starting Hermes backup ===")
log(f"Source: {SOURCE_DIR}")
log(f"Destination: {backup_file}")

# Check source exists
if not os.path.isdir(SOURCE_DIR):
    log(f"ERROR: Source directory {SOURCE_DIR} does not exist")
    exit(1)

# Calculate sizes
total_size = get_size(SOURCE_DIR)
log(f"Total source size: {total_size / (1024*1024):.1f} MB")

# Calculate excluded size
excluded_size = 0
for excl in EXCLUDE_DIRS:
    full_path = os.path.join("/root", excl)
    if os.path.exists(full_path):
        excl_size = get_size(full_path)
        excluded_size += excl_size
        log(f"  Excluding: {excl} ({excl_size / (1024*1024):.1f} MB)")

included_size = total_size - excluded_size
log(f"Included in backup: {included_size / (1024*1024):.1f} MB")

# Create backup
log("Creating compressed backup...")
try:
    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), "/root"))]
            
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "/root")
                if not should_exclude(arcname):
                    tar.add(file_path, arcname=arcname)
    log("Backup created successfully")
except Exception as e:
    log(f"ERROR: Backup creation failed: {e}")
    exit(1)

# Get backup size
backup_size = os.path.getsize(backup_file)
log(f"Backup size: {backup_size / (1024*1024):.1f} MB")

# Count and cleanup old backups
backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("hermes_backup_") and f.endswith(".tar.gz")])
backup_count = len(backup_files)
log(f"Total backups in directory: {backup_count}")

if backup_count > MAX_BACKUPS:
    delete_count = backup_count - MAX_BACKUPS
    log(f"Removing {delete_count} old backup(s)...")
    for old_backup in backup_files[:-MAX_BACKUPS]:
        old_path = os.path.join(BACKUP_DIR, old_backup)
        log(f"Deleting: {old_path}")
        os.remove(old_path)
    log("Cleanup complete")
else:
    log(f"No cleanup needed (count: {backup_count} <= max: {MAX_BACKUPS})")

# Final summary
remaining = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("hermes_backup_") and f.endswith(".tar.gz")])
log("=== Backup completed successfully ===")
log(f"Backup file: {backup_file}")
log(f"Backup size: {backup_size / (1024*1024):.1f} MB")
log(f"Total backups retained: {len(remaining)}")

print("\n" + "="*60)
print("Backup Summary:")
print(f"  Source: {SOURCE_DIR}")
print(f"  Backup file: {backup_file}")
print(f"  Backup size: {backup_size / (1024*1024):.1f} MB")
print(f"  Total source size: {total_size / (1024*1024):.1f} MB")
print(f"  Excluded (cache): {excluded_size / (1024*1024):.1f} MB")
print(f"  Included: {included_size / (1024*1024):.1f} MB")
print(f"  Total backups: {len(remaining)}")
print(f"  Log file: {LOG_FILE}")
print("="*60)