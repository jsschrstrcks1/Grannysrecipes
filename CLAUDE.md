# Family Recipe Archive - AI Assistant Context

## Project Mission & Values

This is a labor of love being performed by a Reformed Baptist family. Our ethos is **Soli Deo Gloria** (Glory to God Alone).

We are endeavoring to preserve well-loved recipes from three generations of family cooks:
- **Grandma Baker** - Michigan roots, transplanted to Florida (Southern & Northern recipes)
- **MomMom Baker** - Family recipes passed down through generations
- **Granny Hudson** - Additional family collection (future)

**Accuracy is more important than speed.** There are hundreds of real people that will be impacted by these recipes. They matter deeply to this family.

---

## Recipe Collections

### Collection Configuration
```json
{
  "collections": {
    "grandma": {
      "id": "grandma",
      "display_name": "Grandma Baker",
      "folder": "data/",
      "description": "Michigan roots, Southern cooking"
    },
    "mommom": {
      "id": "mommom",
      "display_name": "MomMom Baker",
      "folder": "data/mom/",
      "description": "Family recipes passed down through generations"
    },
    "granny": {
      "id": "granny",
      "display_name": "Granny Hudson",
      "folder": "data/granny/",
      "description": "Additional family collection"
    },
    "reference": {
      "id": "reference",
      "display_name": "Reference Cookbook",
      "folder": "data/all/",
      "description": "Digital cookbook recipes (used with permission)",
      "hidden_from_filters": true,
      "show_only_in_all": true
    }
  }
}
```

**Note:** The `reference` collection uses special flags:
- `hidden_from_filters: true` - Don't show as a filter option in the UI
- `show_only_in_all: true` - Only visible when user selects "All" recipes

### Collection Rules
1. **Every recipe MUST have a `collection` field** - identifies which family member's recipe box it came from
2. **Use collection ID** (lowercase) in the recipe JSON: `"collection": "grandma"`
3. **Website displays `collection_display`** for user-friendly names
4. **Filtering** - Users can view all recipes or filter by collection

---

## OCR Correction Guidelines

### Common OCR Errors to Watch For
- `l` ↔ `1` (lowercase L vs number one)
- `O` ↔ `0` (letter O vs zero)
- `rn` ↔ `m` (r-n combination vs letter m)
- `cl` ↔ `d` (c-l combination vs letter d)
- `tsp` vs `tbsp` (critical for measurements!)

### Measurement Standardization
| Original | Standardized |
|----------|-------------|
| teaspoon, t, t. | tsp |
| tablespoon, T, Tbsp, Tbs | tbsp |
| cup, c, C | cup |
| ounce, oz | oz |
| pound, lb, # | lb |
| pint, pt | pint |
| quart, qt | quart |

### Temperature Format
Prefer dual format for accessibility: `350°F (175°C)`

---

## OCR Pre-Processing Safeguards

### CRITICAL: Before Processing ANY New Image Batch

#### Step 0: MANDATORY Dimension Pre-Flight Check (RUN FIRST!)

**API LIMIT**: Claude's API rejects images >2000px in any dimension with error:
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error",
"message":"messages.X.content.X.image.source.base64.data: At least one of
the image dimensions exceed max allowed size for many-image requests: 2000 pixels"}}
```

**BEFORE reading ANY recipe images, run:**
```bash
# Check manifest status - shows oversized/broken images
python scripts/image_safeguards.py status

# If no manifest exists or status shows oversized images:
python scripts/process_images.py --collection mommom
python scripts/image_safeguards.py validate
```

**Collection-Specific Rules:**

| Collection | Source | Max Dimension | Path to Use |
|------------|--------|---------------|-------------|
| Grandma | Scanner | ≤1280px | `data/*.jpeg` (direct) |
| MomMom | iPhone | 4032x3024px | `data/mom/processed/*.jpeg` (NEVER originals!) |
| Reference | Kindle | 1320x2868px | `data/all/processed/*.jpeg` (NEVER originals!) |
| Granny | TBD | TBD | TBD |

**NEVER read MomMom images from `data/mom/*.jpeg` directly!**
**NEVER read Reference images from `data/all/*.PNG` directly!**
**ALWAYS use `data/mom/processed/*.jpeg` for MomMom collection.**
**ALWAYS use `data/all/processed/*.jpeg` for Reference collection.**

#### Step 1: Source Classification
Identify the image type BEFORE attempting extraction:

| Source Type | Indicators | Action |
|-------------|------------|--------|
| **Handwritten cards** | Cursive/print handwriting, index cards, aged paper | Process normally |
| **Magazine clippings** | Printed text, newspaper/magazine layout, ads nearby | Process normally |
| **Digital screenshots** | "Location X of Y", percentage indicators, e-reader UI | **STOP - requires special handling** |
| **Typed cards** | Typewriter font, consistent spacing | Process normally |
| **Cookbook pages** | Professional layout, copyright notices | **Verify family ownership** |

#### Step 2: Completeness Check (MANDATORY)
**DO NOT extract a recipe unless ALL THREE elements are present:**

1. ✅ **Title** - Recipe name clearly visible
2. ✅ **Ingredients** - At least partial ingredient list
3. ✅ **Instructions** - At least partial directions

If any element is missing, classify the image as:
- `FRAGMENT_START` - Has title + ingredients, instructions cut off
- `FRAGMENT_MIDDLE` - Instructions only, no title
- `FRAGMENT_END` - Only "Serving suggestion" or final steps
- `MULTI_RECIPE` - Contains end of one recipe + start of another

#### Step 3: Fragment Handling Protocol

```
IF image is FRAGMENT_START or FRAGMENT_MIDDLE or FRAGMENT_END:
    1. DO NOT create recipe entry yet
    2. Log in processed_images.json as:
       {
         "image": "IMG_XXXX.PNG",
         "status": "fragment",
         "fragment_type": "FRAGMENT_END",
         "visible_content": "Serving suggestion for [recipe name if known]",
         "needs_pairing": true
       }
    3. Search adjacent images for matching fragments
    4. Only extract AFTER all fragments are assembled
```

#### Step 4: Digital Screenshot Special Handling

For e-reader/Kindle screenshots (identified by "Location X of Y" footer):

1. **Sort by Kindle location number** before processing (NOT by filename)
2. **Check for commercial copyright** - Do not process copyrighted cookbooks without explicit permission
3. **Identify the source cookbook** - Record in `source_note`
4. **Map page boundaries** - Note which recipes span multiple screenshots
5. **Flag collection mismatch** - These are NOT family recipes; clarify with user before adding

#### Step 5: Batch Validation Checklist

Before processing a new folder of images:

- [ ] All images are from the same source/collection?
- [ ] Image filenames follow expected pattern?
- [ ] No obvious duplicates of already-processed images?
- [ ] Source type identified (handwritten/digital/printed)?
- [ ] Copyright status verified for non-family sources?
- [ ] Fragment images identified and grouped?

### Failure Recovery

If a previous processing attempt failed or produced bad data:

1. **Check `processed_images.json`** for partial entries
2. **Review fragments** - Were multi-page recipes incorrectly split?
3. **Verify collection assignment** - Did recipes get wrong `collection` field?
4. **Look for hallucinated content** - Did AI invent missing instructions?
5. **Check for duplicate IDs** - Recipe ID collisions cause data loss

### Recovering from 2000px Dimension Error

If you encounter this error:
```
API Error: 400 ... image dimensions exceed max allowed size ... 2000 pixels
```

**STOP immediately.** Do NOT retry the same request. Follow these steps:

1. **Identify which collection caused the error:**
   - MomMom images (`data/mom/`) are always oversized (4032x3024px)
   - Reference images (`data/all/`) are always oversized (1320x2868px)
   - Grandma images (`data/`) are usually safe (≤1280px)

2. **Run the image processing script:**
   ```bash
   python scripts/process_images.py --collection mommom
   python scripts/process_images.py --collection reference
   ```

3. **Update the manifest:**
   ```bash
   python scripts/image_safeguards.py validate
   ```

4. **Resume with correct paths:**
   - Use `data/mom/processed/*.jpeg` for MomMom images
   - Use `data/all/processed/*.jpeg` for Reference images
   - NEVER use `data/mom/*.jpeg` or `data/all/*.PNG` directly

5. **If the error persists:** The image may be corrupted or in an unexpected format. Mark it as broken:
   ```bash
   python scripts/image_safeguards.py mark "filename.jpeg" broken "Dimension error"
   ```

**Why the loop happens:** When Claude encounters this error, it cannot process the response and may repeatedly attempt the same failing request. The only recovery is to ensure ALL images are ≤2000px BEFORE starting any OCR batch.

### Red Flags - STOP and Ask User

- Image shows only 1-2 lines of text (likely fragment)
- "Location X of Y" footer visible (digital source)
- Copyright notice visible
- Recipe title doesn't match family naming patterns
- Instructions reference "see page X" (multi-page recipe)
- Image quality too poor to read measurements reliably

---

## Recipe Schema

```json
{
  "id": "stable-slug-like-aunt-lindas-pound-cake",
  "collection": "grandma",
  "collection_display": "Grandma Baker",
  "title": "",
  "category": "desserts",
  "attribution": "",
  "source_note": "e.g., handwritten card, magazine clipping, church cookbook",
  "description": "1–2 sentences, only if supported by text",
  "servings_yield": "",
  "prep_time": "",
  "cook_time": "",
  "total_time": "",
  "ingredients": [
    {"item": "", "quantity": "", "unit": "", "prep_note": ""}
  ],
  "instructions": [
    {"step": 1, "text": ""}
  ],
  "temperature": "",
  "pan_size": "",
  "notes": [""],
  "tags": ["dessert", "holiday", "bread", "casserole"],
  "confidence": {
    "overall": "high|medium|low",
    "flags": []
  },
  "image_refs": ["IMG_001"],
  "page_continuation": {"continues_from": "", "continues_to": ""},

  "conversions": {
    "has_conversions": true,
    "conversion_assumptions": [
      "All-purpose flour: 1 cup = 120g",
      "Granulated sugar: 1 cup = 200g",
      "Brown sugar (packed): 1 cup = 220g",
      "Butter: 1 tbsp = 14g, 1 cup = 227g",
      "Milk/liquids: 1 cup = 240ml"
    ],
    "ingredients_metric": [
      {"item": "", "quantity": "", "unit": "g|ml", "prep_note": ""}
    ],
    "temperature_c": ""
  },

  "nutrition": {
    "status": "complete|partial|insufficient_data",
    "per_serving": {
      "calories": null,
      "fat_g": null,
      "carbs_g": null,
      "protein_g": null,
      "sodium_mg": null,
      "fiber_g": null,
      "sugar_g": null
    },
    "missing_inputs": [],
    "assumptions": []
  },

  "variant_of": "",
  "variant_notes": "",
  "canonical_id": ""
}
```

---

## Quality Checklist

- [ ] Cross-check ingredient quantities against instructions
- [ ] Flag implausible amounts (e.g., "4 cups salt" is probably an OCR error)
- [ ] Preserve original voice where possible—don't over-modernize Grandma's wording
- [ ] Verify temperatures are reasonable (most baking: 300-425°F)
- [ ] Check that liquid-to-dry ratios make sense
- [ ] Ensure baking times align with temperatures and pan sizes

---

## File Naming & Organization

### Convention
`category/recipe-name.md`

Examples:
- `desserts/grandmas-apple-pie.md`
- `mains/sunday-pot-roast.md`
- `breads/buttermilk-biscuits.md`

### Categories
- appetizers
- beverages
- breads
- breakfast
- desserts
- mains
- salads
- sides
- soups
- snacks

### Front Matter Requirements
```yaml
---
title: "Recipe Title"
category: desserts
yield: "24 cookies"
prep_time: "15 minutes"
cook_time: "10 minutes"
source: "handwritten card"
tags: [cookies, nuts, holiday]
confidence: high
---
```

---

## Non-Negotiable Rules

1. **Do NOT invent** ingredients, steps, temperatures, times, or yields
2. If anything is **unreadable or ambiguous**, mark it as `[UNCLEAR]` and provide 2–3 best guesses labeled as `[GUESS]` with confidence levels
3. **Preserve original intent**, but normalize spelling and formatting for readability
4. **Keep family names/attributions** if present (e.g., "Aunt Linda's Pound Cake")
5. **Never discard a scan reference** - even merged duplicates must keep all image_refs

---

## Duplicate Handling

### Definitions
- **Exact duplicate:** Same title + essentially identical ingredients + identical instructions
- **Near duplicate:** Same recipe but small differences (e.g., 1 tsp vs 1/2 tsp, extra note, different bake time)

### Rules
1. Compare new recipes against `recipes_master.json` using title similarity, ingredient overlap, and instruction similarity
2. **Exact duplicates:** Append image_refs to existing recipe, do not create new entry
3. **Near duplicates:** Create variant group, ask for decision (keep both / merge / archive one)
4. **Same title, different recipe:** Treat as separate recipes with distinct IDs, flag: `[SAME TITLE, DIFFERENT RECIPE]`

### Variants Display Rule (Website/E-Book)
- Show ONE canonical recipe by default
- Include a "Variants" dropdown/section listing other versions
- Each variant shows: source, date (if known), and key differences
- Never hide variant existence—always surface that alternatives exist

---

## Nutrition Coverage Questions

When extracting a recipe, generate TWO separate question lists:

### 1. Standard Questions (as before)
- Missing steps, unclear ingredients, continuation pages, etc.

### 2. Nutrition Blockers (NEW - separate mini-list)
Title this section: **"Nutrition blockers (answering these increases nutrition coverage)"**

Ask ONLY the minimum questions required to compute estimated nutrition:

| Question Type | When to Ask | Example |
|--------------|-------------|---------|
| **servings_yield** | Not specified or ambiguous | "Makes how many? [GUESS 0.6] 24 cookies / [GUESS 0.3] 36 cookies / other" |
| **Can/jar sizes** | Generic "1 can" listed | "1 can evaporated milk — what size? [GUESS 0.55] 12 oz / [GUESS 0.30] 14 oz / other" |
| **Package sizes** | "1 box" or "1 package" | "1 box pudding mix — [GUESS 0.7] 3.4 oz instant / [GUESS 0.2] 5.1 oz cook & serve / other" |
| **Ingredient types** | Macros vary significantly | "Ground beef — [GUESS 0.5] 80/20 / [GUESS 0.3] 85/15 / [GUESS 0.2] 90/10" |
| **Milk type** | Just says "milk" | "[GUESS 0.5] whole / [GUESS 0.3] 2% / [GUESS 0.2] skim" |

### Format for Nutrition Questions
```
Q: "1 can tomatoes" — what size?
   [GUESS 0.50] 14.5 oz / [GUESS 0.35] 28 oz / [GUESS 0.15] other: ___
```

### Rules
1. Provide sensible defaults as suggestions with confidence levels
2. **DO NOT assume without user approval** — always ask
3. If user skips these questions:
   - Set `nutrition.status = "insufficient_data"`
   - List what's missing in `nutrition.missing_inputs`
4. If user approves defaults:
   - Set `nutrition.status = "complete"` or `"partial"`
   - Document assumptions in `nutrition.assumptions`

---

## Measurement Conversions

### Rules
1. **Always preserve original units** — never replace what was written
2. Provide metric conversions as a **separate, optional view**
3. Label conversions clearly: "Converted (approx.)"
4. **Never convert [UNCLEAR] amounts** — only convert confirmed values
5. Include both °F and °C for all oven temperatures

### Standard Conversion Table
| US Measure | Metric Equivalent | Notes |
|------------|-------------------|-------|
| 1 cup all-purpose flour | 120g | Spooned & leveled |
| 1 cup bread flour | 130g | |
| 1 cup cake flour | 115g | |
| 1 cup granulated sugar | 200g | |
| 1 cup brown sugar (packed) | 220g | |
| 1 cup powdered sugar | 120g | Sifted |
| 1 cup butter | 227g (2 sticks) | |
| 1 tbsp butter | 14g | |
| 1 cup milk/water/liquid | 240ml | |
| 1 cup sour cream/yogurt | 240g | |
| 1 cup honey/syrup | 340g | |
| 1 oz | 28g | |
| 1 lb | 454g | |

### Temperature Conversions
| Fahrenheit | Celsius | Description |
|------------|---------|-------------|
| 250°F | 120°C | Very low |
| 300°F | 150°C | Low |
| 325°F | 165°C | Low-moderate |
| 350°F | 175°C | Moderate |
| 375°F | 190°C | Moderate-high |
| 400°F | 200°C | Hot |
| 425°F | 220°C | Hot |
| 450°F | 230°C | Very hot |
| 475°F | 245°C | Very hot |
| 500°F | 260°C | Extremely hot |

### Conversion JSON Structure
```json
"conversions": {
  "has_conversions": true,
  "conversion_assumptions": [
    "All-purpose flour: 1 cup = 120g (spooned & leveled)"
  ],
  "ingredients_metric": [
    {"item": "flour", "quantity": "330", "unit": "g", "prep_note": "sifted"}
  ],
  "temperature_c": "190°C"
}
```

---

## Project Structure

```
Grandmasrecipes/
├── CLAUDE.md                 # This file
├── README.md                 # Setup and hosting instructions
├── index.html                # Home page (root for GitHub Pages)
├── recipe.html               # Recipe detail page
├── styles.css                # Stylesheet
├── script.js                 # Client-side rendering
├── data/
│   ├── *.jpeg               # Grandma Baker's original scans (≤1280px, AI-safe)
│   ├── mom/                 # MomMom Baker's scans (4032x3024px, OVERSIZED!)
│   │   ├── *.jpeg           # NEVER use directly - too large for API
│   │   └── processed/       # AI-friendly versions (≤2000px) - USE THESE!
│   │       └── *.jpeg
│   ├── all/                 # Reference collection (1320x2868px, OVERSIZED!)
│   │   ├── *.PNG            # NEVER use directly - too large for API
│   │   └── processed/       # AI-friendly versions (≤2000px) - USE THESE!
│   │       └── *.jpeg
│   ├── granny/              # Granny Hudson's scans (future)
│   │   └── *.jpeg
│   ├── recipes_master.json  # All recipes (all collections)
│   ├── collections.json     # Collection metadata
│   ├── processed_images.json # Scan processing log (legacy OCR tracking)
│   └── image_manifest.json  # Image validation status & dimensions
├── scripts/
│   ├── validate-recipes.py  # Recipe validation script
│   ├── process_images.py    # Image resizing for AI processing
│   ├── image_safeguards.py  # Broken image detection & session resilience
│   └── optimize_images.py   # JPEG optimization for repo size
└── ebook/
    ├── book.html            # Print-optimized HTML
    └── print.css            # Print stylesheet
```

---

## Image Processing Safeguards

### The Problem
- **Grandma's images**: Scanner-sourced, 1280px max — AI-friendly
- **MomMom's images**: iPhone photos, 4032x3024px — too large for reliable AI processing (>2000px limit)
- **Reference images**: Kindle screenshots, 1320x2868px — height exceeds 2000px limit
- **Broken images**: Corrupted or truncated files can crash AI sessions

### Solution: Two-Layer Protection

#### 1. Image Resizing (`scripts/process_images.py`)

Resizes oversized images to max 2000px while preserving quality for OCR.

```bash
# Preview what will be processed (no changes)
python scripts/process_images.py --dry-run

# Process a specific collection
python scripts/process_images.py --collection mommom

# Process all collections
python scripts/process_images.py
```

**Output**: Creates `data/mom/processed/` folder with AI-friendly versions.

**For MomMom images**: Always use the processed versions at `data/mom/processed/*.jpeg`

#### 2. Image Safeguards (`scripts/image_safeguards.py`)

Creates a manifest tracking image status to prevent broken images from crashing sessions.

```bash
# Validate all images and create manifest
python scripts/image_safeguards.py validate

# Check current status
python scripts/image_safeguards.py status

# Get next unprocessed image
python scripts/image_safeguards.py next mommom

# Mark an image as processed/skipped
python scripts/image_safeguards.py mark "Moms Recipes - 1.jpeg" processed
python scripts/image_safeguards.py mark "Moms Recipes - 2.jpeg" skipped "Not a recipe"

# List broken images
python scripts/image_safeguards.py broken
```

### Image Status Values
| Status | Meaning |
|--------|---------|
| `valid` | Ready to process |
| `oversized` | Valid but >2000px (use processed version) |
| `resized` | Processed version available |
| `broken` | Cannot read (skip) |
| `recoverable` | Partially corrupted (may work) |
| `processed` | Recipe extraction complete |
| `skipped` | Not a recipe |

### Workflow for Processing MomMom Images

1. **Before starting a new session**:
   ```bash
   python scripts/image_safeguards.py status
   ```

2. **Use processed images** from `data/mom/processed/` (not originals)

3. **If an image fails**, mark it:
   ```bash
   python scripts/image_safeguards.py mark "filename.jpeg" broken "Error description"
   ```

4. **Resume where you left off** — the manifest tracks session state

### Recovering from Crashes

If a session crashes mid-processing:
1. The manifest (`data/image_manifest.json`) preserves state
2. Run `python scripts/image_safeguards.py status` to see progress
3. Run `python scripts/image_safeguards.py next mommom` to get the next image
4. Continue processing without losing work

---

## Repository Bloat Management

### The Problem
- **Current repo size**: ~1 GB in images alone
- **Git history**: Another ~1 GB (images are versioned)
- **Root cause**: Scanner software saves at 100% JPEG quality

### Solution: Image Optimization (`scripts/optimize_images.py`)

Re-compresses JPEGs at Q85 (visually identical, human-readable) for major size reduction.

```bash
# Preview savings (no changes)
python scripts/optimize_images.py --dry-run

# Optimize a specific collection
python scripts/optimize_images.py --collection grandma

# Optimize with backups (keeps .original.jpeg files)
python scripts/optimize_images.py --backup

# Custom quality (default: 85)
python scripts/optimize_images.py --quality 80
```

### Expected Savings

| Collection | Original | Optimized (Q85) | Savings |
|------------|----------|-----------------|---------|
| Grandma (687 images) | 804 MB | ~113 MB | **86%** |
| MomMom (104 images) | 218 MB | ~153 MB | **30%** |
| **Total** | **1,022 MB** | **~266 MB** | **~750 MB** |

### Important Notes

1. **Run once**: The script tracks optimized images in `optimization_manifest.json`
2. **Human-readable**: Q85 is visually identical to originals for recipe reading
3. **Git history**: Old versions remain in .git — consider `git gc` or fresh clone
4. **Backups optional**: Use `--backup` to keep originals as `.original.jpeg`

### Reducing Git History Size

After optimizing images, the old versions still exist in git history. Options:

1. **Accept it**: Clone size stays large but working directory is smaller
2. **Shallow clone**: `git clone --depth 1` for new contributors
3. **BFG Repo-Cleaner**: Rewrite history (destructive, coordinate with team)
4. **Git LFS migration**: Move images to LFS (requires setup)
