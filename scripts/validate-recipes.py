#!/usr/bin/env python3
"""
Recipe Validation Script: thin wrapper over the shared validator.

The checks live in scripts/recipe_validator/core.py (byte-identical across the household
recipe repos); this repo's categories, limits and switches live in
scripts/recipe_validator/config.json. Same CLI, report and exit codes as before.

Usage:
    python scripts/validate-recipes.py
    python scripts/validate-recipes.py --strict  # Fail on warnings too
"""

import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the working tree free of __pycache__
sys.path.insert(0, str(Path(__file__).parent))

from recipe_validator.core import main_cli  # noqa: E402


if __name__ == '__main__':
    sys.exit(main_cli(Path(__file__).parent.parent,
                      Path(__file__).parent / 'recipe_validator' / 'config.json',
                      sys.argv))
