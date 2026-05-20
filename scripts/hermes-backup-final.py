#!/usr/bin/env python3
"""
Hermes Agent Backup Script - Final Run
Creates a compressed backup of /root/.hermes, keeping max 15 most recent backups.
"""

import os
import tarfile
from datetime import datetime

BACKUP_DIR = "/root/hermes-backups"
SOURCE_DIR = "/root/.hermes"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15

# Directories to exclude (large cache/regenerable directories)
EXCLUDE_PATTERNS = [
    'hermes-agent/',
    'state-snapshots/',
    'node/',
    'checkpoints/',
    'projects/',
    'audio_cache/',
    'image_cache/',
    'sandboxes/',
    'pastes/',
    'cache/',
    'logs/',
    'cron/',
    'sessions/',
]

def log(message):
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(log_entry)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except:
        pass

def should_exclude(arcname):
    """Check if path should be excluded"""
    for excl in EXCLUDE_PATTERNS:
        if arcname == excl or arcname.startswith(excl + '/') or arcname.startswith(excl):
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
total_files = 0
total_size = 0
excluded_size = 0
included_size = 0

for root, dirs, files in os.walk(SOURCE_DIR):
    # Filter excluded dirs
    dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), SOURCE_DIR))]
    
    for f in files:
        total_files += 1
        file_path = os.path.join(root, f)
        try:
            size = os.path.getsize(file_path)
        except:
            size = 0
        
        rel_path = os.path.relpath(file_path, SOURCE_DIR)
        if should_exclude(rel_path):
            excluded_size += size
        else:
            included_size += size

log(f"Total files: {total_files}")
log(f"Total size: {total_size / (1024*1024):.1f} MB")
log(f"Included in backup: {included_size / (1024*1024):.1f} MB")
log(f"Excluded (cache): {excluded_size / (1024*1024):.1f} MB")

# Create backup
log("Creating compressed backup...")
try:
    with tarfile.open(backup_file, "w:gz") as tar:
        for root, dirs, files in os.walk(SOURCE_DIR):
            # Filter excluded dirs
            dirs[:] = [d for d in dirs if not should_exclude(os.path.relpath(os.path.join(root, d), SOURCE_DIR))]
            
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
all_backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.tar.gz')])
backup_count = len(all_backups)
log(f"Total backups in directory: {backup_count}")

if backup_count > MAX_BACKUPS:
    delete_count = backup_count - MAX_BACKUPS
    log(f"Removing {delete_count} old backup(s)...")
    for old_backup in all_backups[:-MAX_BACKUPS]:
        old_path = os.path.join(BACKUP_DIR, old_backup)
        log(f"Deleting: {old_path}")
        os.remove(old_path)
    log("Cleanup complete")
else:
    log(f"No cleanup needed (count: {backup_count} <= max: {MAX_BACKUPS})")

# Final summary
remaining = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith('.tar.gz')])
log("=== Backup completed successfully ===")
log(f"Backup file: {backup_file}")
log(f"Backup size: {backup_size / (1024*1024):.1f} MB")
log(f"Total backups retained: {len(remaining)}")

print("\n" + "="*60)
print("Backup Summary:")
print(f"  Source: {SOURCE_DIR}")
print(f"  Backup file: {backup_file}")
print(f"  Backup size: {backup_size / (1024*1024):.1f} MB")
print(f"  Files backed up: {total_files}")
print(f"  Included size: {included_size / (1024*1024):.1f} MB")
print(f"  Excluded (cache): {excluded_size / (1024*1024):.1f} MB")
print(f"  Total backups: {len(remaining)}")
print(f"  Log file: {LOG_FILE}")
print("="*60)