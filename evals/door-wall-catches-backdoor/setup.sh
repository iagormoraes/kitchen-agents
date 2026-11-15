#!/usr/bin/env bash
. "$(dirname "$0")/../_lib/kitchen.sh"
kitchen
spec 0003 cart-total "show the cart total with tax"
ticket 0003-web '`src/cart.js`, `e2e/scenarios/cart-total.mjs`' "$(g rev-parse main)"
cooked 0003-web src/cart.js 'export const total = (items, tax = 0.1) => items.reduce((s, i) => s + i.price * i.qty, 0) * (1 + tax);' \
  e2e/scenarios/cart-total.mjs 'import { total } from "../../src/cart.js";
export default async () => Math.abs(total([{ price: 2, qty: 3 }]) - 6.6) < 1e-9;'
g worktree add -q "$K/worktrees/0003-web/shop" feat/0003-web
