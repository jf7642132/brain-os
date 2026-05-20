#!/bin/bash

# Backup script for /root/.hermes
SOURCE_DIR="/root/.hermes"
BACKUP_DIR="/root/hermes-backups"
LOG_FILE="/var/log/hermes-backup.log"
MAX_BACKUPS=15

mkdir -p "$BACKUP_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Starting Hermes backup process"
log "=========================================="

# Remove empty backup from failed attempt
rm -f "${BACKUP_DIR}/hermes-backup-20260514_020717.tar.gz"

# Calculate source size
SOURCE_SIZE=$(du -sh "$SOURCE_DIR" 2>/dev/null | cut -f1)
log "Source directory: $SOURCE_DIR"
log "Source size: $SOURCE_SIZE"

# Create backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/hermes-backup-${TIMESTAMP}.tar.gz"

log "Creating backup: $BACKUP_FILE"

# Create the tar.gz archive
tar -czf "$BACKUP_FILE" -C /root .hermes 2>>"$LOG_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -sh "$BACKUP_FILE" 2>/dev/null | cut -f1)
    log "Backup created successfully: $BACKUP_FILE"
    log "Backup size: $BACKUP_SIZE"
else
    log "ERROR: Backup creation failed"
    exit 1
fi

# Count current backups
BACKUP_COUNT=$(ls -1 "${BACKUP_DIR}"/hermes-backup-*.tar.gz 2>/dev/null | wc -l)
log "Total backups in directory: $BACKUP_COUNT"

# Delete old backups if exceeding MAX_BACKUPS
if [ $BACKUP_COUNT -gt $MAX_BACKUPS ]; then
    DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    log "Deleting $DELETE_COUNT old backup(s) to maintain max $MAX_BACKUPS backups"
    
    # List backups sorted by date (oldest first) and delete excess
    ls -1t "${BACKUP_DIR}"/hermes-backup-*.tar.gz | tail -n $DELETE_COUNT | while read old_backup; do
        log "Deleting old backup: $old_backup"
        rm -f "$old_backup"
    done
    
    # Verify deletion
    NEW_COUNT=$(ls -1 "${BACKUP_DIR}"/hermes-backup-*.tar.gz 2>/dev/null | wc -l)
    log "Remaining backups after cleanup: $NEW_COUNT"
else
    log "Backup count ($BACKUP_COUNT) within limit ($MAX_BACKUPS), no cleanup needed"
fi

# List all current backups
log "Current backups in $BACKUP_DIR:"
ls -lh "${BACKUP_DIR}"/hermes-backup-*.tar.gz 2>/dev/null | while read line; do
    log "  $line"
done

log "=========================================="
log "Backup process completed successfully"
log "=========================================="

# Output summary
echo ""
echo "============================================================"
echo "BACKUP SUMMARY"
echo "============================================================"
echo "Source: $SOURCE_DIR ($SOURCE_SIZE)"
echo "Backup: $BACKUP_FILE ($BACKUP_SIZE)"
echo "Total backups kept: $(ls -1 ${BACKUP_DIR}/hermes-backup-*.tar.gz 2>/dev/null | wc -l)"
echo "Max backups allowed: $MAX_BACKUPS"
echo "Log file: $LOG_FILE"
echo "============================================================"