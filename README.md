# Grandma's Recipe Archive

A treasured collection of family recipes, preserved with love.

> *Soli Deo Gloria*

---

## About This Project

This archive preserves Grandma's recipes—collected from handwritten cards, newspaper clippings, magazine cuttings, and other family treasures. The recipes span her journey from Michigan to Florida, representing both Northern and Southern culinary traditions.

**Current Status:** 5 unique recipes extracted from 6 scanned images

---

## Project Structure

```
Grandmasrecipes/
├── CLAUDE.md                  # AI assistant context & guidelines
├── README.md                  # This file
├── data/
│   ├── *.jpeg                 # Original scanned recipe images
│   ├── recipes_master.json    # All recipes in structured format
│   └── processed_images.json  # Scan processing log & metadata
├── site/
│   ├── index.html             # Home page with search & filters
│   ├── recipe.html            # Recipe detail page
│   ├── styles.css             # Stylesheet
│   └── script.js              # Client-side JavaScript
└── ebook/
    ├── book.html              # Print-optimized e-book HTML
    └── print.css              # Print stylesheet
```

---

## Quick Start

### View the Website Locally

1. **Using Python (recommended):**
   ```bash
   cd Grandmasrecipes
   python -m http.server 8000
   ```
   Then open http://localhost:8000/site/ in your browser.

2. **Using Node.js:**
   ```bash
   npx serve .
   ```

3. **Using PHP:**
   ```bash
   php -S localhost:8000
   ```

### Host on GitHub Pages

1. Push this repository to GitHub
2. Go to **Settings → Pages**
3. Set source to your main branch and `/site` folder (or root)
4. Your site will be live at `https://yourusername.github.io/Grandmasrecipes/site/`

### Host on Netlify

1. Push to GitHub/GitLab
2. Connect to Netlify
3. Set publish directory to `site`
4. Deploy!

### Host on Vercel

1. Push to GitHub
2. Import project in Vercel
3. Set output directory to `site`
4. Deploy!

---

## Generate PDF E-Book

### Method 1: Browser Print (Easiest)

1. Open `ebook/book.html` in your browser
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Select "Save as PDF" as the destination
4. Adjust margins to "None" or "Minimum"
5. Enable "Background graphics" for colors
6. Save

### Method 2: Using wkhtmltopdf

```bash
wkhtmltopdf \
  --enable-local-file-access \
  --page-size Letter \
  --margin-top 0.75in \
  --margin-bottom 0.75in \
  --margin-left 1in \
  --margin-right 1in \
  ebook/book.html grandmas-recipes.pdf
```

### Method 3: Using Pandoc

```bash
pandoc ebook/book.html \
  -o grandmas-recipes.pdf \
  --pdf-engine=wkhtmltopdf \
  --css=ebook/print.css
```

### Method 4: Using Calibre (for EPUB/MOBI)

1. Open Calibre
2. Add book → Select `ebook/book.html`
3. Convert book → Select output format (EPUB, MOBI, etc.)
4. Adjust settings as needed
5. Convert

---

## Adding New Recipes

### 1. Scan Your Recipe

- Scan at 300 DPI or higher
- Save as JPEG in `data/` folder
- Name format: `Grandmas-recipes - N.jpeg`

### 2. Extract the Recipe

Follow the workflow in `CLAUDE.md`:
1. Analyze the scan for orientation and content
2. Extract all recipe data following the JSON schema
3. Check for duplicates against existing recipes
4. Add to `recipes_master.json`
5. Update `processed_images.json`

### 3. Update the E-Book

Add the new recipe to `ebook/book.html`:
- Add to Table of Contents
- Add recipe in appropriate section
- Update the Index

---

## Recipe JSON Schema

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
  "confidence": {
    "overall": "high|medium|low",
    "flags": []
  },
  "image_refs": ["filename.jpeg"]
}
```

---

## Current Recipes

| Recipe | Category | Source | Confidence |
|--------|----------|--------|------------|
| Ginger-Onion Lo Mein | Mains | Magazine clipping | Medium* |
| Glazed Carrots | Sides | Tampa Tribune, 1994 | High |
| Jubilie Jumbles | Desserts | Typed card (Betty Crocker, 1955) | High |
| Original Chex Party Mix | Snacks | Cereal box | High |
| She's a Geisha Cocktail | Beverages | Izumi restaurant menu | High |

*\* Instructions partially inferred from standard technique*

---

## Known Issues & Flags

### Ginger-Onion Lo Mein
- Original clipping was cut off
- Steps 5-7 inferred from standard lo mein technique
- **If you find the original source, please update!**

### Jubilie Jumbles
- Original card showed "2 tsp" butter in glaze
- Corrected to "2 tbsp" per canonical Carnation recipe
- Spelling "Jubilie" preserved from original (may be "Jubilee")

---

## Recommended Tools for Future Processing

### OCR & Text Extraction
- **EasyOCR** - Good for messy scans
- **PaddleOCR** - Excellent for mixed layouts
- **Tesseract** - Gold standard open-source OCR

### Image Preprocessing
- **OpenCV** - Deskewing, denoising, contrast
- **unpaper** - Post-processing scanned pages
- **ScanTailor** - Batch processing with GUI

### E-Book Generation
- **Calibre** - Full-featured e-book management
- **Pandoc** - Universal document converter
- **ebooklib** - Python library for EPUB creation

---

## File Integrity

After modifying recipes, validate:

```bash
# Check JSON syntax
python -m json.tool data/recipes_master.json > /dev/null && echo "JSON valid"

# Check for required fields (basic)
python -c "
import json
with open('data/recipes_master.json') as f:
    data = json.load(f)
    for r in data['recipes']:
        assert 'id' in r, f'Missing id in {r.get(\"title\", \"unknown\")}'
        assert 'title' in r, f'Missing title in {r[\"id\"]}'
        assert 'ingredients' in r, f'Missing ingredients in {r[\"title\"]}'
        assert 'instructions' in r, f'Missing instructions in {r[\"title\"]}'
print('All recipes valid!')
"
```

---

## Contributing

This is a family project. If you're family and have:
- Additional scans of Grandma's recipes
- Corrections to existing recipes
- Memories or context about specific recipes

Please reach out!

---

## License

This recipe collection is a family treasure. Please use respectfully.

---

*"She looketh well to the ways of her household, and eateth not the bread of idleness."*
— Proverbs 31:27
