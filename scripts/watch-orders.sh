#!/bin/sh
# Watch a kitchen's cooking stations; print one line only when one has stalled.
#   watch-orders.sh <kit folder> [--once]
# Run by the plugin monitor (monitors/monitors.json) the first time kitchen:expedite runs, in the
# session's folder: each line it prints wakes the expediter. Monitors don't start with -p, so a
# headless session keeps watching inside its own turn (expedite §1). Never writes anything.
# A station is cooking when its ticket names a Worktree that exists and its plate isn't done; it
# has stalled when watchdog.sh says it is idle over the limit (KITCHEN_IDLE_MINUTES, default 30).
# Each stalled station is reported once per stall. --once checks a single time (for the tests).
kit=${1:?usage: watch-orders.sh <kit folder> [--once]}; once=$2
limit=${KITCHEN_IDLE_MINUTES:-30}
home=$(python3 -I "$kit/scripts/kitchen.py" find "$PWD" | cut -f1)
[ -n "$home" ] || exit 0
reported=""
while :; do
  while IFS='	' read -r id wt; do
    [ -n "$id" ] || continue
    out=$(ORDERS="$home/orders" sh "$kit/scripts/watchdog.sh" "$wt" "$id" "$limit" 2>/dev/null); code=$?
    case " $reported " in *" $id "*) [ "$code" = 2 ] || reported=$(echo "$reported" | sed "s/ $id//") ;; esac
    if [ "$code" = 2 ] && case " $reported " in *" $id "*) false ;; *) true ;; esac; then
      echo "Kitchen watch: station $id stalled ($out). Stop it and start a fresh run from its ticket and plate (expedite §2); tell the owner."
      reported="$reported $id"
    fi
  done <<STATIONS
$(python3 -I "$kit/scripts/kitchen.py" cooking "$home")
STATIONS
  [ "$once" = "--once" ] && exit 0
  sleep 300
done
