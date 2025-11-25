# Dual Repository Sync Analysis and Strategy

**Date:** 2025-11-25
**Analyst:** Claude Code Orchestrator

## Executive Summary

This document provides a comprehensive analysis of the current dual-repository structure and proposes a robust strategy for maintaining consistent commits across both the public and private GitHub repositories.

---

## Current Repository Status

### 1. Public Repository
- **URL:** https://github.com/Ok-landscape/computational-pipeline
- **Location:** /home/user/computational-pipeline/
- **Branch:** main
- **Status:** 2 commits ahead of origin/main (not pushed)
- **Last Commit:** 46a1591 "Update notebook to use descriptive plot naming"

### 2. Private Repository
- **URL:** https://github.com/Ok-landscape/computational-pipeline-outputs
- **Location:** /home/user/computational-pipeline/social-media-automation/repo-data/
- **Branch:** main
- **Status:** Up to date with origin/main
- **Last Commit:** 35f32f8 "Fix: Proper display control for finite_element_method_heat_transfer.ipynb"

---

## Critical Findings

### Issue 1: Massive Content Divergence

The public repository is SEVERELY out of sync with actual work:

**Missing from Public Repo (all untracked):**
- Entire social-media-automation codebase (30+ Python files)
- All documentation (14+ markdown files)
- Configuration files (.env.example, requirements.txt, setup.sh)
- Data directories and extracted content

**This means:**
- All social media automation work is NOT in the public repository
- Recent documentation improvements are NOT public
- The public repo appears to only have notebooks and latex-templates

### Issue 2: Private Repo Has Active Automation

The private repository contains:
- Notebooks with outputs
- Social media post text files (output/social_posts/)
- Orchestration logs and state tracking
- LaTeX templates
- System prompts and workflow definitions

### Issue 3: Unclear Repository Strategy

Currently there's confusion about:
- What content belongs where?
- Should repos be mirrors or have different purposes?
- What's the commit workflow?

---

## Recommended Repository Strategy

### Strategy: Separation of Public Code vs. Private Outputs

**Public Repository (computational-pipeline):**
- Purpose: Shareable codebase, documentation, templates
- Contents:
  - /social-media-automation/ (ALL Python code)
  - /social-media-automation/*.md (documentation)
  - /latex-templates/ (templates)
  - /notebooks/published/ (notebooks WITHOUT outputs for cleanliness)
  - Configuration examples (.env.example, requirements.txt, setup.sh)

**Private Repository (computational-pipeline-outputs):**
- Purpose: Generated content, outputs, executed notebooks, automation state
- Contents:
  - /notebooks/published/ (notebooks WITH outputs)
  - /output/social_posts/ (generated social media content)
  - /orchestration/ (logs, state tracking)
  - /latex-templates/ (possibly shared)
  - Workflow and system prompts

### Content Distribution Matrix

| Content Type | Public | Private | Notes |
|--------------|--------|---------|-------|
| Python source code | YES | NO | Share the automation system |
| Documentation | YES | YES | Public gets user-facing docs, private gets all |
| Notebooks (no outputs) | YES | NO | Clean reference notebooks |
| Notebooks (with outputs) | NO | YES | Execution results, plots |
| Social media posts | NO | YES | Generated content |
| LaTeX templates | YES | YES | Both for different uses |
| Configuration (.env) | Example only | Real values | Security |
| Orchestration logs | NO | YES | Internal tracking |

---

## Identified Content Gaps

### Public Repo Missing (HIGH PRIORITY):

1. **Social Media Automation System** (0/30+ files)
   - All .py files in social-media-automation/
   - Would make the public repo actually useful

2. **Documentation** (0/14 files)
   - README.md
   - SETUP.md
   - QUICK_START.md
   - ARCHITECTURE.md
   - OPERATIONS.md
   - QUALITY_STANDARDS.md
   - NOTEBOOK_PLOT_NAMING_STANDARD.md
   - And 7 more implementation/guide documents

3. **Configuration Templates**
   - .env.example
   - requirements.txt
   - setup.sh

4. **Critical Issue:** Public repo has 2 unpushed commits
   - Need to push these first before adding new content

### Private Repo Status: GOOD
- Has recent updates
- Has notebook outputs
- Has generated social posts
- Has orchestration state

---

## Immediate Action Plan

### Phase 1: Resolve Public Repo State (CRITICAL)

1. **Push pending commits**
   ```bash
   cd /home/user/computational-pipeline
   git push origin main
   ```

2. **Add social-media-automation code to public repo**
   - Add all Python files
   - Add documentation files
   - Add configuration examples
   - Exclude: .env, repo-data/, data/, media/, extracted_images/

3. **Update .gitignore for public repo**
   - Ensure sensitive files excluded
   - Ensure output directories excluded
   - Ensure repo-data/ excluded (it's the private repo clone!)

### Phase 2: Establish Sync Workflow

**For Code/Documentation Changes:**
1. Make changes in /home/user/computational-pipeline/social-media-automation/
2. Commit to public repo (code + docs)
3. If changes affect outputs, also update private repo

**For Notebook Execution:**
1. Execute notebooks (generates outputs)
2. Commit to private repo only (notebooks with outputs)

**For Generated Content:**
1. Social media posts, plots, etc.
2. Commit to private repo only

### Phase 3: Create Automation Scripts

Create helper scripts to manage dual commits where appropriate.

---

## Proposed File Structure

### Public Repo (.gitignore additions needed):
```
computational-pipeline/
├── .gitignore (UPDATE: exclude outputs, data, private content)
├── notebooks/
│   └── published/ (clean notebooks, no outputs)
├── latex-templates/
│   └── templates/
└── social-media-automation/
    ├── README.md
    ├── SETUP.md
    ├── ARCHITECTURE.md
    ├── (all other .md docs)
    ├── (all .py files)
    ├── requirements.txt
    ├── setup.sh
    └── .env.example
    (EXCLUDE: .env, repo-data/, data/, media/, *.pyc, __pycache__)
```

### Private Repo (current structure is good):
```
computational-pipeline-outputs/
├── notebooks/
│   └── published/ (WITH outputs and plots)
├── output/
│   └── social_posts/
├── orchestration/
│   ├── logs.jsonl
│   └── state.json
├── latex-templates/
├── system_prompts.md
└── workflow.py
```

---

## Risks and Mitigations

### Risk 1: Accidental Exposure of Secrets
**Mitigation:**
- Update .gitignore in public repo BEFORE adding files
- Never commit actual .env file to public
- Review each commit before pushing

### Risk 2: Repository Confusion
**Mitigation:**
- Clear documentation (this file)
- Consistent commit messages indicating which repo
- Scripts that make repo target explicit

### Risk 3: Content Drift
**Mitigation:**
- Regular audits (weekly/monthly)
- Automated checks for critical file presence
- Clear ownership model (code=public, outputs=private)

---

## Success Metrics

After implementation:
1. Public repo has complete, usable social-media-automation system
2. Public repo has comprehensive documentation
3. Private repo continues to receive output updates
4. No secrets in public repo
5. Clear separation of concerns
6. Both repos actively maintained

---

## Next Steps

1. Review and approve this strategy
2. Execute Phase 1 (fix public repo state)
3. Create sync automation scripts
4. Document the workflow for future use
5. Establish monitoring/audit process

---

## Questions to Resolve

1. Should notebooks be in BOTH repos (clean in public, with outputs in private)?
   - Recommendation: YES

2. Should LaTeX templates be in BOTH repos?
   - Recommendation: YES (they're source files)

3. Should documentation be duplicated or split?
   - Recommendation: Public gets user-facing, private gets everything

4. How to handle future automation runs?
   - Recommendation: Outputs always go to private, code updates go to public
