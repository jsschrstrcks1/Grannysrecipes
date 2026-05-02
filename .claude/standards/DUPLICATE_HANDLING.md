# Duplicate Handling — Granny's Archive

## Definitions

- **Exact duplicate** — same title + essentially identical ingredients + identical instructions.
- **Near duplicate** — same recipe but small differences (e.g., 1 tsp vs 1/2 tsp, extra note, different bake time).

## Rules

1. Compare new recipes against `recipes_master.json` using title similarity, ingredient overlap, and instruction similarity.
2. **Exact duplicates:** append `image_refs` to existing recipe; do not create a new entry.
3. **Near duplicates:** create a variant group; ask for decision (keep both / merge / archive one).
4. **Same title, different recipe:** treat as separate recipes with distinct IDs; flag `[SAME TITLE, DIFFERENT RECIPE]`.

## Variants Display Rule

- Show ONE canonical recipe by default.
- Include a "Variants" dropdown / section listing other versions.
- Each variant shows: source, date (if known), and key differences.
- Never hide variant existence — always surface that alternatives exist.
