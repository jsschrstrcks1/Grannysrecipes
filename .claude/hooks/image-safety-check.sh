#!/bin/bash
# Image Safety Check Hook for Granny Hudson's Recipe Archive
# Warns before reading potentially oversized images
#
# This hook checks image dimensions before Read operations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

FILE_PATH="${CLAUDE_FILE_PATH:-$1}"

# Check if the file is an image
if [[ "$FILE_PATH" == *.jpeg ]] || [[ "$FILE_PATH" == *.jpg ]] || [[ "$FILE_PATH" == *.png ]]; then
    # Check if it's in the processed directory (already safe)
    if [[ "$FILE_PATH" == *"/processed/"* ]]; then
        exit 0  # Safe to read
    fi

    # Check if it's in the granny directory (might be oversized)
    if [[ "$FILE_PATH" == *"/granny/"* ]]; then
        # Check for processed version
        BASENAME=$(basename "$FILE_PATH")
        PROCESSED_PATH="$PROJECT_DIR/granny/processed/$BASENAME"

        if [[ -f "$PROCESSED_PATH" ]]; then
            echo "WARNING: Use processed version instead: granny/processed/$BASENAME (original may exceed 2000px limit)"
        else
            echo "WARNING: Image may exceed 2000px limit. Run: python scripts/image_safeguards.py status"
        fi
    fi
fi

exit 0
