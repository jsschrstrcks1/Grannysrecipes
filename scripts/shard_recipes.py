#!/usr/bin/env python3
"""
Recipe Sharding Script for Granny's Recipe Archive

Creates category-based shards from recipes_master.json for improved
on-demand loading performance. Generates:
- recipes-index.json: Lightweight index with minimal recipe metadata
- recipes-{category}.json: Full recipe data per category

Usage:
    python scripts/shard_recipes.py [--dry-run]
"""

import json
import os
import sys
from pathlib import Path

# Configuration
SOURCE_FILE = 'granny/recipes_master.json'
OUTPUT_DIR = 'granny'


def create_shards(dry_run=False):
    """Create category-based recipe shards from master file."""

    # Load source recipes
    source_path = Path(SOURCE_FILE)
    if not source_path.exists():
        print(f"Error: Source file not found: {SOURCE_FILE}")
        sys.exit(1)

    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    recipes = data.get('recipes', [])
    meta = data.get('meta', {})

    if not recipes:
        print("Error: No recipes found in source file")
        sys.exit(1)

    print(f"Loaded {len(recipes)} recipes from {SOURCE_FILE}")

    # Group recipes by category
    by_category = {}
    for recipe in recipes:
        category = recipe.get('category', 'uncategorized')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(recipe)

    print(f"Found {len(by_category)} categories: {list(by_category.keys())}")

    # Create index with minimal metadata for fast initial load
    index_recipes = []
    for recipe in recipes:
        index_recipes.append({
            'id': recipe.get('id'),
            'title': recipe.get('title'),
            'category': recipe.get('category'),
            'tags': recipe.get('tags', []),
            'collection': recipe.get('collection'),
            'collection_display': recipe.get('collection_display'),
            'description': (recipe.get('description', '') or '')[:100],
            'servings_yield': recipe.get('servings_yield', ''),
            'total_time': recipe.get('total_time', '') or recipe.get('cook_time', ''),
            # Include variant info for grid filtering
            'variant_of': recipe.get('variant_of'),
            'canonical_id': recipe.get('canonical_id'),
        })

    # Build shard manifest
    shards = []
    for category, category_recipes in sorted(by_category.items()):
        shards.append({
            'category': category,
            'file': f'recipes-{category}.json',
            'count': len(category_recipes)
        })

    # Prepare index data
    index_data = {
        'meta': {
            **meta,
            'sharded': True,
            'shard_strategy': 'by_category',
            'total_recipes': len(recipes),
            'shard_count': len(shards)
        },
        'shards': shards,
        'recipes': index_recipes
    }

    if dry_run:
        print("\n[DRY RUN] Would create the following files:")
        print(f"  - {OUTPUT_DIR}/recipes-index.json ({len(index_recipes)} recipes)")
        for shard in shards:
            print(f"  - {OUTPUT_DIR}/{shard['file']} ({shard['count']} recipes)")
        print(f"\nTotal storage: 1 index + {len(shards)} category shards")
        return

    # Write index file
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    index_path = output_dir / 'recipes-index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)
    print(f"\nCreated: {index_path}")

    # Write category shard files
    for category, category_recipes in by_category.items():
        shard_data = {
            'meta': {
                'category': category,
                'count': len(category_recipes)
            },
            'recipes': category_recipes
        }

        shard_path = output_dir / f'recipes-{category}.json'
        with open(shard_path, 'w', encoding='utf-8') as f:
            json.dump(shard_data, f, indent=2)
        print(f"Created: {shard_path} ({len(category_recipes)} recipes)")

    print(f"\nSharding complete!")
    print(f"  - Index file: recipes-index.json")
    print(f"  - Category shards: {len(shards)} files")
    print(f"  - Total recipes: {len(recipes)}")


def main():
    dry_run = '--dry-run' in sys.argv
    create_shards(dry_run=dry_run)


if __name__ == '__main__':
    main()
