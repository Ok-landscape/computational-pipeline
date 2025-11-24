# GitHub Publishing Guide for LaTeX Templates

This guide provides step-by-step instructions for publishing the latex-templates collection to GitHub and CoCalc ShareServer.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Publishing Workflows](#publishing-workflows)
3. [CoCalc ShareServer Integration](#cocalc-shareserver-integration)
4. [Automation Options](#automation-options)
5. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Prerequisites

- GitHub account
- CoCalc project with templates
- Git configured locally

### Step 1: Configure Git

```bash
# Navigate to repository
cd /home/user/latex-templates

# Verify git is initialized (should already be done)
git status

# Configure git identity (if not already configured)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 2: Set Up GitHub Repository

```bash
# Run setup script with your GitHub username
./scripts/setup_github.sh YOUR_GITHUB_USERNAME

# This script will:
# - Configure git remote
# - Update publisher script with correct URL
# - Check authentication
# - Create initial commits
```

### Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `latex-templates`
3. Description: "Collection of 201 LaTeX templates for scientific computing"
4. Choose Public or Private
5. **DO NOT** check "Initialize with README"
6. Click "Create repository"

### Step 4: Configure Authentication

#### Option A: SSH Keys (Recommended)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Display public key
cat ~/.ssh/id_ed25519.pub

# Copy the output and add to GitHub:
# 1. Go to https://github.com/settings/keys
# 2. Click "New SSH key"
# 3. Paste the public key
# 4. Click "Add SSH key"

# Test connection
ssh -T git@github.com

# Update remote to use SSH
git remote set-url origin git@github.com:YOUR_USERNAME/latex-templates.git
```

#### Option B: Personal Access Token

```bash
# Generate token at: https://github.com/settings/tokens
# Click "Generate new token (classic)"
# Select scope: "repo" (all)
# Generate and copy the token

# Configure git to store credentials
git config --global credential.helper store

# When you push, use your username and token as password
```

---

## Publishing Workflows

### Quick Start: Publish Everything

```bash
# Add all templates and PDFs
git add templates/
git add output/
git add README.md CLAUDE.md COCALC_SHARESERVER.md
git add scripts/ config/

# Check what will be committed
git status

# Commit
git commit -m "Initial commit: Add LaTeX template collection

- 201 templates across 67 scientific categories
- 103 compiled PDFs
- Build and publishing scripts
- Documentation"

# Push to GitHub
git push -u origin main
```

### Workflow 1: Publish All (First Time)

Use when publishing for the first time or after major updates:

```bash
# Interactive batch publish
./scripts/publish_all.sh

# Dry run (commit locally but don't push)
./scripts/publish_all.sh --dry-run
```

### Workflow 2: Publish New/Modified Only

Use for incremental updates after adding or modifying templates:

```bash
# Check what changed
git status --short

# Publish only changes
./scripts/publish_new.sh
```

### Workflow 3: Publish Specific Category

Use when working on templates in a specific field:

```bash
# Publish aerospace templates
./scripts/publish_category.sh aerospace

# Publish biology templates
./scripts/publish_category.sh biology

# See available categories
ls templates/
```

### Workflow 4: Publish Single Template

Use when updating one template:

```bash
# Publish single template (with PDF)
python3 scripts/latex_publisher.py single templates/physics/quantum_mechanics.tex

# Publish without PDF
python3 scripts/latex_publisher.py single templates/math/topology.tex --no-pdf
```

### Workflow 5: Manual Control

For fine-grained control:

```bash
# Add specific files
git add templates/aerospace/rocket_propulsion.tex
git add output/rocket_propulsion.pdf

# Commit with custom message
git commit -m "Add rocket propulsion analysis template

- Includes thrust calculations
- Isp optimization examples
- Compiled with PythonTeX"

# Push
git push origin main
```

---

## CoCalc ShareServer Integration

### Step 1: Find Your Project ID

Your CoCalc project ID is in the browser URL:

```
https://cocalc.com/projects/YOUR-PROJECT-ID-HERE/files/...
```

Copy the project ID (long hexadecimal string).

### Step 2: Generate Share Links

```bash
# Generate links for all templates
./scripts/generate_share_links.sh YOUR-PROJECT-ID

# This creates SHARE_LINKS.md with direct links to all files
```

### Step 3: Enable Public Access in CoCalc

**Method 1: Project-Wide Public Access**

1. Open your CoCalc project
2. Click Settings (gear icon)
3. Under "Public files", enable:
   - `templates/` directory
   - `output/` directory

**Method 2: Individual Share Links**

1. Navigate to a file in CoCalc
2. Click the "Share" button
3. Copy the public share link
4. Share link remains valid until revoked

### Step 4: Publish Share Links to GitHub

```bash
# Add generated share links
git add SHARE_LINKS.md

# Commit
git commit -m "Add CoCalc ShareServer links for all templates"

# Push
git push origin main
```

### Updating Share Links

After adding new templates or recompiling PDFs:

```bash
# Regenerate share links
./scripts/generate_share_links.sh YOUR-PROJECT-ID

# Commit and push
git add SHARE_LINKS.md
git commit -m "Update CoCalc share links"
git push
```

---

## Automation Options

### Option 1: Cron Job (Periodic Publishing)

Automatically publish changes every hour:

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour)
0 * * * * cd /home/user/latex-templates && /home/user/latex-templates/scripts/publish_new.sh >> /home/user/latex-templates/logs/cron.log 2>&1
```

### Option 2: Git Hooks (On Commit)

Automatically push after local commits:

```bash
# Create post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Auto-push after commit (use with caution)

# Only push if on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ]; then
    git push origin main
fi
EOF

# Make executable
chmod +x .git/hooks/post-commit
```

### Option 3: GitHub Actions (CI/CD)

Automatically compile templates when `.tex` files are pushed:

```yaml
# .github/workflows/compile-latex.yml
name: Compile LaTeX Templates

on:
  push:
    paths:
      - 'templates/**/*.tex'

jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install LaTeX
        run: sudo apt-get install -y texlive-full
      - name: Compile changed templates
        run: ./scripts/compile_changed.sh
      - name: Commit PDFs
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add output/*.pdf
          git commit -m "Auto-compile PDFs [skip ci]"
          git push
```

### Option 4: Watch Script (Real-Time)

Automatically publish when files change:

```bash
# Create watch script
cat > scripts/watch_and_publish.sh << 'EOF'
#!/bin/bash
# Watch for changes and auto-publish

while true; do
    # Check for changes
    git fetch origin main
    LOCAL=$(git rev-parse main)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" != "$REMOTE" ]; then
        # Pull changes
        git pull origin main

        # Check for new local changes
        if [ -n "$(git status --porcelain)" ]; then
            # Publish changes
            ./scripts/publish_new.sh
        fi
    fi

    # Wait 5 minutes
    sleep 300
done
EOF

chmod +x scripts/watch_and_publish.sh

# Run in background
nohup ./scripts/watch_and_publish.sh > logs/watch.log 2>&1 &
```

---

## Troubleshooting

### Issue: Authentication Failed

**Symptoms**: `git push` fails with "Permission denied" or "Authentication failed"

**Solutions**:

1. **Verify SSH key**:
   ```bash
   ssh -T git@github.com
   # Should see: "Hi USERNAME! You've successfully authenticated..."
   ```

2. **Check remote URL**:
   ```bash
   git remote -v
   # Should be: git@github.com:USERNAME/latex-templates.git
   ```

3. **Use HTTPS with token**:
   ```bash
   git remote set-url origin https://github.com/USERNAME/latex-templates.git
   # When pushing, use PAT as password
   ```

### Issue: Large Files Rejected

**Symptoms**: "file is X MB; this exceeds GitHub's file size limit of 100 MB"

**Solutions**:

1. **Use Git LFS**:
   ```bash
   git lfs install
   git lfs track "output/*.pdf"
   git add .gitattributes
   git commit -m "Track PDFs with Git LFS"
   ```

2. **Optimize PDFs**:
   ```bash
   # Compress large PDFs
   for pdf in output/*.pdf; do
       gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
          -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
          -sOutputFile="${pdf}.compressed" "$pdf"
       mv "${pdf}.compressed" "$pdf"
   done
   ```

3. **Exclude large PDFs**:
   ```bash
   # Add to .gitignore
   echo "output/*_large.pdf" >> .gitignore
   ```

### Issue: Merge Conflicts in PDFs

**Symptoms**: Git reports conflicts in binary PDF files

**Solution**:

```bash
# Always use local version for PDFs
git checkout --ours output/*.pdf
git add output/*.pdf

# Or recompile from source
git checkout main templates/category/file.tex
# Recompile the template
git add output/file.pdf
```

### Issue: Too Many Files

**Symptoms**: `git add` takes very long or fails

**Solution**:

```bash
# Add by category
for category in templates/*/; do
    echo "Adding $category..."
    git add "$category"
done

# Or use batch script
./scripts/publish_all.sh
```

### Issue: Publishing Script Fails

**Symptoms**: `publish_new.sh` or `publish_all.sh` exits with error

**Check**:

```bash
# View logs
cat logs/publishing.log

# Check git status
git status

# Verify scripts are executable
ls -l scripts/*.sh

# Make executable if needed
chmod +x scripts/*.sh
```

---

## Best Practices

### 1. Regular Commits

Commit frequently with meaningful messages:

```bash
# Bad
git commit -m "updates"

# Good
git commit -m "Add thermodynamics templates

- Classical thermodynamics equations
- Statistical mechanics examples
- Compiled PDFs included"
```

### 2. Organize by Category

Publish related templates together:

```bash
# Publish all physics templates at once
./scripts/publish_category.sh physics

# Then publish all math templates
./scripts/publish_category.sh mathematics
```

### 3. Test Before Publishing

```bash
# Dry run first
./scripts/publish_all.sh --dry-run

# Review changes
git diff --cached

# Then publish
git push origin main
```

### 4. Keep Share Links Updated

After any template changes:

```bash
# Recompile templates
make all-docs

# Regenerate share links
./scripts/generate_share_links.sh YOUR-PROJECT-ID

# Publish both
git add output/ SHARE_LINKS.md
git commit -m "Update templates and share links"
git push
```

### 5. Use Tags for Releases

Mark stable versions:

```bash
# Tag major release
git tag -a v1.0 -m "Release v1.0: Initial collection of 201 templates"

# Push tags
git push origin --tags
```

---

## Quick Reference

### Common Commands

```bash
# Status
git status
python3 scripts/latex_publisher.py status

# Publish new/modified
./scripts/publish_new.sh

# Publish all
./scripts/publish_all.sh

# Publish category
./scripts/publish_category.sh CATEGORY

# Generate share links
./scripts/generate_share_links.sh PROJECT-ID

# View logs
tail -f logs/publishing.log
```

### File Locations

- **Templates**: `/home/user/latex-templates/templates/`
- **PDFs**: `/home/user/latex-templates/output/`
- **Scripts**: `/home/user/latex-templates/scripts/`
- **Logs**: `/home/user/latex-templates/logs/`
- **Documentation**: `/home/user/latex-templates/*.md`

---

## Support

- **GitHub Issues**: Report problems with publishing workflow
- **CoCalc Support**: help@cocalc.com for ShareServer questions
- **Documentation**: See [COCALC_SHARESERVER.md](COCALC_SHARESERVER.md)

---

**Last Updated**: 2025-11-24
