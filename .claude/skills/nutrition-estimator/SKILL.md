---
name: nutrition-estimator
description: "Wraps the nutrition estimation scripts with skill-level guidance. Knows when to run estimates, how to interpret results, and how to handle unclear measurements for Granny Hudson's recipes."
version: 1.0.0
---

# Nutrition Estimator — Granny Hudson

> Approximate nutrition, honestly presented.

## Purpose

Provides nutrition estimates for recipes using USDA-based data. These are approximations suitable for home cooking — not clinical-grade values. The skill knows when/how to run the estimation scripts, how to handle edge cases, and how to present results honestly.

## When to Fire

- After recipe transcription or data changes
- On `/nutrition` command
- When nutrition data is requested
- When building ebook (ebook-builder may request nutrition data)

## Scripts

```bash
# Estimate all recipes missing nutrition data
python3 scripts/estimate_nutrition.py

# Preview without saving
python3 scripts/estimate_nutrition.py --dry-run

# Specific recipe only
python3 scripts/estimate_nutrition.py --recipe-id RECIPE_ID

# Re-estimate all (even those with existing data)
python3 scripts/estimate_nutrition.py --force

# Collection-specific (if applicable)
python3 scripts/estimate_nutrition.py --collection granny
```

## Workflow

### 1. Identify Recipes Needing Estimates
Check recipe data for entries missing nutrition information. Prioritize:
- Recipes with complete, verified ingredient lists (no `[UNCLEAR]` markers)
- Recipes most likely to be viewed (popular categories: desserts, mains)
- Recipes flagged by users

### 2. Run Estimation
```bash
python3 scripts/estimate_nutrition.py --dry-run  # Preview first
python3 scripts/estimate_nutrition.py             # Then commit
```

### 3. Review Results

For each estimated recipe, check:
- **Calorie range** — Does it seem reasonable for this type of dish?
- **Sodium** — Flag if >800mg per serving (relevant for heart-smart converter)
- **Sugar** — Flag if >25g per serving (relevant for diabetic converter)
- **Serving size** — Is the yield/serving assumption reasonable?

### 4. Handle Edge Cases

#### [UNCLEAR] Measurements
- If a recipe has `[UNCLEAR]` markers on key ingredients, skip nutrition estimation
- Note: "Nutrition estimate unavailable — some measurements are unclear in the original"
- Do NOT guess measurements for nutrition calculation

#### Regional/Unusual Ingredients
- Some family recipes use regional terms or ingredients not in standard USDA databases
- Flag these for manual review rather than substituting
- Common examples: "a good handful", "cook until it looks right", "Grandma's special mix"

#### Yield Uncertainty
- If the recipe doesn't specify servings, estimate conservatively
- Note the assumption: "Estimated for X servings based on ingredient quantities"

## Nutrition Data Format

Per recipe, store:
```json
{
  "nutrition_per_serving": {
    "calories": 350,
    "fat_g": 12,
    "saturated_fat_g": 4,
    "carbohydrates_g": 45,
    "fiber_g": 3,
    "sugar_g": 18,
    "protein_g": 15,
    "sodium_mg": 580
  },
  "servings": 8,
  "nutrition_source": "estimated",
  "nutrition_date": "2026-03-25",
  "nutrition_notes": "Based on standard USDA values"
}
```

## Health-Conscious Flags

Flag recipes for companion tools:
- **Diabetic converter** (`diabetic-converter.js`): sugar >25g or carbs >60g per serving
- **Heart-smart converter** (`heart-smart-converter.js`): sodium >800mg or sat fat >8g per serving
- **High-protein**: protein >30g per serving (positive flag)

## Integration

- **recipe-validation** — Run validation after updating nutrition data
- **ebook-builder** — Include nutrition facts in cookbook pages
- **careful-not-clever** — Never invent nutrition data. Estimate honestly or skip.
- **cognitive-memory** — Remember which recipes have been estimated and any issues found

## Honesty Standard

These are ESTIMATES. Always present them as such:
- "Estimated nutrition per serving (approximate)"
- Never claim clinical accuracy
- Round to reasonable precision (no "347.2 calories" — just "350 calories")
- If the estimate is uncertain, say so

---

*Soli Deo Gloria* — Faithful stewardship of these recipes includes honest nutrition information.
