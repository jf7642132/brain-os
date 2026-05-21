#!/bin/bash
# Chronicle Agent Git commit helper
# Run this after writing a log file to commit it to the wiki repo

cd <KNOWLEDGE_DIR> || exit 1
git add -A
git commit -m "auto: Chronicle Agent scan $(date '+%Y-%m-%d %H:%M')"
