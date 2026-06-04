#!/bin/bash
# bootstrap-env.sh — Ensures orchestrator API keys are available.
#
# Strategy:
#   1. If orchestrator/.env exists → done (also backs up to ~/.orchestrator.env)
#   2. If ~/.orchestrator.env exists → restore it
#   3. Otherwise → decode from env_seed.py (committed, obfuscated)
#
# Usage:  bash bootstrap-env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ENV="$SCRIPT_DIR/.env"
HOME_ENV="$HOME/.orchestrator.env"

# Case 1: local .env exists — back it up and done
if [ -f "$LOCAL_ENV" ]; then
    cp -f "$LOCAL_ENV" "$HOME_ENV" 2>/dev/null
    exit 0
fi

# Case 2: home backup exists — restore
if [ -f "$HOME_ENV" ]; then
    cp -f "$HOME_ENV" "$LOCAL_ENV" 2>/dev/null
    exit 0
fi

# Case 3: decode from seed (always available after clone)
if [ -f "$SCRIPT_DIR/env_seed.py" ]; then
    python3 "$SCRIPT_DIR/env_seed.py" --decode 2>/dev/null
    # Back up the restored file
    if [ -f "$LOCAL_ENV" ]; then
        cp -f "$LOCAL_ENV" "$HOME_ENV" 2>/dev/null
    fi
    exit 0
fi

echo "[bootstrap] WARNING: No .env source found." >&2
exit 0
