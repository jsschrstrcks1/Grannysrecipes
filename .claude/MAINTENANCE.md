# Maintenance Guide for Granny Hudson's Recipe Archive

This guide provides step-by-step workflows for common maintenance tasks.

---

## Table of Contents

1. [Adding New Recipe Images](#adding-new-recipe-images)
2. [Transcribing Handwritten Cards](#transcribing-handwritten-cards)
3. [Updating Existing Recipes](#updating-existing-recipes)
4. [Pre-Deployment Checklist](#pre-deployment-checklist)
5. [Fixing Validation Errors](#fixing-validation-errors)
6. [Regenerating Shards](#regenerating-shards)
7. [Cross-Repository Sync](#cross-repository-sync)

---

## Adding New Recipe Images

### Step 1: Prepare Images

```bash
# Check current image status
python scripts/image_safeguards.py status

# Copy new images to granny/
cp /path/to/new-images/*.jpeg granny/
```

### Step 2: Process Oversized Images

```bash
# Check for oversized images
python scripts/image_safeguards.py validate

# Process any images >2000px
python scripts/process_images.py --collection granny
```

### Step 3: Validate Image Manifest

```bash
# Update the manifest
python scripts/image_safeguards.py validate

# Check status
python scripts/image_safeguards.py status
```

---

## Transcribing Handwritten Cards

### Step 1: Pre-Flight Check

```bash
# ALWAYS run before reading images
python scripts/image_safeguards.py status

# Get next unprocessed image
python scripts/image_safeguards.py next granny
```

### Step 2: Transcribe

1. Read the image (use processed version if oversized)
2. Create recipe JSON following schema in CLAUDE.md
3. Use `[UNCLEAR]` for any uncertain text
4. Set appropriate confidence rating

### Step 3: Add to Master

1. Add recipe to `granny/recipes_master.json`
2. Include `image_refs` with source image filename
3. Set `collection: "granny"` and `collection_display: "Granny Hudson"`

### Step 4: Validate and Mark Complete

```bash
# Validate the recipe
python scripts/validate-recipes.py

# Mark image as processed
python scripts/image_safeguards.py mark "filename.jpeg" processed

# Regenerate shards
python scripts/shard_recipes.py
```

---

## Updating Existing Recipes

### Step 1: Locate Recipe

```bash
# Find recipe by title
grep -n "recipe-title" granny/recipes_master.json
```

### Step 2: Make Changes

1. Edit `granny/recipes_master.json`
2. Preserve `[UNCLEAR]` markers unless verified
3. Update `confidence` if uncertainty resolved

### Step 3: Validate and Regenerate

```bash
# Validate changes
python scripts/validate-recipes.py

# Regenerate shards
python scripts/shard_recipes.py
```

---

## Pre-Deployment Checklist

Before pushing to GitHub Pages:

```bash
# 1. Validate all recipes
python scripts/validate-recipes.py

# 2. Check image manifest
python scripts/image_safeguards.py status

# 3. Regenerate shards
python scripts/shard_recipes.py

# 4. Verify no unresolved [UNCLEAR] markers (optional)
grep -r "UNCLEAR" granny/recipes_master.json | wc -l
```

---

## Fixing Validation Errors

### Missing Required Field

```bash
# Find the recipe
grep -B5 '"id": "recipe-id"' granny/recipes_master.json

# Add missing field (e.g., category)
# Edit the JSON to include: "category": "desserts"
```

### Invalid Category

Valid categories: `appetizers`, `beverages`, `breads`, `breakfast`, `desserts`, `mains`, `salads`, `sides`, `soups`, `snacks`

### Duplicate ID

```bash
# Find duplicates
grep '"id":' granny/recipes_master.json | sort | uniq -d

# Rename one (add suffix like -v2 or -card2)
```

### Suspicious Measurement

1. Check original image
2. Verify measurement is correct
3. If OCR error, fix it
4. If intentional (large batch), add note explaining

---

## Regenerating Shards

After any change to `recipes_master.json`:

```bash
# Regenerate all shards
python scripts/shard_recipes.py

# This updates:
# - granny/recipes-index.json (lightweight index)
# - granny/recipes-{category}.json (full recipe data per category)
```

### Verify Shards

```bash
# Count recipes in index
python -c "import json; d=json.load(open('granny/recipes-index.json')); print(f'Index: {len(d[\"recipes\"])} recipes')"

# Count by category
for f in granny/recipes-*.json; do
  if [[ "$f" != *"index"* ]] && [[ "$f" != *"master"* ]]; then
    count=$(python -c "import json; print(len(json.load(open('$f'))['recipes']))")
    echo "$f: $count recipes"
  fi
done
```

---

## Cross-Repository Sync

This repository (Grannysrecipes) is part of a family of recipe archives:

| Repository | Collection | Hub URL |
|------------|------------|---------|
| Grandmasrecipes | grandma-baker | (Main hub) |
| MomsRecipes | mommom-baker | |
| **Grannysrecipes** | **granny-hudson** | |
| Allrecipes | all | |

### Standards That Must Match

- Recipe schema structure
- Valid categories list
- Measurement abbreviations
- Confidence ratings
- `[UNCLEAR]` marker format

See `.claude/CROSS_REPO_STANDARDS.md` for full details.

### Hub Aggregation

The Grandmasrecipes hub fetches from this repo via:
```
https://jsschrstrcks1.github.io/Grannysrecipes/granny/recipes_master.json
```

Ensure `recipes_master.json` is valid before pushing.

---

## Troubleshooting

### Image Won't Read (2000px Error)

```bash
# Check dimensions
python scripts/image_safeguards.py status

# Process oversized images
python scripts/process_images.py --collection granny

# Use processed version
# Read from: granny/processed/filename.jpeg
```

### Validation Script Not Found

```bash
# Verify script exists
ls scripts/validate-recipes.py

# If missing, check if it needs to be created
# based on CLAUDE.md validation rules
```

### Shards Out of Sync

```bash
# Regenerate all shards
python scripts/shard_recipes.py

# Verify counts match
python -c "
import json
master = json.load(open('granny/recipes_master.json'))
index = json.load(open('granny/recipes-index.json'))
print(f'Master: {len(master[\"recipes\"])} recipes')
print(f'Index: {len(index[\"recipes\"])} recipes')
"
```

---

*Last updated: 2026-01*
