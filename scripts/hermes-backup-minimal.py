#!/usr/bin/env python3
"""
Hermes Agent Backup Script - Minimal Backup
Creates a compressed backup of essential .hermes files only.
"""

import os
import tarfile
from datetime import datetime

BACKUP_DIR = "/root/hermes-backups"
SOURCE_DIR = "/root/.hermes"
LOG_FILE = "/var/log/hermes-backup.log"
MAX_BACKUPS = 15

# Only include these essential files/directories
INCLUDE_DIRS = [
    'SOUL.md',
    '.env',
    'auth.json',
    'config/',
    'config.yaml',
    'cron/',
    'hooks/',
    'kanban/',
    'kanban.db',
    'knowledge/',
    'learnings/',
    '.learnings/',
    'memories/',
    'scripts/',
    'skills/',
    'state.db',
    'response_store.db',
    'gateway_state.json',
    'channel_directory.json',
    'profiles/',
    'sessions/',
    'logs/',
    'browser_recordings/',
    'plugins/',
    'bin/',
    '.hermes_history',
    '.skills_prompt_snapshot.json',
]

# Directories to always exclude
EXCLUDE_DIRS = [
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
    'models_dev_cache.json',
    'response_store.db-shm',
    'response_store.db-wal',
    'state.db-shm',
    'state.db-wal',
    'auth.lock',
    'gateway.lock',
    'gateway.pid',
    'interrupt_debug.log',
    'cookies.txt',
    'processes.json',
    'pairing/',
    'weixin/',
    'whatsapp/',
]

def safe_getsize(path):
    """Get file size safely, returning 0 on error"""
    try:
        return os.path.getsize(path)
    except:
        return 0

def log(message):
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(log_entry)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except:
        pass

def should_include(arcname):
    """Check if path should be included"""
    # Check exclusion first
    for excl in EXCLUDE_DIRS:
        if arcname == excl or arcname.startswith(excl + '/') or arcname.startswith(excl):
            return False
    
    # Check inclusion list
    for incl in INCLUDE_DIRS:
        if arcname == incl or arcname.startswith(incl + '/') or arcname.startswith(incl):
            return True
    
    return False

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUP_DIR, f"hermes_backup_{timestamp}.tar.gz")

log("=== Starting Hermes backup (minimal) ===")
log(f"Source: {SOURCE_DIR}")
log(f"Destination: {backup_file}")

# Check source exists
if not os.path.isdir(SOURCE_DIR):
    log(f"ERROR: Source directory {SOURCE_DIR} does not exist")
    exit(1)

# Calculate included size
included_size = 0
included_files = 0
for item in INCLUDE_DIRS:
    item_path = os.path.join(SOURCE_DIR, item)
    if os.path.exists(item_path):
        if os.path.isfile(item_path):
            included_size += safe_getsize(item_path)
            included_files += 1
        elif os.path.isdir(item_path):
            for root, dirs, files in os.walk(item_path):
                for f in files:
                    included_size += safe_getsize(os.path.join(root, f))
                    included_files += 1

log(f"Included: {included_files} files, {included_size / (1024*1024):.1f} MB")

# Create backup
log("Creating compressed backup...")
try:
    with tarfile.open(backup_file, "w:gz") as tar:
        for item in INCLUDE_DIRS:
            item_path = os.path.join(SOURCE_DIR, item)
            if os.path.exists(item_path):
                arcname = f".hermes/{item}"
                if os.path.isfile(item_path):
                    tar.add(item_path, arcname=arcname)
                elif os.path.isdir(item_path):
                    for root, dirs, files in os.walk(item_path):
                        for f in files:
                            file_path = os.path.join(root, f)
                            rel_path = os.path.relpath(file_path, SOURCE_DIR)
                            tar.add(file_path, arcname=f".hermes/{rel_path}")
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
print(f"  Files included: {included_files}")
print(f"  Total backups: {len(remaining)}")
print(f"  Log file: {LOG_FILE}")
print("="*60)