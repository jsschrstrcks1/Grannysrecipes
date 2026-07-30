# Granny Hudson's Recipe Archive

A treasured collection of family recipes from Granny Hudson — preserved
with love, kept private to family, and packaged as both a static website
and a printable e-book.

> *Soli Deo Gloria.*

---

## Table of Contents

- [About this project](#about-this-project)
- [Family Recipe Archive (multi-repo)](#family-recipe-archive-multi-repo)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Privacy & anti-indexing](#privacy--anti-indexing)
- [Memorial section](#memorial-section)
- [Generate the e-book / PDF](#generate-the-e-book--pdf)
- [Adding new recipes](#adding-new-recipes)
- [Recipe JSON schema](#recipe-json-schema)
- [Validation](#validation)
- [Recommended tools](#recommended-tools-for-future-processing)
- [Multi-LLM integration](#multi-llm-integration)
- [Contributing](#contributing)
- [License](#license)

---

## About this project

This archive preserves Granny Hudson's recipes — collected from
handwritten cards, newspaper clippings, magazine cuttings, and other
family treasures. Granny's life ran from Florida to Boston and back, and
her recipes carry the marks of both.

This is a **private family archive**. Unlike the other recipe repos in
the family, this site is intentionally hidden from search engines and
AI crawlers. See [Privacy & anti-indexing](#privacy--anti-indexing).

This repository is part of a family recipe preservation project, split
from the main Grandmasrecipes repository for better organization.

---

## Family Recipe Archive (multi-repo)

| Repo | Collection |
|---|---|
| [MomsRecipes](https://github.com/jsschrstrcks1/MomsRecipes) | MomMom Baker (heirloom recipes) |
| [Grandmasrecipes](https://github.com/jsschrstrcks1/Grandmasrecipes) | Grandma Baker (Michigan → Florida) |
| **Grannysrecipes** | **Granny Hudson (Florida → Boston → back)** *(this repo)* |
| [Allrecipes](https://github.com/jsschrstrcks1/Allrecipes) | Reference cookbooks & magazines |

---

## Project structure

```
Grannysrecipes/
├── CLAUDE.md                  # AI assistant context
├── OVERLOOKED_TIPS_REPORT.md  # Audit of "tips that should have been captured"
├── README.md                  # This file
├── index.html                 # Home page with search & filters
├── recipe.html                # Recipe detail page
├── styles.css                 # Stylesheet
├── script.js                  # Client-side JavaScript
├── robots.txt                 # Search-engine directives (BLOCKS ALL)
├── granny/                    # Granny Hudson's recipe collection — NOTE: this repo's data
│                              #   lives HERE, not in data/ like every sibling repo. Deployed
│                              #   consumers pin these URLs; see data/README.md before "fixing".
│   ├── *.jpeg                 # Original scanned recipe images
│   ├── processed/             # AI-friendly resized versions (if needed)
│   ├── recipes_master.json    # All recipes
│   └── processed_images.json  # Scan processing log & metadata
├── Memorial/                  # Tribute pages (see "Memorial section")
├── scripts/                   # Validation, image processing, privacy checks
│   ├── validate-recipes.py
│   ├── process_images.py
│   ├── image_safeguards.py
│   ├── optimize_images.py
│   └── check-noindex.sh       # Privacy enforcement
├── .githooks/
│   └── pre-commit             # Enforces noindex / no-sitemap rules
└── ebook/
    ├── book.html              # Print-optimized e-book
    └── print.css              # Print stylesheet
```

---

## Quick start

### View the site locally

```bash
# Python (recommended)
cd Grannysrecipes
python -m http.server 8000

# or Node.js
npx serve .

# or PHP
php -S localhost:8000
```

Open <http://localhost:8000>.

### Host on GitHub Pages / Netlify / Vercel

Pure static. **Before publishing, double-check the privacy controls
below — this archive is family-only.**

---

## Privacy & anti-indexing

This is a **private family recipe archive**. Several controls work
together to keep it out of search engines and AI crawlers:

- **`robots.txt`** — blocks all search engines and AI crawlers.
- **Meta tags** — every HTML file includes `noindex, nofollow`.
- **No `sitemap.xml`** — intentionally absent.
- **Family-name gate** — a simple authentication step on the front end.

### Required developer setup

After cloning, enable the privacy-enforcing git hooks **once**:

```bash
git config core.hooksPath .githooks
```

The pre-commit hook verifies before every commit that:

1. `robots.txt` blocks all crawlers.
2. No `sitemap.xml` exists.
3. Every HTML file has the `noindex` meta tag.

Run the check manually any time:

```bash
bash scripts/check-noindex.sh
```

### If you fork this repository

Please maintain the privacy protections. These are real family recipes
shared among relatives — not intended for public discovery.

---

## Memorial section

The `Memorial/` directory holds tribute pages: photos, stories, and the
memories tied to specific recipes. Treat memorial content with the same
care as the recipes themselves — preserve voice, never embellish, and
never publish a memorial page without the family's explicit consent.

The `OVERLOOKED_TIPS_REPORT.md` audit captures small notes ("Granny
always added a pinch of nutmeg") that originally lived only in family
memory. New tips go through the same validation as recipes.

---

## Generate the e-book / PDF

#### Browser print (easiest)

1. Open `ebook/book.html` in a browser.
2. `Ctrl+P` (or `Cmd+P`) → "Save as PDF".
3. Set margins to "None" or "Minimum"; enable "Background graphics".

#### `wkhtmltopdf`

```bash
wkhtmltopdf \
  --enable-local-file-access \
  --page-size Letter \
  --margin-top 0.75in --margin-bottom 0.75in \
  --margin-left 1in --margin-right 1in \
  ebook/book.html grannys-recipes.pdf
```

#### Pandoc

```bash
pandoc ebook/book.html \
  -o grannys-recipes.pdf \
  --pdf-engine=wkhtmltopdf \
  --css=ebook/print.css
```

#### Calibre (EPUB / MOBI)

Add `ebook/book.html` to Calibre, "Convert book", choose your format.

---

## Adding new recipes

1. **Scan** at 300 DPI or higher; save as JPEG in `granny/`.
2. **Extract** following [`CLAUDE.md`](CLAUDE.md):
   - Analyze the scan for orientation and content.
   - Extract recipe data per the JSON schema.
   - Check for duplicates against existing recipes.
   - Append to `granny/recipes_master.json`.
   - Update `granny/processed_images.json`.
3. **Update the e-book** (`ebook/book.html`):
   - Add to Table of Contents.
   - Insert the recipe in the appropriate section.
   - Update the Index.
4. **Validate** (see below) and commit. The pre-commit hook re-runs the
   privacy check; if it fails, **fix the underlying file** rather than
   bypassing the hook.

---

## Recipe JSON schema

```json
{
  "id": "recipe-slug",
  "title": "Recipe Title",
  "attribution": "Source/Author",
  "source_note": "Where it came from",
  "description": "Brief description",
  "category": "desserts|mains|sides|etc",
  "servings_yield": "4 servings",
  "prep_time": "15 minutes",
  "cook_time": "30 minutes",
  "total_time": "45 minutes",
  "ingredients": [
    {"item": "flour", "quantity": "2", "unit": "cups", "prep_note": "sifted"}
  ],
  "instructions": [
    {"step": 1, "text": "Preheat oven to 350°F."}
  ],
  "temperature": "350°F (175°C)",
  "pan_size": "9x13 inch pan",
  "notes": ["Any additional notes"],
  "tags": ["dessert", "holiday", "vintage"],
  "confidence": {"overall": "high|medium|low", "flags": []},
  "image_refs": ["filename.jpeg"]
}
```

---

## Validation

```bash
# JSON syntax
python -m json.tool granny/recipes_master.json > /dev/null && echo "JSON valid"

# Full validation
python scripts/validate-recipes.py

# Privacy check (also runs from pre-commit hook)
bash scripts/check-noindex.sh
```

The validator enforces required fields, slug uniqueness, image
references, and category vocabulary. The privacy check enforces the
anti-indexing rules.

---

## Recommended tools for future processing

- **OCR:** EasyOCR, PaddleOCR, Tesseract.
- **Image preprocessing:** OpenCV, unpaper, ScanTailor.
- **E-book generation:** Calibre, Pandoc, ebooklib.

---

## Multi-LLM integration

Defaults to **`recipe` mode** in the multi-LLM orchestrator hosted in
[ken](https://github.com/jsschrstrcks1/ken).

| Skill | Usage |
|---|---|
| `/consult gpt structure "..."` | Quick second opinion |
| `/orchestrate recipe "<task>"` | Full pipeline: transcribe → validate → integrate |
| Cognitive memory | Scope `/Grannysrecipes` |

The `recipe-transcription` and `recipe-validation` skills are designed
for messy handwriting and partial text. They never invent steps —
anything inferred is flagged.

#### Setup (per session)

```bash
pip3 install -q -r /home/user/ken/orchestrator/requirements.txt
```

#### Privacy posture for AI assistants

- Recipe content **may** be shared with AI models for transcription
  help.
- Memorial content (people's names, photos, stories) **must not** be
  sent to external models. Process it locally.

---

## Contributing

This is a family project. If you're family and have:

- Additional scans of Granny Hudson's recipes
- Corrections to existing recipes
- Memories or context about specific recipes

Please reach out. If you fork, **keep the privacy protections.**

---

## License

This recipe collection is a family treasure. Please use respectfully.
The site source is published under [`LICENSE`](LICENSE) (GNU AGPL v3);
recipe text, photos, and memorial content are family-private and not
licensed for commercial reuse or republication.

---

*"She looketh well to the ways of her household, and eateth not the
bread of idleness." — Proverbs 31:27*
