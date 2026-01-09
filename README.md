# Granny Hudson's Recipe Archive

A treasured collection of family recipes, preserved with love.

> *Soli Deo Gloria*

---

## About This Project

This archive preserves Granny Hudson's recipes—collected from handwritten cards, newspaper clippings, magazine cuttings, and other family treasures.

This repository is part of a family recipe preservation project, split from the main Grandmasrecipes repository for better organization.

**Related repositories:**
- **Grandmasrecipes** - Main repository (Grandma Baker's collection)
- **Grannysrecipes** - This repository (Granny Hudson's collection)

---

## Project Structure

```
Grannysrecipes/
├── CLAUDE.md                  # AI assistant context & guidelines
├── README.md                  # This file
├── index.html                 # Home page with search & filters
├── recipe.html                # Recipe detail page
├── styles.css                 # Stylesheet
├── script.js                  # Client-side JavaScript
├── robots.txt                 # Search engine directives
├── granny/                    # Granny Hudson's recipe collection
│   ├── *.jpeg                 # Original scanned recipe images
│   ├── processed/             # AI-friendly resized versions (if needed)
│   ├── recipes_master.json    # All recipes in structured format
│   └── processed_images.json  # Scan processing log & metadata
├── scripts/                   # Utility scripts
│   ├── validate-recipes.py    # Recipe validation
│   ├── process_images.py      # Image resizing
│   ├── image_safeguards.py    # Image validation
│   └── optimize_images.py     # JPEG optimization
└── ebook/
    ├── book.html              # Print-optimized e-book HTML
    └── print.css              # Print stylesheet
```

---

## Quick Start

### View the Website Locally

1. **Using Python (recommended):**
   ```bash
   cd Grannysrecipes
   python -m http.server 8000
   ```
   Then open http://localhost:8000/ in your browser.

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
3. Set source to your main branch and root folder
4. Your site will be live at `https://yourusername.github.io/Grannysrecipes/`

### Host on Netlify

1. Push to GitHub/GitLab
2. Connect to Netlify
3. Set publish directory to root
4. Deploy!

### Host on Vercel

1. Push to GitHub
2. Import project in Vercel
3. Deploy!

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
- Save as JPEG in `granny/` folder
- Recommended naming: descriptive or numbered (e.g., `recipe-name.jpeg` or `101 Medium.jpeg`)

### 2. Extract the Recipe

Follow the workflow in `CLAUDE.md`:
1. Analyze the scan for orientation and content
2. Extract all recipe data following the JSON schema
3. Check for duplicates against existing recipes
4. Add to `granny/recipes_master.json`
5. Update `granny/processed_images.json`

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

## Current Status

Recipe extraction from Granny Hudson's collection is in progress. Check `granny/recipes_master.json` for the current list of extracted recipes.

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
python -m json.tool granny/recipes_master.json > /dev/null && echo "JSON valid"

# Use the validation script
python scripts/validate-recipes.py
```

---

## Contributing

This is a family project. If you're family and have:
- Additional scans of Granny Hudson's recipes
- Corrections to existing recipes
- Memories or context about specific recipes

Please reach out!

---

## License

This recipe collection is a family treasure. Please use respectfully.

---

*"She looketh well to the ways of her household, and eateth not the bread of idleness."*
— Proverbs 31:27
