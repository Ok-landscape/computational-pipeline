# CoCalc ShareServer Integration

This document explains how to share LaTeX templates and compiled PDFs via CoCalc's ShareServer, making them publicly accessible via HTTP.

## Overview

CoCalc ShareServer allows you to publish files from your project to the web without needing a separate hosting service. Files are accessible via:

```
https://cocalc.com/projects/<PROJECT_ID>/files/<FILE_PATH>
```

## Quick Setup

### 1. Find Your Project ID

Your CoCalc project ID is visible in the browser URL when viewing your project:

```
https://cocalc.com/projects/YOUR-PROJECT-ID-HERE/files/...
```

The project ID is a long hexadecimal string (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`).

### 2. Get Shareable Links

#### Option A: Via CoCalc Web UI

1. Navigate to a file in the Files tab
2. Click on the file to open it
3. Click the "Share" button in the toolbar
4. Copy the public share link

#### Option B: Via Terminal (Programmatic)

```bash
# Set your project ID
PROJECT_ID="your-project-id-here"

# Template file
TEMPLATE="templates/aerospace/rocket_propulsion.tex"
SHARE_URL="https://cocalc.com/projects/${PROJECT_ID}/files/${TEMPLATE}"

echo "Template: $SHARE_URL"

# Compiled PDF
PDF="output/rocket_propulsion.pdf"
PDF_URL="https://cocalc.com/projects/${PROJECT_ID}/files/${PDF}"

echo "PDF: $PDF_URL"
```

### 3. Make Files Public

By default, CoCalc files require authentication. To make them publicly accessible:

#### Method 1: Project Settings
1. Go to Project Settings (gear icon)
2. Under "Project Control", find "Public files"
3. Enable public access to specific directories

#### Method 2: Share Links
1. Use the Share button to create a public share link
2. This generates a special URL that doesn't require login
3. Share links remain valid until revoked

## Automation Scripts

### Generate Share Links for All Templates

Create a script to generate a comprehensive index:

```bash
#!/bin/bash
# File: scripts/generate_share_links.sh

PROJECT_ID="your-project-id-here"
OUTPUT_FILE="SHARE_LINKS.md"

echo "# LaTeX Template Share Links" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Generated: $(date)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Iterate through categories
for category in templates/*/; do
    category_name=$(basename "$category")
    echo "## ${category_name^}" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"

    # Find .tex files
    find "$category" -name "*.tex" -type f | sort | while read tex_file; do
        basename=$(basename "$tex_file" .tex)
        rel_path="${tex_file#./}"

        # Template link
        template_url="https://cocalc.com/projects/${PROJECT_ID}/files/${rel_path}"

        # PDF link (if exists)
        pdf_file="output/${basename}.pdf"
        if [ -f "$pdf_file" ]; then
            pdf_url="https://cocalc.com/projects/${PROJECT_ID}/files/${pdf_file}"
            echo "- **${basename}**: [Source](${template_url}) | [PDF](${pdf_url})" >> "$OUTPUT_FILE"
        else
            echo "- **${basename}**: [Source](${template_url})" >> "$OUTPUT_FILE"
        fi
    done

    echo "" >> "$OUTPUT_FILE"
done

echo "Share links generated: $OUTPUT_FILE"
```

### Batch Update Share Status

```bash
#!/bin/bash
# File: scripts/update_share_status.sh
# Purpose: Update public sharing status for all templates and PDFs

# This requires CoCalc API access (if available)
# Or manual configuration via web interface

echo "To make files publicly accessible:"
echo ""
echo "1. Go to Project Settings"
echo "2. Enable 'Public files' for:"
echo "   - templates/"
echo "   - output/"
echo ""
echo "Or use individual share links for selective sharing"
```

## Integration with GitHub

You can include CoCalc share links in your GitHub README to provide direct access:

```markdown
## Live Examples

View and download templates directly:

| Category | Template | Source | PDF |
|----------|----------|--------|-----|
| Aerospace | Rocket Propulsion | [View](https://cocalc.com/projects/.../templates/aerospace/rocket_propulsion.tex) | [Download](https://cocalc.com/projects/.../output/rocket_propulsion.pdf) |
```

## Advanced: CoCalc Public API

If you have access to CoCalc's API, you can programmatically manage shares:

```python
#!/usr/bin/env python3
"""
File: scripts/cocalc_share_api.py
Purpose: Manage CoCalc shares via API (if available)
"""

import requests
import json
from pathlib import Path

# Configuration
PROJECT_ID = "your-project-id"
API_KEY = "your-api-key"  # If available
BASE_URL = "https://cocalc.com/api/v1"

def create_public_share(file_path):
    """
    Create a public share link for a file.
    Note: This is a conceptual example - actual API may differ
    """
    endpoint = f"{BASE_URL}/projects/{PROJECT_ID}/files/share"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "path": file_path,
        "public": True
    }

    response = requests.post(endpoint, headers=headers, json=data)

    if response.status_code == 200:
        share_data = response.json()
        return share_data.get("url")
    else:
        print(f"Error creating share: {response.status_code}")
        return None

def list_public_shares():
    """List all public shares in the project."""
    endpoint = f"{BASE_URL}/projects/{PROJECT_ID}/shares"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error listing shares: {response.status_code}")
        return None

# Note: CoCalc's public API may have different endpoints
# Check documentation: https://doc.cocalc.com/api/
```

## Best Practices

### 1. Organize Shares by Category

Create separate share indexes for different audiences:

- `SHARE_LINKS_PUBLIC.md` - General access
- `SHARE_LINKS_STUDENTS.md` - Educational templates
- `SHARE_LINKS_RESEARCH.md` - Research-grade templates

### 2. Update Links Regularly

After adding new templates or recompiling PDFs:

```bash
# Regenerate share links
./scripts/generate_share_links.sh

# Commit to GitHub
git add SHARE_LINKS.md
git commit -m "Update share links"
git push
```

### 3. Include Direct Download Links

For PDFs, provide both view and download options:

```markdown
- [View PDF](https://cocalc.com/projects/.../output/doc.pdf)
- [Download PDF](https://cocalc.com/projects/.../output/doc.pdf?download=true)
```

### 4. Version Control Share Links

Keep share links in version control so others can access the latest versions:

```bash
git add SHARE_LINKS.md
git commit -m "Update CoCalc share links for new templates"
```

## Limitations and Considerations

### File Size Limits
- CoCalc may have bandwidth limits for public shares
- Large PDFs (>50MB) might not be ideal for direct sharing
- Consider using GitHub LFS for very large files

### Authentication
- Public shares don't require CoCalc login
- But project must enable public file access
- Or use individual share tokens

### Persistence
- Share links persist until manually revoked
- Links remain valid even if you rename files (until next share update)
- Regular regeneration ensures consistency

### Alternative: GitHub as Primary Host

For maximum accessibility, consider:

1. **GitHub + CoCalc Development**
   - Develop and compile in CoCalc
   - Push to GitHub for public distribution
   - Use GitHub Pages for web hosting
   - CoCalc shares for live editing/collaboration

2. **Dual Distribution**
   - CoCalc shares for interactive development
   - GitHub releases for stable versions
   - Document both access methods

## Example Integration

Complete workflow combining GitHub and CoCalc:

```bash
#!/bin/bash
# File: scripts/publish_with_shares.sh

# 1. Compile templates
make all-docs

# 2. Generate CoCalc share links
./scripts/generate_share_links.sh

# 3. Publish to GitHub
./scripts/publish_all.sh

# 4. Update GitHub README with share links
python3 scripts/update_readme_with_shares.py

# 5. Commit everything
git add SHARE_LINKS.md README.md
git commit -m "Update templates and share links"
git push
```

## Support and Resources

- **CoCalc Documentation**: https://doc.cocalc.com/
- **CoCalc API**: https://doc.cocalc.com/api/
- **Public Sharing**: https://doc.cocalc.com/share.html
- **CoCalc Support**: help@cocalc.com

## Quick Reference

### Common Commands

```bash
# Set project ID
export COCALC_PROJECT_ID="your-project-id"

# Generate share link
echo "https://cocalc.com/projects/${COCALC_PROJECT_ID}/files/templates/category/file.tex"

# Generate all share links
./scripts/generate_share_links.sh

# Update README with links
python3 scripts/update_readme_with_shares.py
```

### URL Format

```
# View file
https://cocalc.com/projects/<PROJECT_ID>/files/<PATH>

# Download file
https://cocalc.com/projects/<PROJECT_ID>/files/<PATH>?download=true

# Share link (public)
https://cocalc.com/<SHARE_ID>
```
