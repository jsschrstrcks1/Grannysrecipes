#!/bin/bash
# check-noindex.sh - Verify anti-indexing measures are in place
# This script ensures the family recipe archive remains private
#
# Checks:
# 1. robots.txt blocks all crawlers
# 2. No sitemap.xml exists
# 3. All HTML files have noindex meta tags

set -e

ERRORS=0
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

echo "Checking anti-indexing measures..."

# 1. Check robots.txt exists and blocks all
if [ ! -f "$REPO_ROOT/robots.txt" ]; then
    echo "❌ ERROR: robots.txt is missing!"
    ERRORS=$((ERRORS + 1))
else
    if ! grep -q "User-agent: \*" "$REPO_ROOT/robots.txt" || ! grep -q "Disallow: /" "$REPO_ROOT/robots.txt"; then
        echo "❌ ERROR: robots.txt must contain 'User-agent: *' and 'Disallow: /'"
        ERRORS=$((ERRORS + 1))
    else
        echo "✓ robots.txt blocks all crawlers"
    fi
fi

# 2. Check no sitemap.xml exists
if [ -f "$REPO_ROOT/sitemap.xml" ]; then
    echo "❌ ERROR: sitemap.xml exists - this helps indexing! Please remove it."
    ERRORS=$((ERRORS + 1))
else
    echo "✓ No sitemap.xml (good)"
fi

# 3. Check all HTML files have noindex meta tag
HTML_FILES=$(find "$REPO_ROOT" -maxdepth 2 -name "*.html" -type f 2>/dev/null)
for html_file in $HTML_FILES; do
    if [ -f "$html_file" ]; then
        if ! grep -qi 'meta name="robots" content="noindex' "$html_file"; then
            echo "❌ ERROR: $html_file is missing noindex meta tag!"
            echo "   Add: <meta name=\"robots\" content=\"noindex, nofollow, noarchive, nosnippet, noimageindex\">"
            ERRORS=$((ERRORS + 1))
        else
            echo "✓ $(basename "$html_file") has noindex meta tag"
        fi
    fi
done

# 4. Check for any sitemap references in HTML
for html_file in $HTML_FILES; do
    if [ -f "$html_file" ]; then
        if grep -qi 'sitemap' "$html_file"; then
            echo "⚠ WARNING: $html_file references 'sitemap' - please verify this is not enabling indexing"
        fi
    fi
done

echo ""
if [ $ERRORS -gt 0 ]; then
    echo "=========================================="
    echo "FAILED: $ERRORS anti-indexing issue(s) found"
    echo "=========================================="
    echo ""
    echo "This is a private family recipe archive."
    echo "Please fix the issues above before committing."
    exit 1
else
    echo "=========================================="
    echo "PASSED: All anti-indexing measures in place"
    echo "=========================================="
    exit 0
fi
