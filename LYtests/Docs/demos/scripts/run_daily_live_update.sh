#!/bin/zsh
set -euo pipefail

BASE="/Users/ios15/Documents/New project/LYtests/Docs/demos"
LOG="$BASE/scripts/live_update.log"

cd "$BASE"
/usr/bin/python3 scripts/generate_live_data_from_whitelist.py \
  --out hardtech-live-data.json \
  --limit 10 \
  --backfill-days 5 \
  --archive-days 7 >> "$LOG" 2>&1
cp hardtech-live-data.json site/hardtech-live-data.json
