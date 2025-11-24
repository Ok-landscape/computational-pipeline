#!/bin/bash
# Build script for PythonTeX documents
# Usage: ./build_pythontex.sh <filename.tex>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.tex>"
    echo "Example: $0 engineering_report.tex"
    exit 1
fi

FILENAME="$1"
BASENAME="${FILENAME%.tex}"

echo "=== Building PythonTeX document: $FILENAME ==="

# Get the directory of the tex file
TEXDIR=$(dirname "$FILENAME")
if [ "$TEXDIR" = "." ]; then
    TEXDIR=$(pwd)
fi

cd "$TEXDIR"
TEXFILE=$(basename "$FILENAME")

echo ""
echo "Pass 1: Initial LaTeX compilation..."
pdflatex -interaction=nonstopmode "$TEXFILE"

echo ""
echo "Pass 2: Executing Python code..."
pythontex "$TEXFILE"

echo ""
echo "Pass 3: Final LaTeX compilation..."
pdflatex -interaction=nonstopmode "$TEXFILE"

echo ""
echo "=== Build complete! Output: ${BASENAME}.pdf ==="
