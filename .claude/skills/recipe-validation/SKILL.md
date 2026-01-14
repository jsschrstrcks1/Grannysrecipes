# Recipe Validation Skill

Guidance for validating recipes in Granny Hudson's Recipe Archive to ensure schema compliance and data quality.

---

## Core Responsibilities

1. **Schema Compliance** — Ensure all recipes have required fields
2. **Data Quality** — Catch suspicious measurements and errors
3. **Consistency** — Maintain uniform formatting across recipes
4. **Image Integrity** — Verify image references exist

**Remember:** Accuracy is more important than speed. These recipes matter deeply to this family.

---

## Recipe Schema

### Required Fields

```json
{
  "id": "recipe-slug-granny",      // Unique, kebab-case
  "collection": "granny",           // Always "granny" for this repo
  "title": "Recipe Title",          // Human-readable name
  "category": "desserts",           // One of valid categories
  "ingredients": [],                // Non-empty array
  "instructions": []                // Non-empty array
}
```

### Optional Fields

```json
{
  "collection_display": "Granny Hudson",
  "attribution": "Aunt Linda",
  "source_note": "handwritten card",
  "description": "Short description",
  "servings_yield": "24 cookies",
  "prep_time": "15 minutes",
  "cook_time": "30 minutes",
  "total_time": "45 minutes",
  "temperature": "350°F (175°C)",
  "pan_size": "9x13 inch",
  "notes": [],
  "tags": [],
  "image_refs": [],
  "confidence": {},
  "conversions": {},
  "nutrition": {},
  "variant_of": "",
  "canonical_id": ""
}
```

---

## Valid Categories

Exactly one of these (case-sensitive):

```
appetizers
beverages
breads
breakfast
desserts
mains
salads
sides
soups
snacks
```

---

## Validation Checks

### 1. Required Fields Present

Every recipe must have: `id`, `collection`, `title`, `category`, `ingredients`, `instructions`

### 2. ID Format

- Must be kebab-case: `grannys-apple-pie` (not `Granny's Apple Pie`)
- Must be unique across all recipes
- Should end with `-granny` for this collection

### 3. Measurement Sanity

| Ingredient | Maximum Safe Amount |
|------------|---------------------|
| salt | 0.5 cups, 3 tbsp, 6 tsp |
| sugar | 6 cups |
| flour | 10 cups |
| butter | 4 cups |
| baking soda | 4 tsp |
| baking powder | 4 tbsp |

### 4. Temperature Range

- Minimum: 200°F (93°C)
- Maximum: 550°F (288°C)

### 5. Image References

If `image_refs` is present, verify files exist in:
- `granny/*.jpeg`
- `granny/processed/*.jpeg`

---

## Common Validation Errors

### Missing Required Field

```
ERROR: Recipe "apple-pie" missing required field: category
FIX: Add "category": "desserts" to the recipe
```

### Invalid Category

```
ERROR: Recipe "cookies" has invalid category: "desert"
FIX: Change to "desserts" (check spelling)
```

### Duplicate ID

```
ERROR: Duplicate recipe ID: "chocolate-cake-granny"
FIX: Make IDs unique (add variant suffix: "-v2")
```

### Suspicious Measurement

```
WARNING: "salt": "4 cups" exceeds sanity limit (max 0.5 cups)
CHECK: Verify original recipe. Likely OCR error (4 tsp?)
```

### Missing Image

```
WARNING: Image reference "IMG_1234" not found
CHECK: Verify file exists in granny/ folder
```

---

## Running Validation

```bash
# From project root
python scripts/validate-recipes.py

# Expected output (success):
# Validating recipes...
# Checked 101 recipes
# 0 errors, 0 warnings

# Expected output (issues):
# ERROR: Recipe "test" missing field: ingredients
# WARNING: Suspicious measurement in "cake": salt = 2 cups
```

---

## Guardrails

### MUST DO

- Run validation after ANY edit to recipes_master.json
- Fix all ERRORs before committing
- Investigate all WARNINGs (don't auto-dismiss)
- Preserve `[UNCLEAR]` markers until verified
- Re-run sharding script after modifying recipes

### MUST NOT

- Commit recipes with validation errors
- Ignore suspicious measurement warnings
- Remove `[UNCLEAR]` markers without verification
- Auto-fix errors by inventing data
- Assume warnings are false positives

---

## Post-Validation Actions

After fixing all errors:

1. Re-run validation to confirm fixes
2. Update shards if recipes were modified:
   ```bash
   python scripts/shard_recipes.py
   ```
3. Commit with descriptive message
4. Note any intentionally ignored warnings

---

## Integration with Sharding

This repository uses category-based sharding. After modifying `recipes_master.json`:

```bash
# Regenerate shards
python scripts/shard_recipes.py

# This updates:
# - granny/recipes-index.json
# - granny/recipes-{category}.json
```

---

## Resources

- **CLAUDE.md** — Full project guidelines
- **scripts/validate-recipes.py** — Validation script
- **scripts/shard_recipes.py** — Shard generation
- **granny/recipes_master.json** — Master recipe database

---

*Soli Deo Gloria*
