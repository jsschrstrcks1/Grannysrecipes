#!/bin/bash
# Post-Write Validation Hook for Granny Hudson's Recipe Archive
# Automatically validates recipes_master.json after any edit
#
# This hook runs after Edit or Write operations on recipe files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Check if the edited file is related to recipes
FILE_PATH="${CLAUDE_FILE_PATH:-}"

# Only validate if we edited the recipes file
if [[ "$FILE_PATH" == *"recipes_master.json"* ]] || [[ "$FILE_PATH" == *"recipes"* && "$FILE_PATH" == *".json"* ]]; then
    # Run validation quietly, only show errors
    cd "$PROJECT_DIR"
    if [[ -f "scripts/validate-recipes.py" ]]; then
        python scripts/validate-recipes.py 2>&1 | grep -E "(ERROR|FAIL|Invalid)" || true
    fi
fi

exit 0
