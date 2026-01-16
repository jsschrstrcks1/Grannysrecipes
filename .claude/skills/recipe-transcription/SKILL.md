# Recipe Transcription Skill

Specialized guidance for accurately transcribing handwritten recipe cards from Granny Hudson's collection.

---

## Core Principles

| Priority | Principle |
|----------|-----------|
| 1 | **Accuracy-First** — Never guess or invent recipe content |
| 2 | **Preservation-First** — Handwritten images are sacred heirlooms |
| 3 | **Fidelity-First** — Preserve Granny's exact wording |
| 4 | **Readability-First** — Family members need clear, usable recipes |

**Remember:** Accuracy is more important than speed. These recipes matter deeply to this family.

---

## Pre-Transcription Checklist

Before reading any image:

- [ ] Check image dimensions: `python scripts/image_safeguards.py status`
- [ ] Use `granny/processed/` versions if originals exceed 2000px
- [ ] Verify image is complete (not a fragment)
- [ ] Identify source type (handwritten, typed, magazine clipping)

---

## OCR Correction Standards

### Common Character Confusions

| Often Misread | Correct | Context Clue |
|---------------|---------|--------------|
| `l` (ell) | `1` (one) | Numbers in measurements |
| `O` (oh) | `0` (zero) | Numbers in temperatures |
| `rn` | `m` | Words like "warm" → "warrn" |
| `cl` | `d` | Words like "cold" → "colcl" |
| `ii` | `u` | Words like "cup" → "ciip" |

### Critical Measurement Distinctions

| Abbreviation | Meaning | Common OCR Error |
|--------------|---------|------------------|
| `tsp` | teaspoon | Confused with `tbsp` |
| `tbsp` | tablespoon | Confused with `tsp` |
| `c` or `C` | cup | Confused with `e` or `G` |
| `oz` | ounce | Confused with `02` |
| `lb` | pound | Confused with `16` |

**CRITICAL:** A `tbsp` vs `tsp` error can ruin a recipe. Always verify!

---

## Transcription Output Format

```json
{
  "id": "recipe-name-granny",
  "collection": "granny",
  "collection_display": "Granny Hudson",
  "title": "Recipe Title",
  "category": "category",
  "source_note": "handwritten card",
  "ingredients": [
    {"item": "flour", "quantity": "2", "unit": "cups", "prep_note": "sifted"}
  ],
  "instructions": [
    {"step": 1, "text": "Instruction text here"}
  ],
  "notes": [],
  "tags": [],
  "image_refs": ["IMG_1234"],
  "confidence": {
    "overall": "high|medium|low",
    "flags": []
  }
}
```

---

## Confidence Ratings

| Rating | Criteria | Action |
|--------|----------|--------|
| `high` | All text clearly readable | Proceed normally |
| `medium` | 1-3 unclear words | Use `[UNCLEAR]` markers |
| `low` | Multiple unclear sections | Flag for review |

### Using [UNCLEAR] Markers

```json
// Single unclear word with guesses
"quantity": "[UNCLEAR: 1/2 or 1/4]"

// Completely illegible
"item": "[UNCLEAR]"

// Unclear with confidence
"text": "Add [UNCLEAR: butter?] and mix well"
```

---

## Valid Categories

Use exactly one of these:

```
appetizers, beverages, breads, breakfast, desserts,
mains, salads, sides, soups, snacks
```

---

## Measurement Standardization

| Original | Standardized |
|----------|--------------|
| teaspoon, t, t. | tsp |
| tablespoon, T, Tbsp, Tbs | tbsp |
| cup, c, C | cup |
| ounce, oz | oz |
| pound, lb, # | lb |
| pint, pt | pint |
| quart, qt | quart |

### Temperature Format

Always use dual format: `350°F (175°C)`

---

## Guardrails

### MUST DO

- Use `[UNCLEAR]` for any text you cannot read with certainty
- Preserve original spelling and grammar (Granny's voice)
- Check image dimensions before reading
- Run validation after adding recipe
- Include `image_refs` linking to source scan

### MUST NOT

- Invent ingredients, steps, or measurements
- Guess what unclear text says
- "Improve" or modernize Granny's wording
- Delete handwritten image files
- Commit recipes without validation

---

## Post-Transcription Validation

After transcribing:

```bash
# Validate the recipe
python scripts/validate-recipes.py

# Check for issues
# - Required fields present?
# - Valid category?
# - Measurements make sense?
```

---

## Fragment Handling

If an image shows only part of a recipe:

1. Do NOT create a partial recipe entry
2. Log as fragment in `processed_images.json`
3. Search for matching fragments
4. Only transcribe when complete

---

## Resources

- **CLAUDE.md** — Full project guidelines
- **scripts/validate-recipes.py** — Validation tool
- **scripts/image_safeguards.py** — Image dimension checker
- **granny/recipes_master.json** — Recipe database

---

*Soli Deo Gloria*
