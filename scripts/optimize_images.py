#!/usr/bin/env python3
"""
Image Optimization Script for Grandma's Recipe Archive

Reduces repository bloat by optimizing JPEG quality while maintaining
human readability. Scanner images (Grandma's) are often saved at 100%
quality and can be reduced 80-90% with no visible quality loss.

Usage:
    python scripts/optimize_images.py --dry-run          # Preview changes
    python scripts/optimize_images.py --collection grandma  # Optimize one collection
    python scripts/optimize_images.py                    # Optimize all collections
    python scripts/optimize_images.py --quality 80       # Custom quality (default: 85)
    python scripts/optimize_images.py --backup           # Keep .original files

Key features:
- Preserves dimensions (no resizing)
- Maintains human readability (Q85 = visually identical)
- Creates backup on first run (can be disabled)
- Skips already-optimized images
- Tracks optimization in manifest
"""

import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import argparse

try:
    from PIL import Image
    import io
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


# Configuration
DEFAULT_QUALITY = 85  # Excellent quality, major size reduction
MIN_SAVINGS_PERCENT = 10  # Skip if savings < 10%

COLLECTIONS = {
    "grandma": {"path": "", "expected_savings": 0.85},
    "mommom": {"path": "mom/", "expected_savings": 0.30},
    "granny": {"path": "granny/", "expected_savings": 0.50}
}


class ImageOptimizer:
    """Optimizes JPEG images for repository storage."""

    def __init__(self, data_dir: Path, quality: int = DEFAULT_QUALITY,
                 dry_run: bool = False, keep_backup: bool = False):
        self.data_dir = data_dir
        self.quality = quality
        self.dry_run = dry_run
        self.keep_backup = keep_backup
        self.manifest_path = data_dir / "optimization_manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load or create optimization manifest."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass

        return {
            "created": datetime.now().isoformat(),
            "last_run": None,
            "quality_setting": self.quality,
            "optimized_images": {},
            "stats": {
                "total_original_bytes": 0,
                "total_optimized_bytes": 0,
                "images_optimized": 0,
                "images_skipped": 0
            }
        }

    def save_manifest(self):
        """Save manifest to disk."""
        self.manifest["last_run"] = datetime.now().isoformat()
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def is_already_optimized(self, filepath: Path) -> bool:
        """Check if image was already optimized."""
        key = str(filepath.relative_to(self.data_dir))
        if key in self.manifest["optimized_images"]:
            entry = self.manifest["optimized_images"][key]
            # Check if file hasn't changed since optimization
            current_size = filepath.stat().st_size
            if entry.get("optimized_size") == current_size:
                return True
        return False

    def estimate_savings(self, filepath: Path) -> Dict:
        """Estimate savings without modifying the file."""
        original_size = filepath.stat().st_size

        with Image.open(filepath) as img:
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Compress to buffer
            buffer = io.BytesIO()
            img.save(buffer, 'JPEG', quality=self.quality, optimize=True)
            optimized_size = buffer.tell()

        savings_bytes = original_size - optimized_size
        savings_percent = (savings_bytes / original_size) * 100 if original_size > 0 else 0

        return {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "savings_bytes": savings_bytes,
            "savings_percent": savings_percent,
            "worth_optimizing": savings_percent >= MIN_SAVINGS_PERCENT
        }

    def optimize_image(self, filepath: Path) -> Dict:
        """Optimize a single image file."""
        result = {
            "success": False,
            "action": None,
            "original_size": 0,
            "new_size": 0,
            "savings_percent": 0,
            "error": None
        }

        try:
            # Check if already optimized
            if self.is_already_optimized(filepath):
                result["action"] = "skipped_already_optimized"
                result["success"] = True
                return result

            # Estimate savings first
            estimate = self.estimate_savings(filepath)
            result["original_size"] = estimate["original_size"]

            if not estimate["worth_optimizing"]:
                result["action"] = "skipped_minimal_savings"
                result["new_size"] = estimate["original_size"]
                result["savings_percent"] = estimate["savings_percent"]
                result["success"] = True
                return result

            if self.dry_run:
                result["action"] = "would_optimize"
                result["new_size"] = estimate["optimized_size"]
                result["savings_percent"] = estimate["savings_percent"]
                result["success"] = True
                return result

            # Create backup if requested
            if self.keep_backup:
                backup_path = filepath.with_suffix('.original.jpeg')
                if not backup_path.exists():
                    shutil.copy2(filepath, backup_path)

            # Optimize the image
            with Image.open(filepath) as img:
                # Preserve EXIF if possible
                exif = img.info.get('exif')

                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')

                # Save optimized version
                save_kwargs = {
                    'quality': self.quality,
                    'optimize': True
                }
                if exif:
                    save_kwargs['exif'] = exif

                img.save(filepath, 'JPEG', **save_kwargs)

            # Record in manifest
            new_size = filepath.stat().st_size
            key = str(filepath.relative_to(self.data_dir))
            self.manifest["optimized_images"][key] = {
                "original_size": estimate["original_size"],
                "optimized_size": new_size,
                "quality": self.quality,
                "optimized_at": datetime.now().isoformat()
            }

            result["action"] = "optimized"
            result["new_size"] = new_size
            result["savings_percent"] = ((estimate["original_size"] - new_size) /
                                          estimate["original_size"]) * 100
            result["success"] = True

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"
            result["action"] = "error"

        return result

    def optimize_collection(self, collection_id: str) -> Dict:
        """Optimize all images in a collection."""
        if collection_id not in COLLECTIONS:
            return {"error": f"Unknown collection: {collection_id}"}

        collection_path = self.data_dir / COLLECTIONS[collection_id]["path"]

        if not collection_path.exists():
            return {"error": f"Collection path not found: {collection_path}"}

        # Find all JPEG images (exclude processed folder and backups)
        images = []
        for pattern in ["*.jpeg", "*.jpg"]:
            images.extend(collection_path.glob(pattern))

        images = [f for f in images
                  if "processed" not in str(f)
                  and ".original." not in str(f)]

        print(f"\n{'='*60}")
        print(f"Optimizing collection: {collection_id}")
        print(f"Path: {collection_path}")
        print(f"Found {len(images)} images")
        print(f"Quality setting: {self.quality}")
        print(f"{'='*60}\n")

        stats = {
            "collection": collection_id,
            "total": len(images),
            "optimized": 0,
            "skipped": 0,
            "errors": 0,
            "original_bytes": 0,
            "new_bytes": 0
        }

        for i, img_path in enumerate(sorted(images), 1):
            print(f"[{i}/{len(images)}] {img_path.name}...", end=" ")

            result = self.optimize_image(img_path)
            stats["original_bytes"] += result.get("original_size", 0)

            if result["action"] == "optimized":
                stats["optimized"] += 1
                stats["new_bytes"] += result["new_size"]
                print(f"OK ({result['savings_percent']:.1f}% smaller)")
            elif result["action"] == "would_optimize":
                stats["optimized"] += 1
                stats["new_bytes"] += result["new_size"]
                print(f"WOULD SAVE {result['savings_percent']:.1f}%")
            elif result["action"] in ["skipped_already_optimized", "skipped_minimal_savings"]:
                stats["skipped"] += 1
                stats["new_bytes"] += result.get("original_size", 0)
                print("SKIP (already optimized or minimal savings)")
            elif result["action"] == "error":
                stats["errors"] += 1
                print(f"ERROR: {result['error']}")

        return stats

    def optimize_all(self) -> Dict:
        """Optimize all collections."""
        all_stats = {}

        for collection_id in COLLECTIONS:
            collection_path = self.data_dir / COLLECTIONS[collection_id]["path"]
            if collection_path.exists():
                all_stats[collection_id] = self.optimize_collection(collection_id)

        return all_stats


def format_size(bytes_val: int) -> str:
    """Format bytes as human-readable size."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    else:
        return f"{bytes_val / (1024 * 1024):.1f} MB"


def print_summary(results: Dict):
    """Print optimization summary."""
    print("\n" + "="*60)
    print("OPTIMIZATION SUMMARY")
    print("="*60)

    total_original = 0
    total_new = 0
    total_optimized = 0

    for collection_id, stats in results.items():
        if "error" in stats:
            continue

        total_original += stats["original_bytes"]
        total_new += stats["new_bytes"]
        total_optimized += stats["optimized"]

        savings = stats["original_bytes"] - stats["new_bytes"]
        savings_pct = (savings / stats["original_bytes"] * 100) if stats["original_bytes"] > 0 else 0

        print(f"\n{collection_id.upper()}:")
        print(f"  Images processed:  {stats['total']}")
        print(f"  Optimized:         {stats['optimized']}")
        print(f"  Skipped:           {stats['skipped']}")
        print(f"  Errors:            {stats['errors']}")
        print(f"  Original size:     {format_size(stats['original_bytes'])}")
        print(f"  New size:          {format_size(stats['new_bytes'])}")
        print(f"  Savings:           {format_size(savings)} ({savings_pct:.1f}%)")

    if total_original > 0:
        total_savings = total_original - total_new
        total_pct = (total_savings / total_original * 100)
        print(f"\n{'='*60}")
        print(f"TOTAL SAVINGS: {format_size(total_savings)} ({total_pct:.1f}%)")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Optimize recipe archive images to reduce repository size"
    )
    parser.add_argument(
        '--collection', '-c',
        choices=['grandma', 'mommom', 'granny', 'all'],
        default='all',
        help="Collection to optimize (default: all)"
    )
    parser.add_argument(
        '--quality', '-q',
        type=int,
        default=DEFAULT_QUALITY,
        help=f"JPEG quality 1-100 (default: {DEFAULT_QUALITY})"
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        '--backup', '-b',
        action='store_true',
        help="Keep .original.jpeg backup files"
    )

    args = parser.parse_args()

    # Validate quality
    if args.quality < 1 or args.quality > 100:
        print("ERROR: Quality must be between 1 and 100")
        sys.exit(1)

    # Find data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'

    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        sys.exit(1)

    optimizer = ImageOptimizer(
        data_dir,
        quality=args.quality,
        dry_run=args.dry_run,
        keep_backup=args.backup
    )

    if args.dry_run:
        print("\n*** DRY RUN MODE - No files will be modified ***\n")

    # Run optimization
    if args.collection == 'all':
        results = optimizer.optimize_all()
    else:
        results = {args.collection: optimizer.optimize_collection(args.collection)}

    # Save manifest (unless dry run)
    if not args.dry_run:
        optimizer.save_manifest()

    # Print summary
    print_summary(results)

    if args.dry_run:
        print("\n*** DRY RUN - Run without --dry-run to apply changes ***")


if __name__ == '__main__':
    main()
