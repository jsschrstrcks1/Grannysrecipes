#!/usr/bin/env python3
"""
Image Processing Script for Grandma's Recipe Archive

Handles:
1. Images larger than 2000px in any dimension (resizes for AI processing)
2. Broken/corrupted images (validates and logs errors)
3. Batch processing with progress tracking
4. Non-destructive processing (creates optimized copies)

Usage:
    python scripts/process_images.py                    # Process all collections
    python scripts/process_images.py --collection mom   # Process MomMom's images only
    python scripts/process_images.py --dry-run          # Preview without changes
    python scripts/process_images.py --fix-broken       # Attempt recovery of broken images
"""

import json
import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import argparse

try:
    from PIL import Image, ImageFile, ExifTags
    # Allow loading truncated images for recovery attempts
    ImageFile.LOAD_TRUNCATED_IMAGES = True
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


# Configuration
MAX_DIMENSION = 2000  # Maximum pixels in any dimension
JPEG_QUALITY = 92     # Quality for resized images (high quality for OCR)
PROCESSED_FOLDER = "processed"  # Subfolder for resized images

# Collection paths relative to data/
COLLECTIONS = {
    "grandma": "",           # data/*.jpeg
    "mommom": "mom/",        # data/mom/*.jpeg
    "granny": "granny/",     # data/granny/*.jpeg (future)
    "reference": "all/"      # data/all/*.PNG (Kindle screenshots)
}


class ImageProcessor:
    """Handles image validation, resizing, and error recovery."""

    def __init__(self, data_dir: Path, dry_run: bool = False):
        self.data_dir = data_dir
        self.dry_run = dry_run
        self.results = {
            "processed": [],
            "skipped": [],
            "errors": [],
            "resized": []
        }

    def validate_image(self, image_path: Path) -> Dict:
        """
        Validate an image file and return detailed status.

        Returns dict with:
            - valid: bool
            - error: str (if invalid)
            - width: int
            - height: int
            - needs_resize: bool
            - format: str
            - file_size: int
            - recoverable: bool (if corrupted but partially readable)
        """
        result = {
            "valid": False,
            "error": None,
            "width": None,
            "height": None,
            "needs_resize": False,
            "format": None,
            "file_size": 0,
            "recoverable": False,
            "orientation": None
        }

        try:
            result["file_size"] = image_path.stat().st_size

            if result["file_size"] == 0:
                result["error"] = "Empty file (0 bytes)"
                return result

        except OSError as e:
            result["error"] = f"Cannot access file: {e}"
            return result

        try:
            with Image.open(image_path) as img:
                # Try to load the image data (catches truncated files)
                img.load()

                result["width"] = img.width
                result["height"] = img.height
                result["format"] = img.format
                result["valid"] = True
                result["needs_resize"] = (
                    img.width > MAX_DIMENSION or img.height > MAX_DIMENSION
                )

                # Extract EXIF orientation if present
                try:
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            if ExifTags.TAGS.get(tag) == 'Orientation':
                                result["orientation"] = value
                                break
                except Exception:
                    pass  # EXIF reading failed, not critical

        except Image.UnidentifiedImageError:
            result["error"] = "Unrecognized image format"
            # Try to detect if it's a known format with corruption
            result["recoverable"] = self._check_recoverable(image_path)

        except OSError as e:
            error_str = str(e).lower()
            if "truncated" in error_str or "corrupt" in error_str:
                result["error"] = f"Corrupted image: {e}"
                result["recoverable"] = True
            else:
                result["error"] = f"Cannot read image: {e}"

        except Exception as e:
            result["error"] = f"Unexpected error: {type(e).__name__}: {e}"

        return result

    def _check_recoverable(self, image_path: Path) -> bool:
        """Check if a corrupted image might be partially recoverable."""
        try:
            with open(image_path, 'rb') as f:
                header = f.read(12)
                # JPEG magic bytes
                if header[:2] == b'\xff\xd8':
                    return True
                # PNG magic bytes
                if header[:8] == b'\x89PNG\r\n\x1a\n':
                    return True
        except Exception:
            pass
        return False

    def resize_image(self, image_path: Path, output_path: Path) -> Dict:
        """
        Resize an image to fit within MAX_DIMENSION while preserving aspect ratio.

        Returns dict with status and details.
        """
        result = {
            "success": False,
            "original_size": None,
            "new_size": None,
            "error": None
        }

        try:
            with Image.open(image_path) as img:
                result["original_size"] = (img.width, img.height)

                # Handle EXIF orientation
                try:
                    exif = img._getexif()
                    if exif:
                        for tag, value in exif.items():
                            if ExifTags.TAGS.get(tag) == 'Orientation':
                                if value == 3:
                                    img = img.rotate(180, expand=True)
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                                break
                except Exception:
                    pass  # EXIF handling failed, continue with original orientation

                # Calculate new dimensions
                ratio = min(MAX_DIMENSION / img.width, MAX_DIMENSION / img.height)
                if ratio < 1:
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)

                    # High-quality downscaling for OCR readability
                    img_resized = img.resize(
                        (new_width, new_height),
                        Image.Resampling.LANCZOS
                    )
                    result["new_size"] = (new_width, new_height)
                else:
                    # Image doesn't need resizing, just copy
                    img_resized = img.copy()
                    result["new_size"] = result["original_size"]

                if not self.dry_run:
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # Convert RGBA to RGB for JPEG
                    if img_resized.mode in ('RGBA', 'P'):
                        img_resized = img_resized.convert('RGB')

                    img_resized.save(output_path, 'JPEG', quality=JPEG_QUALITY)

                result["success"] = True

        except Exception as e:
            result["error"] = f"{type(e).__name__}: {e}"

        return result

    def attempt_recovery(self, image_path: Path, output_path: Path) -> Dict:
        """
        Attempt to recover a partially corrupted image.

        Uses LOAD_TRUNCATED_IMAGES to salvage what we can.
        """
        result = {
            "success": False,
            "recovered_size": None,
            "error": None,
            "data_loss": False
        }

        try:
            # ImageFile.LOAD_TRUNCATED_IMAGES is already True
            with Image.open(image_path) as img:
                try:
                    img.load()
                except Exception as e:
                    result["data_loss"] = True
                    # Continue anyway - we may have partial data

                if img.width > 0 and img.height > 0:
                    result["recovered_size"] = (img.width, img.height)

                    if not self.dry_run:
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')

                        img.save(output_path, 'JPEG', quality=JPEG_QUALITY)

                    result["success"] = True
                else:
                    result["error"] = "No recoverable image data"

        except Exception as e:
            result["error"] = f"Recovery failed: {type(e).__name__}: {e}"

        return result

    def get_file_hash(self, filepath: Path) -> str:
        """Generate MD5 hash for duplicate detection."""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def process_collection(self, collection_id: str) -> Dict:
        """Process all images in a collection."""
        if collection_id not in COLLECTIONS:
            return {"error": f"Unknown collection: {collection_id}"}

        collection_path = self.data_dir / COLLECTIONS[collection_id]
        processed_path = collection_path / PROCESSED_FOLDER

        if not collection_path.exists():
            return {"error": f"Collection path not found: {collection_path}"}

        # Find all image files (JPEG and PNG)
        image_files = (list(collection_path.glob("*.jpeg")) +
                       list(collection_path.glob("*.jpg")) +
                       list(collection_path.glob("*.png")) +
                       list(collection_path.glob("*.PNG")))
        image_files = [f for f in image_files if PROCESSED_FOLDER not in str(f)]

        print(f"\n{'='*60}")
        print(f"Processing collection: {collection_id}")
        print(f"Path: {collection_path}")
        print(f"Found {len(image_files)} images")
        print(f"{'='*60}\n")

        results = {
            "collection": collection_id,
            "total": len(image_files),
            "valid": 0,
            "resized": 0,
            "skipped": 0,
            "errors": [],
            "details": []
        }

        for i, image_file in enumerate(sorted(image_files), 1):
            print(f"[{i}/{len(image_files)}] {image_file.name}...", end=" ")

            # Validate
            validation = self.validate_image(image_file)

            detail = {
                "filename": image_file.name,
                "validation": validation,
                "action": None,
                "result": None
            }

            if not validation["valid"]:
                print(f"ERROR: {validation['error']}")
                results["errors"].append({
                    "file": image_file.name,
                    "error": validation["error"],
                    "recoverable": validation["recoverable"]
                })
                detail["action"] = "error"

            elif validation["needs_resize"]:
                print(f"RESIZING ({validation['width']}x{validation['height']})...", end=" ")

                output_file = processed_path / image_file.name
                resize_result = self.resize_image(image_file, output_file)

                if resize_result["success"]:
                    results["resized"] += 1
                    results["valid"] += 1
                    print(f"OK -> {resize_result['new_size'][0]}x{resize_result['new_size'][1]}")
                    detail["action"] = "resized"
                    detail["result"] = resize_result
                else:
                    print(f"FAILED: {resize_result['error']}")
                    results["errors"].append({
                        "file": image_file.name,
                        "error": f"Resize failed: {resize_result['error']}"
                    })
                    detail["action"] = "resize_failed"
                    detail["result"] = resize_result
            else:
                results["valid"] += 1
                results["skipped"] += 1
                print(f"OK ({validation['width']}x{validation['height']}, no resize needed)")
                detail["action"] = "skipped"

            results["details"].append(detail)

        return results

    def process_all_collections(self) -> Dict:
        """Process all configured collections."""
        all_results = {}

        for collection_id in COLLECTIONS:
            collection_path = self.data_dir / COLLECTIONS[collection_id]
            if collection_path.exists():
                all_results[collection_id] = self.process_collection(collection_id)

        return all_results


def generate_processing_log(results: Dict, output_path: Path):
    """Generate a JSON log of processing results."""
    log = {
        "processing_date": datetime.now().isoformat(),
        "max_dimension": MAX_DIMENSION,
        "jpeg_quality": JPEG_QUALITY,
        "collections": results
    }

    # Calculate summary
    total_processed = 0
    total_resized = 0
    total_errors = 0

    for collection_results in results.values():
        if isinstance(collection_results, dict) and "total" in collection_results:
            total_processed += collection_results.get("valid", 0)
            total_resized += collection_results.get("resized", 0)
            total_errors += len(collection_results.get("errors", []))

    log["summary"] = {
        "total_processed": total_processed,
        "total_resized": total_resized,
        "total_errors": total_errors
    }

    with open(output_path, 'w') as f:
        json.dump(log, f, indent=2)

    print(f"\nProcessing log saved to: {output_path}")


def print_summary(results: Dict):
    """Print a summary of processing results."""
    print("\n" + "="*60)
    print("PROCESSING SUMMARY")
    print("="*60)

    for collection_id, collection_results in results.items():
        if isinstance(collection_results, dict) and "error" not in collection_results:
            print(f"\n{collection_id.upper()}:")
            print(f"  Total images:  {collection_results['total']}")
            print(f"  Valid:         {collection_results['valid']}")
            print(f"  Resized:       {collection_results['resized']}")
            print(f"  Skipped:       {collection_results['skipped']}")
            print(f"  Errors:        {len(collection_results['errors'])}")

            if collection_results['errors']:
                print("\n  ERRORS:")
                for err in collection_results['errors'][:5]:  # Show first 5
                    print(f"    - {err['file']}: {err['error']}")
                if len(collection_results['errors']) > 5:
                    print(f"    ... and {len(collection_results['errors']) - 5} more")


def main():
    parser = argparse.ArgumentParser(
        description="Process recipe archive images for AI-friendly dimensions"
    )
    parser.add_argument(
        '--collection', '-c',
        choices=['grandma', 'mommom', 'granny', 'reference', 'all'],
        default='all',
        help="Collection to process (default: all)"
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help="Preview changes without modifying files"
    )
    parser.add_argument(
        '--fix-broken',
        action='store_true',
        help="Attempt to recover broken/corrupted images"
    )

    args = parser.parse_args()

    # Find data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'

    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        sys.exit(1)

    processor = ImageProcessor(data_dir, dry_run=args.dry_run)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No files will be modified ***\n")

    # Process collections
    if args.collection == 'all':
        results = processor.process_all_collections()
    else:
        results = {args.collection: processor.process_collection(args.collection)}

    # Print summary
    print_summary(results)

    # Save log
    if not args.dry_run:
        log_path = data_dir / f"processing_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        generate_processing_log(results, log_path)

    # Exit with error code if there were failures
    total_errors = sum(
        len(r.get('errors', []))
        for r in results.values()
        if isinstance(r, dict)
    )

    if total_errors > 0:
        print(f"\n⚠ Completed with {total_errors} error(s)")
        sys.exit(1)
    else:
        print("\n✓ All images processed successfully")


if __name__ == '__main__':
    main()
