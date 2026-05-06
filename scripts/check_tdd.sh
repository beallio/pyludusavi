#!/usr/bin/env bash
# Strict TDD Enforcement Script
# Checks if new methods/functions in src/ have corresponding tests.

set -e

echo "Checking TDD compliance..."

# Simple check: find all functions in src and ensure they are mentioned in tests
# This is a heuristic but aligns with Task 0.2
FUNCTIONS=$(grep -rE "def [a-zA-Z0-9_]+" src/pyludusavi/ --exclude="__init__.py" --exclude="_version.py" | awk '{print $2}' | cut -d'(' -f1 | sort | uniq)

MISSING=0
for FUNC in $FUNCTIONS; do
    if ! grep -rq "$FUNC" tests/; then
        echo "Error: Function '$FUNC' has no corresponding test."
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    echo "TDD check failed: $MISSING functions missing tests."
    exit 1
fi

echo "TDD check passed."
exit 0
