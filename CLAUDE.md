# Granny Hudson's Recipe Archive — AI Assistant Context

**Version:** 2.0 (lean hub)
**Last updated:** 2026-05-01

> **Soli Deo Gloria.** A labor of love by a Reformed Baptist family.
> Hundreds of real people will use these recipes. **Accuracy beats speed.**

This repo contains **Granny Hudson's** recipe collection, split out from the
original Grandmasrecipes monorepo. Related repos: Grandmasrecipes, MomsRecipes,
Allrecipes.

---

## Quick Start (read first)

1. **Run `python scripts/image_safeguards.py status`** before reading ANY image.
2. **2000 px API limit.** Use `granny/processed/*.jpeg` for oversized originals.
3. **Every recipe MUST have `"collection": "granny"`.**
4. **Never invent** ingredients, steps, temperatures, times, or yields.
5. **Mark unclear text `[UNCLEAR]`** — add `[GUESS]` candidates with confidence levels.
6. **Run `python scripts/validate-recipes.py`** before committing.
7. **Privacy: this is family-only.** Never weaken `noindex` / `robots.txt`.

Decision priority: **accuracy → preservation → fidelity → readability**.

---

## Essential Reading

### Standards (extracted)

| File | What it covers |
|---|---|
| [`.claude/standards/OCR_STANDARDS.md`](.claude/standards/OCR_STANDARDS.md) | Character confusion, measurement standardization, dual-temperature format |
| [`.claude/standards/IMAGE_WORKFLOW.md`](.claude/standards/IMAGE_WORKFLOW.md) | 2000 px pre-flight, manifest, status values, recovery from dimension error |
| [`.claude/standards/FRAGMENT_HANDLING.md`](.claude/standards/FRAGMENT_HANDLING.md) | Source classification, completeness check, fragment / multi-page rules, screenshot handling |
| [`.claude/standards/RECIPE_SCHEMA.md`](.claude/standards/RECIPE_SCHEMA.md) | Full recipe JSON schema (conversions + nutrition + variants) |
| [`.claude/standards/CONVERSIONS.md`](.claude/standards/CONVERSIONS.md) | US ↔ metric tables, temperature conversions, JSON structure |
| [`.claude/standards/NUTRITION_QUESTIONS.md`](.claude/standards/NUTRITION_QUESTIONS.md) | Nutrition-blocker question format, default confidence levels |
| [`.claude/standards/DUPLICATE_HANDLING.md`](.claude/standards/DUPLICATE_HANDLING.md) | Exact / near / same-title rules, variant display |
| [`.claude/standards/BLOAT_MANAGEMENT.md`](.claude/standards/BLOAT_MANAGEMENT.md) | Image optimization (Q85), git history options |

---

## Repository Structure

```
Grannysrecipes/
├── CLAUDE.md                # This hub
├── README.md                # Public-facing overview
├── index.html / recipe.html # Static site
├── styles.css / script.js   # Site bundle
├── robots.txt               # BLOCKS ALL crawlers
├── .githooks/pre-commit     # Enforces noindex / no-sitemap rules
├── .claude/
│   └── standards/           # Extracted reference files (see above)
├── granny/                  # Granny Hudson's collection
│   ├── *.jpeg               # Original scans
│   ├── processed/           # AI-friendly resized copies (≤ 2000 px)
│   ├── recipes_master.json  # All recipes
│   ├── collections.json     # Collection metadata
│   ├── processed_images.json # Scan processing log
│   └── image_manifest.json  # Validation status & dimensions
├── Memorial/                # Tribute pages — do NOT publish without consent
├── scripts/
│   ├── validate-recipes.py
│   ├── process_images.py
│   ├── image_safeguards.py
│   ├── optimize_images.py
│   └── check-noindex.sh     # Privacy enforcement
└── ebook/                   # Print generation
```

---

## Privacy Posture

This is a **private family archive**:

- `robots.txt` blocks all search engines and AI crawlers.
- Every HTML file ships `noindex, nofollow`.
- No `sitemap.xml` is published.
- Family-name gate on the front end.

Enable the privacy enforcement hooks once after cloning:

```bash
git config core.hooksPath .githooks
```

The pre-commit hook verifies `robots.txt`, the absence of `sitemap.xml`, and
`noindex` on every HTML file.

For AI:

- Recipe content **may** be shared with external models for transcription help.
- Memorial content (people's names, photos, stories) **must not** be sent to
  external models. Process locally.

---

## Collection Configuration

```json
{
  "collections": {
    "granny": {
      "id": "granny",
      "display_name": "Granny Hudson",
      "folder": "granny/",
      "description": "Granny Hudson's family collection"
    }
  }
}
```

Rules:

1. Every recipe **must** have `"collection": "granny"`.
2. The website displays `collection_display` for user-friendly names.
3. All images live under `granny/`.

---

## Non-Negotiable Rules

1. Do NOT invent ingredients, steps, temperatures, times, or yields.
2. Mark unreadable / ambiguous text as `[UNCLEAR]`; provide 2–3 `[GUESS]` candidates.
3. Preserve original intent; normalize only spelling and formatting.
4. Keep family names and attributions (e.g., "Aunt Linda's Pound Cake").
5. Never discard a `image_refs` reference — even merged duplicates keep all refs.
6. Never read images >2000 px directly — use `granny/processed/`.
7. Never weaken privacy controls (`robots.txt`, `noindex`, no-sitemap).
8. Never publish memorial content without explicit family consent.

---

## Categories

`appetizers, beverages, breads, breakfast, desserts, mains, salads, sides, soups, snacks`

---

## Validation

```bash
# Recipes
python scripts/validate-recipes.py

# Privacy (also runs from pre-commit)
bash scripts/check-noindex.sh
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 2.0 | 2026-05-01 | Lean hub restructure. Extracted OCR / image / fragment / schema / conversions / nutrition / duplicate / bloat subfiles into `.claude/standards/`. CLAUDE.md cut from ~609 lines to ~145. |
| 1.x | 2026-01..03 | Original monolithic context file |

---

*"She looketh well to the ways of her household, and eateth not the bread of idleness."* — Proverbs 31:27
