#!/bin/sh
# Is a cooking station still moving? The expediter runs this every 30 minutes per station.
#   watchdog.sh <repo dir> <order id> [idle minutes, default 30]
# Progress = the newest of: the repo's last commit, any file under $ORDERS/<order>/ (report,
# evidence). $ORDERS is required: the absolute orders path from the session brief or the ticket.
# Prints the idle minutes; exit 2 when idle is over the limit: stop the station, start a fresh
# run, tell the owner.
repo=$1; order=$2; limit=${3:-30}
orders=${ORDERS:?set ORDERS to the kitchen home orders path}
git -C "$repo" rev-parse --git-dir >/dev/null 2>&1 && [ -n "$order" ] || {
  echo "usage: watchdog.sh <repo dir> <order id> [minutes]"; exit 64; }
[ -d "$orders/$order" ] || { echo "no folder $orders/$order"; exit 64; }
now=$(date +%s)
commit=$(git -C "$repo" log -1 --format=%ct)
# stat -f %m is BSD/macOS; stat -c %Y is GNU/Linux.
newest=$(find "$orders/$order" -type f -exec stat -f %m {} + 2>/dev/null ||
         find "$orders/$order" -type f -exec stat -c %Y {} +)
newest=$(echo "$newest" | sort -n | tail -1)
last=$(( commit > ${newest:-0} ? commit : ${newest:-0} ))
idle=$(( (now - last) / 60 ))
echo "$order: idle ${idle} min (limit ${limit})"
[ "$idle" -le "$limit" ] || exit 2
