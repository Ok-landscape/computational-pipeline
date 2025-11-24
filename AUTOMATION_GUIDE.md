# Automated Workflow Guide

## Overview

This repository includes automated scripts for managing LaTeX template generation, compilation, and GitHub publishing. The automation infrastructure consists of three main scripts that work together to streamline the workflow.

## Repository Structure

```
computational-pipeline/
├── latex-templates/          # LaTeX template collection
│   ├── templates/            # Source .tex files (201 templates)
│   ├── output/               # Compiled PDF files (515 PDFs)
│   ├── logs/                 # Build logs
│   └── scripts/              # Build scripts
├── notebooks/
│   └── published/            # Published Jupyter notebooks (100 notebooks)
├── scripts/                  # Automation scripts
│   ├── auto_publish.sh       # Automated git operations
│   ├── cleanup_repo.sh       # Repository maintenance
│   └── generate_and_publish.py  # Template analysis and management
└── .gitignore               # Comprehensive exclusion rules
```

## Automation Scripts

### 1. auto_publish.sh - Automated Git Publishing

**Purpose**: Monitors the repository for changes and automatically commits and pushes to GitHub.

**Features**:
- Intelligent commit message generation based on changes
- Monitors latex-templates/ and notebooks/published/ directories
- Tracks new templates, modified files, and compiled PDFs
- Automatic staging and committing
- Safe push with error handling

**Usage**:

```bash
# Continuous monitoring (checks every 60 seconds)
./scripts/auto_publish.sh monitor

# Single check and publish
./scripts/auto_publish.sh once

# Show git status
./scripts/auto_publish.sh status
```

**Configuration**:
- Default check interval: 60 seconds
- Can be modified in the script: `CHECK_INTERVAL=60`

**Commit Message Format**:
```
Auto-update: added 5 new template(s), compiled 5 new PDF(s)

New templates added
PDFs compiled

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### 2. cleanup_repo.sh - Repository Cleanup

**Purpose**: Removes LaTeX build artifacts and unnecessary files from the repository.

**What it removes**:
- LaTeX auxiliary files (*.aux, *.log, *.out, *.toc, etc.)
- PythonTeX artifacts (*.pytxcode, pythontex-files-*, etc.)
- SageTeX artifacts (*.sagetex.*, *.sout)
- Knitr artifacts (*.Rout, .Rhistory, figure/)
- Temporary files (*~, *.swp, *.tmp, *.bak)
- Python cache (__pycache__/, *.pyc)

**What it keeps**:
- Source .tex files
- Compiled PDF files in output/
- Documentation (.md, .txt)
- Build scripts (.sh, .py)
- Configuration files

**Usage**:

```bash
# Run cleanup
./scripts/cleanup_repo.sh
```

**Typical output**:
```
Removed 200 auxiliary files
Removed 400 log files
Removed 198 PythonTeX code files
Removed 83 PythonTeX macro files
No tracked build artifacts found in git
```

### 3. generate_and_publish.py - Template Management

**Purpose**: Analyzes template gaps, manages compilation, and coordinates publishing.

**Features**:
- Analyzes current template distribution across 62 categories
- Identifies gaps in template coverage
- Generates JSON reports
- Compiles newly added templates
- Integrates with auto_publish.sh for GitHub publishing

**Usage**:

```bash
# Analyze template gaps and generate report
python3 scripts/generate_and_publish.py --analyze

# Compile newly added templates (without PDFs)
python3 scripts/generate_and_publish.py --compile-new

# Publish changes to GitHub
python3 scripts/generate_and_publish.py --publish
```

**Sample Output**:
```
Current Status:
  Total templates: 194
  Total categories: 62
  Total gaps: 193

Top 10 categories needing templates:
   1. mathematics                    - needs 7 more (current: 3/10)
   2. computer-science               - needs 6 more (current: 2/8)
   3. thermodynamics                 - needs 6 more (current: 0/6)
   4. chemistry                      - needs 5 more (current: 1/6)
   5. data-science                   - needs 5 more (current: 3/8)
```

## Workflow Integration

### Full Automated Workflow

The typical workflow for adding new templates and publishing them:

```bash
# 1. Clean the repository (optional but recommended)
./scripts/cleanup_repo.sh

# 2. Generate new templates (use existing generation scripts)
cd latex-templates
python3 generate_remaining_templates.py

# 3. Analyze what was created
cd /home/user/computational-pipeline
python3 scripts/generate_and_publish.py --analyze

# 4. Compile new templates
python3 scripts/generate_and_publish.py --compile-new

# 5. Publish to GitHub
./scripts/auto_publish.sh once

# OR use continuous monitoring
./scripts/auto_publish.sh monitor
```

### Background Monitoring

For continuous operation, run auto_publish.sh in the background:

```bash
# Start monitoring in background
nohup ./scripts/auto_publish.sh monitor > /tmp/auto_publish.log 2>&1 &

# Check status
tail -f /tmp/auto_publish.log

# Stop monitoring
pkill -f "auto_publish.sh monitor"
```

## Template Generation Strategy

Based on the gap analysis, focus on these priority categories:

### High Priority (5+ templates needed):
1. **Mathematics** (3/10) - needs 7 more
2. **Computer Science** (2/8) - needs 6 more
3. **Thermodynamics** (0/6) - needs 6 more
4. **Chemistry** (1/6) - needs 5 more
5. **Data Science** (3/8) - needs 5 more
6. **Machine Learning** (5/10) - needs 5 more

### Medium Priority (3-4 templates needed):
- Electrical Engineering (2/7)
- Economics (2/7)
- Statistics (3/8)
- Numerical Methods (4/8)
- Mechanical Engineering (5/8)

### Categories at Target:
- Optics (6/6) ✓

## Git Ignore Rules

The enhanced .gitignore excludes build artifacts while preserving:
- Source files: *.tex, *.Rnw, *.bib
- Compiled outputs: *.pdf (in output/)
- Documentation: *.md, *.txt
- Scripts: *.sh, *.py
- Configuration: Makefile, latexmkrc

**Excluded**:
- All LaTeX auxiliary files
- PythonTeX/SageTeX/Knitr temporary files
- Python cache and virtual environments
- IDE files (.vscode/, .idea/)
- OS temporary files
- Log files

## Best Practices

### Before Committing
1. Run cleanup_repo.sh to remove artifacts
2. Verify changes with `git status`
3. Check that only source and PDF files are staged

### When Adding Templates
1. Create .tex file in appropriate templates/ subdirectory
2. Compile locally first to verify
3. Use auto_publish.sh to commit and push
4. Check GitHub to verify PDFs are included

### Repository Maintenance
- Run cleanup weekly or after major compilation runs
- Monitor disk usage: `du -sh latex-templates/`
- Generate analysis reports to track progress
- Keep generation_report.json for historical tracking

## Troubleshooting

### auto_publish.sh Issues

**Problem**: "Failed to push to GitHub"
```bash
# Solution: Pull and rebase first
git pull --rebase origin main
./scripts/auto_publish.sh once
```

**Problem**: No changes detected
```bash
# Check git status manually
git status
# Verify file permissions
ls -la latex-templates/templates/
```

### Compilation Issues

**Problem**: Templates fail to compile
```bash
# Check logs in latex-templates/logs/
cat latex-templates/logs/compilation.log

# Try manual compilation
cd latex-templates/templates/category-name/
pdflatex -interaction=nonstopmode template.tex
```

### Cleanup Issues

**Problem**: Files still present after cleanup
```bash
# Verify file patterns
find latex-templates -name "*.aux" | head -10

# Check file permissions
ls -la latex-templates/templates/
```

## Monitoring and Metrics

### Key Metrics
- Total templates: 194-201
- Total categories: 62
- Compiled PDFs: 515
- Total gaps: ~193 (based on target distribution)
- Repository size: ~180MB

### Progress Tracking
```bash
# Generate current status
python3 scripts/generate_and_publish.py --analyze

# View detailed report
cat latex-templates/generation_report.json | jq .

# Count templates per category
find latex-templates/templates -name "*.tex" | \
  cut -d/ -f4 | sort | uniq -c | sort -rn
```

## Integration with CI/CD

The automation scripts are designed to work with continuous integration:

```yaml
# Example GitHub Actions workflow
name: Auto-compile and publish
on:
  push:
    paths:
      - 'latex-templates/templates/**/*.tex'
jobs:
  compile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Compile templates
        run: python3 scripts/generate_and_publish.py --compile-new
      - name: Publish
        run: ./scripts/auto_publish.sh once
```

## Security Considerations

- GitHub PAT credentials are stored securely via git credential helper
- No credentials are included in scripts or committed files
- .gitignore includes patterns for .env, credentials.json, *.key, *.pem
- Build artifacts are excluded to prevent accidental data exposure

## Performance Optimization

### Compilation Performance
- PythonTeX uses caching (pythontex-files-*)
- Incremental compilation only rebuilds changed templates
- Background compilation during generation
- Parallel compilation possible with GNU parallel

### Publishing Performance
- Single check mode for on-demand publishing
- Intelligent commit message generation
- Batched file additions (git add)
- Status checking before unnecessary operations

## Future Enhancements

Potential improvements to the automation:

1. **Parallel Compilation**: Use GNU parallel for faster compilation
2. **Webhook Integration**: Trigger builds on external events
3. **PDF Validation**: Verify PDF quality after compilation
4. **Template Testing**: Automated syntax and compilation testing
5. **Metrics Dashboard**: Web dashboard for tracking progress
6. **Smart Scheduling**: Compile during off-peak hours
7. **Notification System**: Email/Slack alerts on completion or errors
8. **Version Tagging**: Automatic semantic versioning

## Contact and Support

For issues or questions about the automation:
- Check this guide first
- Review script comments for detailed explanations
- Check git logs: `git log --oneline --graph`
- Review GitHub Actions logs (if enabled)

## License

Scripts are part of the computational-pipeline repository and follow the same license as the main project.
