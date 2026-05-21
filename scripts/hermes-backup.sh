#!/bin/bash
# Hermes Agent Backup Script - Optimized version
# Excludes large runtime directories (node) that can be reinstalled
# Creates compressed backup of HERMES_ROOT, keeps max 15 most recent backups

set -e

# Configuration
SOURCE_DIR="${HERMES_ROOT:-$HOME/.hermes}"
BACKUP_DIR="/root/hermes-backups"
LOG_FILE="/var/log/hermes-backup.log"
MAX_BACKUPS=15
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/hermes_backup_${TIMESTAMP}.tar.gz"

# Directories to exclude (can be reinstalled/recreated)
EXCLUDE_DIRS="node node_modules .cache __pycache__"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" | tee -a "$LOG_FILE"
}

# Start backup
log_message "=== Starting Hermes backup ==="
log_message "Source: $SOURCE_DIR"
log_message "Destination: $BACKUP_FILE"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    log_message "ERROR: Source directory $SOURCE_DIR does not exist"
    exit 1
fi

# Get source size (total and excluding large dirs)
SOURCE_SIZE=$(du -sh "$SOURCE_DIR" 2>/dev/null | cut -f1)
log_message "Total source size: $SOURCE_SIZE"

# Create exclude list for tar
EXCLUDE_ARGS=""
for dir in $EXCLUDE_DIRS; do
    if [ -d "$SOURCE_DIR/$dir" ]; then
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$dir"
        EXCLUDED_SIZE=$(du -sh "$SOURCE_DIR/$dir" 2>/dev/null | cut -f1)
        log_message "Excluding: $dir ($EXCLUDED_SIZE)"
    fi
done

# Create the backup using pigz for parallel compression
log_message "Creating compressed backup with pigz..."

tar -cf - $EXCLUDE_ARGS -C "$(dirname $SOURCE_DIR)" "$(basename $SOURCE_DIR)" 2>> "$LOG_FILE" | pigz -p 4 > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_message "SUCCESS: Backup created - $BACKUP_FILE ($BACKUP_SIZE)"
else
    log_message "ERROR: Backup creation failed"
    exit 1
fi

# Clean up old backups (keep only MAX_BACKUPS most recent)
log_message "Cleaning up old backups (keeping $MAX_BACKUPS most recent)..."
BACKUP_COUNT=$(ls -1t "${BACKUP_DIR}"/hermes_backup_*.tar.gz 2>/dev/null | wc -l)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    DELETED_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    log_message "Found $BACKUP_COUNT backups, removing $DELETED_COUNT oldest..."
    
    # List and delete oldest backups
    ls -1t "${BACKUP_DIR}"/hermes_backup_*.tar.gz | tail -n "$DELETED_COUNT" | while read old_backup; do
        log_message "Deleting: $old_backup"
        rm -f "$old_backup"
    done
    log_message "Cleanup complete: $DELETED_COUNT old backup(s) deleted"
else
    log_message "No cleanup needed: $BACKUP_COUNT backups (max: $MAX_BACKUPS)"
fi

# Show current backup status
log_message "Current backups in $BACKUP_DIR:"
ls -lh "${BACKUP_DIR}"/hermes_backup_*.tar.gz 2>/dev/null | while read line; do
    log_message "  $line"
done

log_message "=== Backup completed successfully ==="

# Return summary
echo ""
echo "=== BACKUP SUMMARY ==="
echo "Backup file: $BACKUP_FILE"
echo "Backup size: $BACKUP_SIZE"
echo "Total backups: $BACKUP_COUNT"
echo "Excluded directories: $EXCLUDE_DIRS"
echo "Log file: $LOG_FILE"
