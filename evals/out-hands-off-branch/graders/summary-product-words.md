---
type: regex
target: { source: file, path: .kitchens/shop/orders/0001-handoff/shop/summary.md }
pattern: '\b(kitchen|stations?|tickets?|expediter|order 0001|spec 0001|0001)\b'
flags: i
match: not_contains
---
