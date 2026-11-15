#!/usr/bin/env bash
. "$(dirname "$0")/../_lib/kitchen.sh"
kitchen
handoff() {   # handoff NNNN branch file content: one-commit branch from main, recorded as handed off
  g switch -q -c "$2" main; put "$REPO/$3" <<<"$4"; g add -A && g commit -qm "$2" && g switch -q main
  echo "$2" | put "$K/orders/$1-handoff/shop/branch"
}
spec 0001 invoice-export "export an invoice as CSV"
handoff 0001 invoice-export src/invoice/export.js 'export const csv = (inv) => inv.lines.map((l) => `${l.name},${l.price}`).join("\n");'
g merge -q --squash invoice-export && g commit -qm "Export an invoice as CSV"   # the project merged it: landed
spec 0002 cart-badge "show the item count on the cart icon"
handoff 0002 cart-badge src/cart/badge.js 'export const badge = (items) => String(items.length);'   # open, other paths
spec 0003 invoice-pdf "download an invoice as PDF"
handoff 0003 invoice-pdf src/invoice/pdf.js 'export const pdf = (inv) => `%PDF ${inv.id}`;'          # open, same folder
spec 0004 invoice-email "email an invoice to the customer"
ticket 0004-web '`src/invoice/`, `e2e/scenarios/invoice-email.mjs`' '<the base this order cooks on>'
