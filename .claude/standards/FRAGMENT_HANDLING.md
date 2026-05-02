# Fragment Handling — Granny's Archive

## Step 1: Source Classification

Identify the image type **before** attempting extraction.

| Source type | Indicators | Action |
|---|---|---|
| **Handwritten cards** | Cursive/print handwriting, index cards, aged paper | Process normally |
| **Magazine clippings** | Printed text, magazine layout, ads nearby | Process normally |
| **Digital screenshots** | "Location X of Y", percentage indicators, e-reader UI | **STOP** — special handling |
| **Typed cards** | Typewriter font, consistent spacing | Process normally |
| **Cookbook pages** | Professional layout, copyright notices | **Verify family ownership** |

## Step 2: Completeness Check (mandatory)

Do not extract a recipe unless **all three** are present:

1. ✅ **Title**
2. ✅ **Ingredients** (at least partial)
3. ✅ **Instructions** (at least partial)

If any element is missing, classify the image:

- `FRAGMENT_START` — title + ingredients, instructions cut off
- `FRAGMENT_MIDDLE` — instructions only, no title
- `FRAGMENT_END` — only "Serving suggestion" or final steps
- `MULTI_RECIPE` — end of one recipe + start of another

## Step 3: Fragment Handling Protocol

```
IF image is FRAGMENT_START / FRAGMENT_MIDDLE / FRAGMENT_END:
  1. Do NOT create a recipe entry yet.
  2. Log in processed_images.json:
     {
       "image": "IMG_XXXX.PNG",
       "status": "fragment",
       "fragment_type": "FRAGMENT_END",
       "visible_content": "Serving suggestion for [recipe name if known]",
       "needs_pairing": true
     }
  3. Search adjacent images for matching fragments.
  4. Only extract AFTER all fragments are assembled.
```

## Step 4: Digital Screenshots

For e-reader / Kindle screenshots ("Location X of Y" footer):

1. **Sort by Kindle location number**, NOT filename.
2. **Verify copyright** — do not process commercial cookbooks without permission.
3. **Identify the source cookbook** — record in `source_note`.
4. **Map page boundaries** — note recipes spanning multiple screenshots.
5. **Flag collection mismatch** — these are NOT family recipes; clarify with user.

## Step 5: Batch Validation Checklist

Before processing a new folder:

- [ ] All images from the same source/collection?
- [ ] Filenames follow expected pattern?
- [ ] No obvious duplicates of already-processed images?
- [ ] Source type identified (handwritten / digital / printed)?
- [ ] Copyright status verified for non-family sources?
- [ ] Fragment images identified and grouped?

## Failure Recovery

If a previous attempt produced bad data:

1. **Check `processed_images.json`** for partial entries.
2. **Review fragments** — were multi-page recipes incorrectly split?
3. **Verify collection assignment** — wrong `collection` field?
4. **Look for hallucinated content** — did AI invent missing instructions?
5. **Check for duplicate IDs** — collisions cause data loss.

## Red Flags — STOP and Ask User

- Image shows only 1–2 lines of text (likely fragment).
- "Location X of Y" footer (digital source).
- Copyright notice visible.
- Title doesn't match family naming patterns.
- Instructions reference "see page X" (multi-page recipe).
- Image quality too poor to read measurements reliably.
