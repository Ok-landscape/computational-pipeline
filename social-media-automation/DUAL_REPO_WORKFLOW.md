# Dual Repository Workflow Guide

**Last Updated:** 2025-11-25

## Overview

This guide documents the workflow for maintaining consistent commits across both GitHub repositories:

- **Public:** https://github.com/Ok-landscape/computational-pipeline
- **Private:** https://github.com/Ok-landscape/computational-pipeline-outputs

## Repository Purposes

### Public Repository (computational-pipeline)
**Purpose:** Share code, documentation, and templates with the community

**Contains:**
- Social media automation Python code
- Documentation (README, setup guides, architecture)
- LaTeX templates
- Clean notebooks (without execution outputs)
- Configuration examples (.env.example, requirements.txt)

**Does NOT contain:**
- Actual .env with secrets
- Executed notebooks with outputs
- Generated social media posts
- Private orchestration logs

### Private Repository (computational-pipeline-outputs)
**Purpose:** Store execution results, outputs, and generated content

**Contains:**
- Executed notebooks WITH outputs
- Generated plots and images
- Social media post text files
- Orchestration logs and state
- Complete workflow data

## Content Distribution Rules

| Content Type | Public | Private | Script to Use |
|--------------|--------|---------|---------------|
| Python source code (.py) | ✅ | ❌ | sync_to_public.sh |
| Documentation (.md) | ✅ | ✅* | sync_to_public.sh (or both) |
| Configuration examples | ✅ | ❌ | sync_to_public.sh |
| Actual .env with secrets | ❌ | ❌ | (never commit) |
| Notebooks (clean) | ✅ | ❌ | sync_to_public.sh |
| Notebooks (with outputs) | ❌ | ✅ | sync_to_private.sh |
| Generated plots/images | ❌ | ✅ | sync_to_private.sh |
| Social media posts | ❌ | ✅ | sync_to_private.sh |
| Orchestration logs | ❌ | ✅ | sync_to_private.sh |

*Some documentation may be in both repos if it's user-facing

## Sync Scripts

Three helper scripts are provided in `/home/user/computational-pipeline/social-media-automation/`:

### 1. sync_to_public.sh
Commits code and documentation to the public repository.

**Usage:**
```bash
cd /home/user/computational-pipeline/social-media-automation
./sync_to_public.sh "Your commit message"
```

**What it does:**
- Adds all .py files (excluding repo-data, __pycache__)
- Adds all .md documentation files
- Adds configuration examples (.env.example, requirements.txt, setup.sh)
- Commits and pushes to public repo

**When to use:**
- After creating/modifying Python code
- After updating documentation
- After adding new features to the automation system

### 2. sync_to_private.sh
Commits outputs and execution results to the private repository.

**Usage:**
```bash
cd /home/user/computational-pipeline/social-media-automation
./sync_to_private.sh "Your commit message"
```

**What it does:**
- Adds executed notebooks (.ipynb with outputs)
- Adds generated plots (.png, .pdf)
- Adds social media post files (.txt)
- Adds orchestration state and logs
- Commits and pushes to private repo

**When to use:**
- After executing notebooks
- After generating new social media posts
- After automation runs produce new content

### 3. sync_both.sh
Commits to BOTH repositories in sequence.

**Usage:**
```bash
cd /home/user/computational-pipeline/social-media-automation
./sync_both.sh "Public message" "Private message"

# Or use same message for both:
./sync_both.sh "Updated feature X"
```

**What it does:**
- Runs sync_to_public.sh with first message
- Runs sync_to_private.sh with second message (or same if not provided)

**When to use:**
- After changes that affect both code AND outputs
- When you've made improvements that generate new results
- For comprehensive updates to the entire system

## Common Workflows

### Workflow 1: Adding a New Python Module

```bash
# 1. Create your new module
cd /home/user/computational-pipeline/social-media-automation
vim new_feature.py

# 2. Test it
python new_feature.py

# 3. Document it
vim README.md  # Add documentation

# 4. Sync to public repo
./sync_to_public.sh "Add new feature: enhanced post validation"
```

### Workflow 2: Executing Notebooks and Generating Posts

```bash
# 1. Execute notebooks (from your automation)
python notebook_executor.py

# 2. This generates outputs in repo-data/notebooks/published/
# and social posts in repo-data/output/social_posts/

# 3. Sync to private repo
./sync_to_private.sh "Execute notebooks and generate posts for 2025-11-25"
```

### Workflow 3: Comprehensive Update (Code + Outputs)

```bash
# 1. Made code changes
vim content_generator.py

# 2. Updated documentation
vim ARCHITECTURE.md

# 3. Ran automation and generated new outputs
python run_automation.py

# 4. Sync both repos
./sync_both.sh "Improve content generator with better LaTeX handling" "Update outputs with improved LaTeX conversion"
```

### Workflow 4: Documentation Update Only

```bash
# 1. Update docs
vim SETUP.md

# 2. Sync to public (users need this)
./sync_to_public.sh "Update setup instructions for clarity"

# OR if it's internal documentation, manually commit to private repo:
cd /home/user/computational-pipeline/social-media-automation/repo-data
git add system_prompts.md
git commit -m "Update internal system prompts"
git push origin main
```

## Manual Sync (When Scripts Don't Fit)

### Public Repo Manual Commit
```bash
cd /home/user/computational-pipeline
git add social-media-automation/specific_file.py
git commit -m "Your message

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

### Private Repo Manual Commit
```bash
cd /home/user/computational-pipeline/social-media-automation/repo-data
git add output/social_posts/specific_post.txt
git commit -m "Your message

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
git push origin main
```

## Best Practices

### 1. Commit Frequently
- Don't let changes pile up
- Smaller commits are easier to review and debug
- Commit logical units of work

### 2. Use Descriptive Messages
- Bad: "Update files"
- Good: "Fix LaTeX equation rendering in post generator"
- Great: "Fix LaTeX equation rendering in post generator - convert \frac to Unicode"

### 3. Review Before Pushing
- Check git status before running sync scripts
- Verify no secrets in staged files
- Ensure correct repository target

### 4. Keep Repos Synchronized
- If code changes might affect outputs, update both
- Don't let one repo get too far ahead

### 5. Never Commit Secrets
- Actual .env file
- API tokens
- Personal access tokens
- Use .env.example for public reference

## Checking Repository Status

### Check Public Repo Status
```bash
cd /home/user/computational-pipeline
git status
git log --oneline -5
```

### Check Private Repo Status
```bash
cd /home/user/computational-pipeline/social-media-automation/repo-data
git status
git log --oneline -5
```

### Verify Both Repos
```bash
# Quick status check script
echo "=== PUBLIC REPO ==="
cd /home/user/computational-pipeline
git status --short
echo ""
echo "=== PRIVATE REPO ==="
cd /home/user/computational-pipeline/social-media-automation/repo-data
git status --short
```

## Troubleshooting

### Issue: Script says "No changes to commit"
**Cause:** No files have been modified or added since last commit
**Solution:** This is normal - no action needed

### Issue: Merge conflict after pull
**Cause:** Changes made in multiple locations
**Solution:**
```bash
git pull origin main
# Resolve conflicts in files
git add resolved_file.py
git commit -m "Resolve merge conflict"
git push origin main
```

### Issue: Accidentally committed to wrong repo
**Cause:** Ran script in wrong directory
**Solution:**
```bash
# Undo last commit (but keep changes)
git reset --soft HEAD~1

# Or completely remove last commit
git reset --hard HEAD~1
git push origin main --force  # DANGEROUS - use with caution
```

### Issue: Forgot to push after commit
**Cause:** Committed locally but didn't push
**Solution:**
```bash
git push origin main
```

### Issue: Want to see what will be committed
**Cause:** Want to preview before committing
**Solution:**
```bash
# The scripts show this automatically, but manually:
git status
git diff --staged
```

## File Locations Reference

```
/home/user/computational-pipeline/
├── .git/                           # Public repo git metadata
├── notebooks/published/            # Clean notebooks (public)
├── latex-templates/
└── social-media-automation/
    ├── *.py                        # All Python code (public)
    ├── *.md                        # Documentation (public)
    ├── .env.example                # Config example (public)
    ├── .env                        # NEVER COMMIT - secrets
    ├── requirements.txt            # Dependencies (public)
    ├── setup.sh                    # Setup script (public)
    ├── sync_to_public.sh          # Sync script for public
    ├── sync_to_private.sh         # Sync script for private
    ├── sync_both.sh               # Sync script for both
    └── repo-data/                  # PRIVATE REPO CLONE
        ├── .git/                   # Private repo git metadata
        ├── notebooks/published/    # Notebooks WITH outputs (private)
        ├── output/social_posts/    # Generated posts (private)
        └── orchestration/          # Logs and state (private)
```

## Quick Reference Commands

```bash
# Sync code to public
cd /home/user/computational-pipeline/social-media-automation
./sync_to_public.sh "message"

# Sync outputs to private
cd /home/user/computational-pipeline/social-media-automation
./sync_to_private.sh "message"

# Sync both
cd /home/user/computational-pipeline/social-media-automation
./sync_both.sh "public message" "private message"

# Check public status
cd /home/user/computational-pipeline && git status

# Check private status
cd /home/user/computational-pipeline/social-media-automation/repo-data && git status

# View recent commits (public)
cd /home/user/computational-pipeline && git log --oneline -10

# View recent commits (private)
cd /home/user/computational-pipeline/social-media-automation/repo-data && git log --oneline -10
```

## Emergency Procedures

### If You Committed Secrets to Public Repo
1. **DO NOT PUSH** if you haven't already
2. Reset the commit: `git reset --soft HEAD~1`
3. Remove the secret file: `git rm --cached .env`
4. Add to .gitignore: `echo ".env" >> .gitignore`
5. Commit again without secrets

If already pushed:
1. Immediately revoke/rotate the exposed credentials
2. Use git filter-branch or BFG Repo-Cleaner to remove from history
3. Force push cleaned history
4. Notify affected parties

### If Repos Get Out of Sync
1. Identify what's different
2. Decide which is the "source of truth"
3. Manually sync the missing content
4. Document what happened to prevent recurrence

## Support and Questions

For questions about this workflow:
1. Check this guide first
2. Review DUAL_REPO_SYNC_ANALYSIS.md for strategy details
3. Check git documentation: https://git-scm.com/doc
4. Review script source code - they're well-commented

---

**Remember:** The goal is to keep your public repo useful for others while keeping private outputs secure. When in doubt, commit to private first, then selectively promote to public.
