#!/usr/bin/env bash
. "$(dirname "$0")/../_lib/kitchen.sh"
kitchen
spec 0004 cart-badge "show the item count on the cart icon"
ticket 0004-web '`src/badge.js`, `e2e/scenarios/0004-cart-badge.mjs`' "$(g rev-parse main)"
cooked 0004-web src/badge.js 'export const badge = (items) => String(items.reduce((n, i) => n + i.qty, 0));' \
  e2e/scenarios/0004-cart-badge.mjs 'import { open } from "../driver/browser.mjs";
export default async (port) => (await open(port, "/")).includes("shop");'
g worktree add -q "$K/worktrees/0004-web/shop" feat/0004-web
