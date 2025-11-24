#!/bin/bash
# PDF verification script
# Usage: ./verify_pdf.sh <filename.pdf>

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.pdf>"
    echo "Example: $0 report.pdf"
    exit 1
fi

FILENAME="$1"

if [ ! -f "$FILENAME" ]; then
    echo "Error: File '$FILENAME' not found!"
    exit 1
fi

echo "=== PDF Verification Report: $FILENAME ==="
echo ""

# Check 1: Structural integrity with qpdf (if available)
echo "--- Structural Integrity Check ---"
if command -v qpdf &> /dev/null; then
    QPDF_RESULT=$(qpdf --check "$FILENAME" 2>&1)
    if [ -z "$QPDF_RESULT" ] || echo "$QPDF_RESULT" | grep -q "No errors"; then
        echo "PASS: PDF structure is valid"
    else
        echo "WARNING: PDF may have structural issues"
        echo "$QPDF_RESULT"
    fi
else
    echo "SKIP: qpdf not installed"
fi
echo ""

# Check 2: PDF metadata with pdfinfo
echo "--- PDF Metadata ---"
if command -v pdfinfo &> /dev/null; then
    pdfinfo "$FILENAME"
else
    echo "SKIP: pdfinfo not installed"
fi
echo ""

# Check 3: Text extraction test
echo "--- Text Extraction Test ---"
if command -v pdftotext &> /dev/null; then
    CHAR_COUNT=$(pdftotext "$FILENAME" - | wc -c)
    if [ "$CHAR_COUNT" -gt 0 ]; then
        echo "PASS: Text extraction successful ($CHAR_COUNT characters)"
    else
        echo "WARNING: No text extracted - check font encoding"
    fi
else
    echo "SKIP: pdftotext not installed"
fi
echo ""

# Check 4: File size sanity check
echo "--- File Size Check ---"
FILE_SIZE=$(stat -c%s "$FILENAME" 2>/dev/null || stat -f%z "$FILENAME" 2>/dev/null)
FILE_SIZE_KB=$((FILE_SIZE / 1024))
echo "File size: ${FILE_SIZE_KB} KB"

if [ "$FILE_SIZE_KB" -lt 1 ]; then
    echo "WARNING: File is very small, may be incomplete"
elif [ "$FILE_SIZE_KB" -gt 50000 ]; then
    echo "NOTE: Large file size, consider optimization"
else
    echo "PASS: File size appears reasonable"
fi

echo ""
echo "=== Verification Complete ==="
