# Repository Bloat Management — Granny's Archive

## Problem

- Image files can be large.
- Old versions remain in `.git`.
- Scanner software often saves at 100% JPEG quality.

## Solution: Image Optimization

`scripts/optimize_images.py` re-compresses JPEGs at Q85 (visually identical,
human-readable) for size reduction.

```bash
# Preview savings (no changes)
python scripts/optimize_images.py --dry-run

# Optimize granny collection
python scripts/optimize_images.py --collection granny

# Optimize with backups (keeps .original.jpeg files)
python scripts/optimize_images.py --backup

# Custom quality (default: 85)
python scripts/optimize_images.py --quality 80
```

## Important Notes

1. **Run once.** The script tracks optimized images in `optimization_manifest.json`.
2. **Q85 is visually identical** to originals for recipe reading.
3. **Git history retains old versions** — see options below.
4. **Backups optional** — use `--backup` to keep originals as `.original.jpeg`.

## Reducing Git History Size

After optimizing, old versions still live in git history. Options:

1. **Accept it** — clone size stays large but working tree is smaller.
2. **Shallow clone** — `git clone --depth 1` for new contributors.
3. **BFG Repo-Cleaner** — rewrite history (destructive; coordinate with team).
4. **Git LFS migration** — move images to LFS (requires setup).
