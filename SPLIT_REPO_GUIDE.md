# Split Repository Implementation Guide

## Overview

This computational pipeline uses a **dual-repository architecture** to separate public educational content from private workflow automation.

## Architecture

### Repository 1: computational-pipeline (PUBLIC)
- **URL**: https://github.com/Ok-landscape/computational-pipeline
- **Remote name**: `origin`
- **Content**: Published notebooks only
- **Purpose**: Public sharing of educational computational notebooks

### Repository 2: computational-pipeline-outputs (PRIVATE)
- **URL**: https://github.com/Ok-landscape/computational-pipeline-outputs
- **Remote name**: `outputs`
- **Content**: Outputs, orchestration files, templates, workflow code
- **Purpose**: Private workflow automation and social media content

## Directory Structure

```
~/computational_pipeline/
├── .git/                          # Git repository (dual remotes)
├── .gitignore                     # Public repo ignore rules
├── .gitignore-outputs             # Private repo ignore rules
├── README.md                      # Public documentation (tracked by origin)
├── notebooks/
│   ├── drafts/                    # NOT tracked (temporary)
│   └── published/                 # Tracked by BOTH repos
│       └── *.ipynb                # Public notebooks
├── output/                        # Tracked by outputs repo ONLY
│   └── social_posts/
│       └── *_posts.txt
├── orchestration/                 # Tracked by outputs repo ONLY
│   ├── logs.jsonl
│   └── state.json
├── templates/                     # Tracked by outputs repo ONLY
│   ├── latex_header.tex
│   └── social_guidelines.md
├── workflow.py                    # Tracked by outputs repo ONLY
└── system_prompts.md              # Tracked by outputs repo ONLY
```

## Git Remote Configuration

```bash
# View remotes
git remote -v

# Output:
# origin   https://github.com/Ok-landscape/computational-pipeline.git (fetch)
# origin   https://github.com/Ok-landscape/computational-pipeline.git (push)
# outputs  https://github.com/Ok-landscape/computational-pipeline-outputs.git (fetch)
# outputs  https://github.com/Ok-landscape/computational-pipeline-outputs.git (push)
```

## .gitignore Strategy

### Main Repo .gitignore (Public)
Ignores everything EXCEPT:
- `notebooks/published/*.ipynb`
- `README.md`
- `.gitignore`

### Private Repo .gitignore-outputs
Ignores:
- `notebooks/` (redundant with public repo)
- Standard development files (cache, env, IDE)

## Workflow Integration

The `workflow.py` file includes a `push_to_outputs_repo()` function that:

1. Checks if `outputs` remote exists
2. Stages files: `output/`, `orchestration/`, `templates/`, `workflow.py`, `system_prompts.md`
3. Commits with timestamp
4. Pushes to `outputs` remote (private repo)

This function is called automatically at the end of the pipeline (Stage 5).

## Manual Operations

### Push to Public Repo (notebooks only)
```bash
cd ~/computational_pipeline
git add notebooks/published/*.ipynb
git commit -m "Add new published notebook"
git push origin main
```

### Push to Private Repo (outputs)
```bash
cd ~/computational_pipeline
git add -f output/ orchestration/ templates/ workflow.py
git commit -m "Update outputs"
git push outputs main
```

Note: Use `-f` to force-add files that are ignored by main .gitignore

### Check Status for Both Repos
```bash
# Check what would go to public repo
git status

# Check what's in private repo
gh repo view Ok-landscape/computational-pipeline-outputs
```

## Automated Pipeline Behavior

When `workflow.py` runs:

1. **Stage 1-2**: Draft and validate notebook
2. **Stage 3**: Push notebook to public repo (`origin`)
   - AGENT_PUBLISHER commits to `notebooks/published/`
   - Pushes to origin/main
3. **Stage 4**: Generate social media content
   - Saves to `output/social_posts/`
4. **Stage 5**: Push outputs to private repo
   - Calls `push_to_outputs_repo()`
   - Commits all private content
   - Pushes to outputs/main

## Security Considerations

### What's Public
- Published notebooks (`.ipynb` files)
- README.md
- Basic documentation

### What's Private
- Social media posts (may contain strategy info)
- Orchestration logs (contain execution history)
- Workflow code (automation implementation)
- System prompts (agent instructions)
- Templates (internal guidelines)

### Secrets
Neither repository should contain:
- API keys
- Authentication tokens
- `.env` files
- Credentials

Both `.gitignore` files exclude these by default.

## Troubleshooting

### Files Not Pushing to Outputs Repo

Check if files are ignored:
```bash
git status  # Should show files as untracked
git add -f output/  # Force add to override .gitignore
```

### Wrong Remote

Check which remote you're pushing to:
```bash
git remote -v
git push origin main    # Public repo
git push outputs main   # Private repo
```

### Merge Conflicts

If both repos track the same file (like notebooks), resolve conflicts:
```bash
git fetch origin
git fetch outputs
git merge origin/main
# Resolve conflicts if any
git push origin main
git push outputs main
```

## Testing the Setup

### Test File
```python
# test_dual_push.py
from workflow import push_to_outputs_repo
import os
import datetime

# Create test file
with open('output/test.txt', 'w') as f:
    f.write(f"Test at {datetime.datetime.now()}")

# Push to private repo
push_to_outputs_repo()
```

### Verify
```bash
gh repo view Ok-landscape/computational-pipeline-outputs
# Should show recent commit with test file
```

## Benefits of Split Approach

1. **Clean Public Repo**: Only polished notebooks visible to public
2. **Private Automation**: Workflow code and tools remain private
3. **Flexible Access**: Share public repo widely, restrict private repo
4. **Separation of Concerns**: Content vs. tooling
5. **Easy Collaboration**: Public notebooks can be forked without exposing automation

## Migration from Single Repo

If migrating from a single repository:

1. Create private repo: `gh repo create <name> --private`
2. Add remote: `git remote add outputs <url>`
3. Update `.gitignore` to exclude private content from origin
4. Force-add private content: `git add -f output/ orchestration/`
5. Push to private repo: `git push outputs main`
6. Remove private content from public repo history (optional, advanced)

## Maintenance

### Regular Tasks

1. **Keep repos in sync**
   - Public repo gets new notebooks
   - Private repo gets updated outputs

2. **Monitor repo sizes**
   - Public: Should remain small (notebooks only)
   - Private: May grow with output files

3. **Periodic cleanup**
   - Archive old logs in `orchestration/`
   - Compress old social posts

## Resources

- Main repo: https://github.com/Ok-landscape/computational-pipeline
- Private repo: https://github.com/Ok-landscape/computational-pipeline-outputs
- GitHub CLI docs: https://cli.github.com/manual/

## Implementation Date

- **Setup Date**: 2025-11-24
- **Implementation**: Option 2 (Split Repository)
- **Status**: Active
