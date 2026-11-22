#!/usr/bin/env bash
. "$(dirname "$0")/../_lib/kitchen.sh"
kitchen
spec 0001 invoice-export "export an invoice as CSV"
ticket 0001-web '`src/invoice/`, `e2e/scenarios/invoice-export.mjs`' "$(g rev-parse main)"
cooked 0001-web src/invoice/export.js 'export const csv = (inv) => inv.lines.map((l) => `${l.name},${l.price}`).join("\n");' \
  e2e/scenarios/invoice-export.mjs 'import { open } from "../driver/browser.mjs";
export default async (port) => (await open(port, "/invoice.csv")).includes(",");'
sha=$(g rev-parse feat/0001-web)
put "$K/orders/0001-web/verdict-$sha.md" <<V
# Verdict 0001-web @ $sha

**Result:** clean · **Act on:** none · **Consider:** none · evidence spot-check: ok
V
ev="$K/orders/0001-web/evidence/web-20261114-100000"
put "$ev/result.json" <<R
{"commit": "$sha", "buildTime": "2026-11-14T10:00:00Z", "status": "pass", "selected": "all",
 "checks": [{"id": "S1.invoice-export", "pass": true, "detail": "csv downloaded"}, {"id": "home-page", "pass": true, "detail": ""}]}
R
mkdir -p "$ev/invoice-export"; printf '\x89PNG\r\n\x1a\nfake' > "$ev/invoice-export/01-download.png"
# reviewed clean and fully proven: order branch merged, owner's folder still on main (no pass yet)
g switch -q -c order/0001 main && g merge -q --no-ff feat/0001-web -m "Merge feat/0001-web" && g switch -q main
