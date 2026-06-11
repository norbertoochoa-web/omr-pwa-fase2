#!/bin/bash
# Cleanup OMR data older than 30 days
# Run daily via cron: 0 3 * * * /path/to/cleanup-omr-data.sh

DATA_DIR="${DATA_DIR:-/var/omr/data}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

echo "[$(date)] Cleaning up files older than $RETENTION_DAYS days in $DATA_DIR/outputs"

find "$DATA_DIR/outputs" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" -o -name "*.txt" \) -mtime +$RETENTION_DAYS -delete

find "$DATA_DIR/outputs" -type d -empty -delete

echo "[$(date)] Cleanup complete"
