#!/usr/bin/env python3
"""
Image Safeguards for Grandma's Recipe Archive

This module provides safeguards to prevent broken images from crashing
AI processing sessions. It creates a processing manifest that tracks:
1. Which images have been validated
2. Which images are broken/problematic
3. Session state for resumable processing

Usage:
    python scripts/image_safeguards.py validate         # Validate all images
    python scripts/image_safeguards.py status           # Show processing status
    python scripts/image_safeguards.py next             # Get next processable image
    python scripts/image_safeguards.py mark <file> <status>  # Mark image status

The manifest file (image_manifest.json) can be used by AI assistants to:
- Skip known broken images
- Resume from where processing left off
- Track which images need human intervention
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

try:
    from PIL import Image, ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False


# Configuration
MANIFEST_FILE = "image_manifest.json"
MAX_DIMENSION = 2000

COLLECTIONS = {
    "grandma": {"path": "", "prefix": "Grandmas-recipes"},
    "mommom": {"path": "mom/", "prefix": "Moms Recipes"},
    "granny": {"path": "granny/", "prefix": "Granny"},
    "reference": {"path": "all/", "prefix": "IMG_"}
}

# Image statuses
STATUS_UNVALIDATED = "unvalidated"
STATUS_VALID = "valid"
STATUS_OVERSIZED = "oversized"         # Valid but needs resize
STATUS_RESIZED = "resized"             # Processed version available
STATUS_BROKEN = "broken"               # Cannot be read
STATUS_RECOVERABLE = "recoverable"     # Broken but may be salvageable
STATUS_PROCESSED = "processed"         # Recipe extraction complete
STATUS_SKIPPED = "skipped"             # Not a recipe (household hints, etc.)


class ImageManifest:
    """Manages the image processing manifest for session resilience."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.manifest_path = data_dir / MANIFEST_FILE
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load existing manifest or create new one."""
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Corrupted manifest, creating backup and starting fresh")
                backup = self.manifest_path.with_suffix('.json.bak')
                self.manifest_path.rename(backup)

        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "max_dimension": MAX_DIMENSION,
            "collections": {},
            "images": {},
            "session": {
                "last_processed": None,
                "processing_collection": None,
                "processing_index": 0
            },
            "stats": {
                "total": 0,
                "validated": 0,
                "broken": 0,
                "oversized": 0,
                "processed": 0
            }
        }

    def save(self):
        """Save manifest to disk."""
        self.manifest["last_updated"] = datetime.now().isoformat()
        self._update_stats()

        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def _update_stats(self):
        """Update summary statistics."""
        stats = {
            "total": 0,
            "validated": 0,
            "broken": 0,
            "oversized": 0,
            "processed": 0,
            "skipped": 0
        }

        for img_data in self.manifest["images"].values():
            stats["total"] += 1
            status = img_data.get("status", STATUS_UNVALIDATED)

            if status in [STATUS_VALID, STATUS_RESIZED, STATUS_PROCESSED, STATUS_SKIPPED]:
                stats["validated"] += 1
            if status == STATUS_BROKEN:
                stats["broken"] += 1
            if status == STATUS_OVERSIZED:
                stats["oversized"] += 1
            if status == STATUS_PROCESSED:
                stats["processed"] += 1
            if status == STATUS_SKIPPED:
                stats["skipped"] += 1

        self.manifest["stats"] = stats

    def validate_image(self, image_path: Path) -> Dict:
        """Validate a single image and return status info."""
        result = {
            "status": STATUS_UNVALIDATED,
            "width": None,
            "height": None,
            "error": None,
            "validated_at": datetime.now().isoformat(),
            "file_size": 0
        }

        try:
            result["file_size"] = image_path.stat().st_size
        except OSError as e:
            result["status"] = STATUS_BROKEN
            result["error"] = f"Cannot access: {e}"
            return result

        if result["file_size"] == 0:
            result["status"] = STATUS_BROKEN
            result["error"] = "Empty file (0 bytes)"
            return result

        if not PILLOW_AVAILABLE:
            # Can't validate without Pillow, assume valid
            result["status"] = STATUS_VALID
            result["error"] = "Pillow not installed, assuming valid"
            return result

        try:
            with Image.open(image_path) as img:
                img.load()  # Actually load to detect truncation
                result["width"] = img.width
                result["height"] = img.height

                if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                    result["status"] = STATUS_OVERSIZED
                else:
                    result["status"] = STATUS_VALID

        except Exception as e:
            error_str = str(e).lower()
            if "truncated" in error_str or "corrupt" in error_str:
                result["status"] = STATUS_RECOVERABLE
            else:
                result["status"] = STATUS_BROKEN
            result["error"] = str(e)

        return result

    def scan_collection(self, collection_id: str) -> List[Path]:
        """Find all images in a collection."""
        if collection_id not in COLLECTIONS:
            return []

        collection_info = COLLECTIONS[collection_id]
        collection_path = self.data_dir / collection_info["path"]

        if not collection_path.exists():
            return []

        images = (list(collection_path.glob("*.jpeg")) +
                  list(collection_path.glob("*.jpg")) +
                  list(collection_path.glob("*.png")) +
                  list(collection_path.glob("*.PNG")))
        # Exclude processed folder
        images = [f for f in images if "processed" not in str(f).lower()]

        return sorted(images)

    def validate_all(self, collection_id: Optional[str] = None):
        """Validate all images in one or all collections."""
        collections = [collection_id] if collection_id else list(COLLECTIONS.keys())

        for coll_id in collections:
            print(f"\nValidating collection: {coll_id}")
            images = self.scan_collection(coll_id)

            if coll_id not in self.manifest["collections"]:
                self.manifest["collections"][coll_id] = {
                    "path": COLLECTIONS[coll_id]["path"],
                    "total_images": len(images)
                }

            for i, img_path in enumerate(images, 1):
                key = f"{coll_id}/{img_path.name}"
                print(f"  [{i}/{len(images)}] {img_path.name}...", end=" ")

                validation = self.validate_image(img_path)
                self.manifest["images"][key] = {
                    "collection": coll_id,
                    "filename": img_path.name,
                    "path": str(img_path.relative_to(self.data_dir)),
                    **validation
                }

                status = validation["status"]
                if status == STATUS_VALID:
                    print("OK")
                elif status == STATUS_OVERSIZED:
                    print(f"OVERSIZED ({validation['width']}x{validation['height']})")
                elif status == STATUS_BROKEN:
                    print(f"BROKEN: {validation['error']}")
                elif status == STATUS_RECOVERABLE:
                    print(f"RECOVERABLE: {validation['error']}")
                else:
                    print(status)

        self.save()

    def get_processable_images(self, collection_id: Optional[str] = None) -> List[Dict]:
        """Get list of images that can be processed (not broken)."""
        result = []

        for key, data in self.manifest["images"].items():
            if collection_id and data.get("collection") != collection_id:
                continue

            status = data.get("status", STATUS_UNVALIDATED)
            # Include valid, oversized (if processed folder exists), and resized
            if status in [STATUS_VALID, STATUS_RESIZED]:
                result.append({
                    "key": key,
                    **data
                })
            elif status == STATUS_OVERSIZED:
                # Check if processed version exists
                processed_path = (
                    self.data_dir /
                    data.get("path", "").replace(data["filename"], f"processed/{data['filename']}")
                )
                if processed_path.exists():
                    data["processed_path"] = str(processed_path.relative_to(self.data_dir))
                    data["status"] = STATUS_RESIZED
                    result.append({"key": key, **data})
                else:
                    # Oversized but no processed version - can still try
                    result.append({"key": key, **data})

        return result

    def get_broken_images(self) -> List[Dict]:
        """Get list of broken images that need attention."""
        return [
            {"key": key, **data}
            for key, data in self.manifest["images"].items()
            if data.get("status") in [STATUS_BROKEN, STATUS_RECOVERABLE]
        ]

    def get_next_unprocessed(self, collection_id: Optional[str] = None) -> Optional[Dict]:
        """Get the next image that hasn't been processed yet."""
        for key, data in self.manifest["images"].items():
            if collection_id and data.get("collection") != collection_id:
                continue

            status = data.get("status", STATUS_UNVALIDATED)
            if status in [STATUS_VALID, STATUS_RESIZED, STATUS_OVERSIZED]:
                return {"key": key, **data}

        return None

    def mark_status(self, filename: str, status: str, notes: str = ""):
        """Mark an image with a specific status."""
        # Find the image by filename
        for key, data in self.manifest["images"].items():
            if data.get("filename") == filename or key.endswith(filename):
                data["status"] = status
                data["status_updated"] = datetime.now().isoformat()
                if notes:
                    data["notes"] = notes
                self.save()
                print(f"Marked {filename} as {status}")
                return True

        print(f"Image not found: {filename}")
        return False

    def set_session_position(self, collection_id: str, index: int, last_file: str):
        """Save session position for resumable processing."""
        self.manifest["session"] = {
            "last_processed": last_file,
            "processing_collection": collection_id,
            "processing_index": index,
            "saved_at": datetime.now().isoformat()
        }
        self.save()

    def get_session_position(self) -> Dict:
        """Get the saved session position."""
        return self.manifest.get("session", {})

    def print_status(self):
        """Print current manifest status."""
        stats = self.manifest.get("stats", {})
        session = self.manifest.get("session", {})

        print("\n" + "="*60)
        print("IMAGE MANIFEST STATUS")
        print("="*60)
        print(f"Last updated: {self.manifest.get('last_updated', 'Never')}")
        print(f"\nStatistics:")
        print(f"  Total images:    {stats.get('total', 0)}")
        print(f"  Validated:       {stats.get('validated', 0)}")
        print(f"  Broken:          {stats.get('broken', 0)}")
        print(f"  Oversized:       {stats.get('oversized', 0)}")
        print(f"  Processed:       {stats.get('processed', 0)}")
        print(f"  Skipped:         {stats.get('skipped', 0)}")

        if session.get("last_processed"):
            print(f"\nSession State:")
            print(f"  Last processed:  {session.get('last_processed')}")
            print(f"  Collection:      {session.get('processing_collection')}")
            print(f"  Index:           {session.get('processing_index')}")

        broken = self.get_broken_images()
        if broken:
            print(f"\nBroken Images ({len(broken)}):")
            for img in broken[:10]:
                status = img.get("status", "unknown")
                error = img.get("error", "")[:50]
                print(f"  - {img['filename']}: [{status}] {error}")
            if len(broken) > 10:
                print(f"  ... and {len(broken) - 10} more")

        print("="*60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    # Find data directory
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'data'

    if not data_dir.exists():
        print(f"ERROR: Data directory not found: {data_dir}")
        sys.exit(1)

    manifest = ImageManifest(data_dir)

    if command == "validate":
        collection = sys.argv[2] if len(sys.argv) > 2 else None
        manifest.validate_all(collection)
        manifest.print_status()

    elif command == "status":
        manifest.print_status()

    elif command == "next":
        collection = sys.argv[2] if len(sys.argv) > 2 else None
        next_img = manifest.get_next_unprocessed(collection)
        if next_img:
            print(f"Next image to process:")
            print(f"  File: {next_img['filename']}")
            print(f"  Path: {next_img.get('path', 'unknown')}")
            print(f"  Status: {next_img.get('status', 'unknown')}")
            if next_img.get('width'):
                print(f"  Size: {next_img['width']}x{next_img['height']}")
        else:
            print("No unprocessed images found")

    elif command == "mark":
        if len(sys.argv) < 4:
            print("Usage: image_safeguards.py mark <filename> <status> [notes]")
            print(f"Valid statuses: {STATUS_PROCESSED}, {STATUS_SKIPPED}, {STATUS_BROKEN}")
            sys.exit(1)
        filename = sys.argv[2]
        status = sys.argv[3]
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        manifest.mark_status(filename, status, notes)

    elif command == "broken":
        broken = manifest.get_broken_images()
        if broken:
            print(f"Broken images ({len(broken)}):\n")
            for img in broken:
                print(f"File: {img['filename']}")
                print(f"  Status: {img.get('status')}")
                print(f"  Error: {img.get('error', 'unknown')}")
                print()
        else:
            print("No broken images found")

    elif command == "processable":
        collection = sys.argv[2] if len(sys.argv) > 2 else None
        images = manifest.get_processable_images(collection)
        print(f"Processable images: {len(images)}")
        for img in images[:20]:
            size = f"{img.get('width', '?')}x{img.get('height', '?')}"
            print(f"  - {img['filename']} ({size}) [{img.get('status')}]")
        if len(images) > 20:
            print(f"  ... and {len(images) - 20} more")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
