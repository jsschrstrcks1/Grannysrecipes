# Image Workflow — Granny's Archive

## Step 0: Pre-flight (run BEFORE any image read)

Claude's API rejects images with any dimension > 2000 px:

```
API Error: 400 ... image dimensions exceed max allowed size for many-image
requests: 2000 pixels
```

Before reading any image:

```bash
python scripts/image_safeguards.py status
```

If the manifest is missing or shows oversized images:

```bash
python scripts/process_images.py --collection granny
python scripts/image_safeguards.py validate
```

## Collection-specific rules

| Collection | Source | Max dim | Path |
|---|---|---|---|
| Granny | Scanned cards | Check first | `granny/*.jpeg` or `granny/processed/*.jpeg` if oversized |

## Manifest Commands

```bash
python scripts/image_safeguards.py validate          # build / refresh manifest
python scripts/image_safeguards.py status            # current state
python scripts/image_safeguards.py next granny       # next unprocessed
python scripts/image_safeguards.py mark "file.jpeg" processed
python scripts/image_safeguards.py mark "file.jpeg" skipped "Not a recipe"
python scripts/image_safeguards.py broken            # list broken
```

## Status Values

| Status | Meaning |
|---|---|
| `valid` | Ready to process |
| `oversized` | Valid but >2000 px (use processed version) |
| `resized` | Processed version available |
| `broken` | Cannot read (skip) |
| `recoverable` | Partially corrupted (may work) |
| `processed` | Recipe extraction complete |
| `skipped` | Not a recipe |

## Recovering from a 2000 px error

If you hit `image dimensions exceed max allowed size`:

1. **STOP.** Do NOT retry the same request.
2. `python scripts/process_images.py --collection granny`
3. `python scripts/image_safeguards.py validate`
4. Re-run using `granny/processed/<filename>.jpeg`.
5. If the error persists, mark broken:
   `python scripts/image_safeguards.py mark "file.jpeg" broken "Dimension error"`.

**Why the loop matters:** when Claude hits this error it cannot read the
response and may keep retrying. The only fix is ensuring all images are
≤ 2000 px BEFORE starting any OCR batch.

## Crash Recovery

If a session crashes mid-processing:

1. The manifest preserves state.
2. `python scripts/image_safeguards.py status` shows progress.
3. `python scripts/image_safeguards.py next granny` returns the next image.
4. Resume — no work lost.
