# Nutrition Coverage Questions — Granny's Archive

When extracting a recipe, generate **two** separate question lists:

1. **Standard questions** (missing steps, unclear ingredients, continuation pages, etc.)
2. **Nutrition blockers** (only the minimum needed to compute estimated nutrition)

Title the second list: **"Nutrition blockers (answering these increases nutrition coverage)"**.

## Question Types

| Type | When | Example |
|---|---|---|
| `servings_yield` | Not specified or ambiguous | "Makes how many? [GUESS 0.6] 24 cookies / [GUESS 0.3] 36 cookies / other" |
| Can / jar size | Generic "1 can" | "1 can evaporated milk — size? [GUESS 0.55] 12 oz / [GUESS 0.30] 14 oz / other" |
| Package size | "1 box" / "1 package" | "1 box pudding mix — [GUESS 0.7] 3.4 oz instant / [GUESS 0.2] 5.1 oz cook & serve / other" |
| Ingredient type | Macros vary | "Ground beef — [GUESS 0.5] 80/20 / [GUESS 0.3] 85/15 / [GUESS 0.2] 90/10" |
| Milk type | Just says "milk" | "[GUESS 0.5] whole / [GUESS 0.3] 2% / [GUESS 0.2] skim" |

## Format

```
Q: "1 can tomatoes" — what size?
   [GUESS 0.50] 14.5 oz / [GUESS 0.35] 28 oz / [GUESS 0.15] other: ___
```

## Rules

1. Provide sensible defaults with confidence levels.
2. **Do NOT assume without user approval** — always ask.
3. If user skips:
   - `nutrition.status = "insufficient_data"`.
   - List gaps in `nutrition.missing_inputs`.
4. If user approves defaults:
   - `nutrition.status = "complete"` or `"partial"`.
   - Document assumptions in `nutrition.assumptions`.
