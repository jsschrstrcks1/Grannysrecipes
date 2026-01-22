#!/usr/bin/env python3
"""
Ingredient Index Builder for Granny Hudson's Recipe Archive

Creates a pre-compiled ingredient search index from recipes_master.json.
Generates granny/ingredient-index.json for fast ingredient-based recipe lookup.

Usage:
    python scripts/build-ingredient-index.py [--dry-run]
"""

import json
import re
import sys
from pathlib import Path

# Configuration
SOURCE_FILE = 'granny/recipes_master.json'
OUTPUT_FILE = 'granny/ingredient-index.json'


def normalize_ingredient(item: str) -> str:
    """Normalize ingredient name to a consistent key format."""
    # Lowercase and strip
    normalized = item.lower().strip()

    # Remove common descriptors that don't affect the core ingredient
    descriptors = [
        r'\bfresh\b', r'\bfrozen\b', r'\bcanned\b', r'\bdried\b',
        r'\bminced\b', r'\bchopped\b', r'\bdiced\b', r'\bsliced\b',
        r'\bshredded\b', r'\bgrated\b', r'\bmelted\b', r'\bsoftened\b',
        r'\broom temperature\b', r'\bcold\b', r'\bwarm\b', r'\bhot\b',
        r'\bcooked\b', r'\buncooked\b', r'\braw\b',
        r'\bfinely\b', r'\bcoarsely\b', r'\broughly\b',
        r'\bsmall\b', r'\bmedium\b', r'\blarge\b',
        r'\bthin\b', r'\bthick\b',
    ]

    for desc in descriptors:
        normalized = re.sub(desc, '', normalized)

    # Remove parenthetical notes
    normalized = re.sub(r'\([^)]*\)', '', normalized)

    # Clean up whitespace and punctuation
    normalized = re.sub(r'[,;:]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    # Convert to slug format for keys
    slug = re.sub(r'[^a-z0-9\s]', '', normalized)
    slug = re.sub(r'\s+', '-', slug).strip('-')

    return slug


def build_index(dry_run=False):
    """Build ingredient index from recipes master file."""
    source_path = Path(SOURCE_FILE)

    if not source_path.exists():
        print(f"Error: Source file not found: {SOURCE_FILE}")
        sys.exit(1)

    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = data.get('recipes', [])

    if not recipes:
        print("Error: No recipes found in source file")
        sys.exit(1)

    print(f"Loaded {len(recipes)} recipes from {SOURCE_FILE}")

    # Build ingredient -> recipe_ids mapping
    ingredient_index = {}

    for recipe in recipes:
        recipe_id = recipe.get('id')
        if not recipe_id:
            continue

        ingredients = recipe.get('ingredients', [])

        for ing in ingredients:
            item = ing.get('item', '')
            if not item:
                continue

            # Normalize the ingredient name
            key = normalize_ingredient(item)
            if not key:
                continue

            # Add recipe to this ingredient's list
            if key not in ingredient_index:
                ingredient_index[key] = []

            if recipe_id not in ingredient_index[key]:
                ingredient_index[key].append(recipe_id)

    # Sort recipe lists for consistency
    for key in ingredient_index:
        ingredient_index[key].sort()

    # Sort ingredients alphabetically
    sorted_index = dict(sorted(ingredient_index.items()))

    # Build output data
    output_data = {
        "meta": {
            "version": "1.0.0",
            "description": "Pre-compiled ingredient search index for Granny Hudson's Kitchen",
            "total_ingredients": len(sorted_index),
            "total_recipes_indexed": len(recipes)
        },
        "ingredients": sorted_index
    }

    if dry_run:
        print(f"\n[DRY RUN] Would create: {OUTPUT_FILE}")
        print(f"  - {len(sorted_index)} unique ingredients")
        print(f"  - {len(recipes)} recipes indexed")

        # Show sample
        sample_keys = list(sorted_index.keys())[:5]
        print("\nSample ingredients:")
        for key in sample_keys:
            print(f"  - {key}: {len(sorted_index[key])} recipes")
        return

    # Write output file
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nCreated: {OUTPUT_FILE}")
    print(f"  - {len(sorted_index)} unique ingredients")
    print(f"  - {len(recipes)} recipes indexed")


def main():
    dry_run = '--dry-run' in sys.argv
    build_index(dry_run=dry_run)


if __name__ == '__main__':
    main()
