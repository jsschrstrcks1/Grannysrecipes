# There is no data here — Granny's corpus lives in `granny/`

**Soli Deo Gloria.**

This repository is the one sibling that does NOT keep its recipe data in `data/`.
Granny Hudson's 567 recipes, their scanned cards, and every index live in
[`granny/`](../granny/):

| What | Where |
|---|---|
| Master corpus | `granny/recipes_master.json` |
| Category shards | `granny/recipes-<category>.json` (10 shards) |
| Shard index | `granny/recipes-index.json` |
| Ingredient index | `granny/ingredient-index.json` |
| Scanned cards | `granny/*.jpeg` |

## Why this directory exists at all

Every sibling repo (Grandmasrecipes, MomsRecipes, Allrecipes) uses `data/`, so a
cross-collection loader written to the obvious convention would look here, find
nothing, and **silently conclude Granny has no recipes** (household ledger
UL-059). This file exists so that failure mode is loud instead of silent: if
your loader led you here, point it at `granny/` — or better, take the path from
explicit configuration, the way the household's consumers do.

## Why the path is NOT being normalised (decision, 2026-07-29)

Deployed consumers pin the `granny/` URL **client-side on GitHub Pages**:

- `Grandmasrecipes/script.js` → `https://jsschrstrcks1.github.io/Grannysrecipes/granny/…`
  (`REMOTE_COLLECTIONS['granny-hudson']`, with `dataPath: 'granny/'` declared explicitly)
- `Allrecipes` aggregates the same URLs
- the operator's Atlas manifest (`ATLAS_RECIPES`) names `granny/recipes_master.json` explicitly

Moving `granny/` → `data/` would require synchronized deploys of three Pages
sites plus an operator-machine manifest edit, and any stale cached page would
break silently — the exact class of failure this archive avoids. Every real
consumer already declares the path explicitly, so the convention gap is a
documentation problem, not a data problem. Recorded as `decided-no` on the
household upgrade ledger (UL-059 / task `recipes-granny-data-path`).

**If you are writing a new consumer:** take each collection's data path from
configuration (a manifest entry, `REMOTE_COLLECTIONS`-style declaration), never
from the `data/` convention. This repo is the reason why.
