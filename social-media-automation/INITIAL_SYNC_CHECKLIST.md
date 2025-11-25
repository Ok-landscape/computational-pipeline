# Initial Dual-Repository Sync Checklist

**Date:** 2025-11-25
**Purpose:** One-time setup to bring both repositories into proper sync

## Current Situation Summary

### Public Repo Issues
- ✅ Has 2 unpushed commits (need to push)
- ❌ Missing entire social-media-automation codebase (30+ Python files)
- ❌ Missing all documentation (14+ markdown files)
- ❌ Missing configuration files (.env.example, requirements.txt, setup.sh)
- ⚠️ Has some notebook output artifacts that shouldn't be there

### Private Repo Status
- ✅ Up to date with remote
- ✅ Has all executed notebooks with outputs
- ✅ Has generated social media posts
- ✅ Has orchestration logs

## Initial Sync Plan

### Phase 1: Prepare Public Repository

#### 1.1 Push Pending Commits
```bash
cd /home/user/computational-pipeline
git status
git log --oneline -3
git push origin main
```
**Status:** [ ] Complete

#### 1.2 Update .gitignore
- ✅ DONE - Updated to exclude:
  - .env and secrets
  - repo-data/ directory
  - Generated outputs
  - Test files

**Status:** [✅] Complete

#### 1.3 Verify .gitignore Working
```bash
cd /home/user/computational-pipeline
git status
# Should NOT show:
# - .env
# - social-media-automation/repo-data/
# - social-media-automation/data/
# - social-media-automation/media/
```
**Status:** [ ] Complete

### Phase 2: Add Social Media Automation Code to Public Repo

#### 2.1 Add Python Files
```bash
cd /home/user/computational-pipeline
git add social-media-automation/*.py
```

Files to be added (30+ files):
- batch_quality_check.py
- check_notebook_outputs.py
- content_audit.py
- content_generator.py
- convert_latex_to_unicode.py
- debug_token.py
- delete_post.py
- duplicate_content_handler.py
- enhanced_scheduler.py
- find_missing_notebooks.py
- fix_latex_posts.py
- image_quality_validator.py
- media_extractor.py
- notebook_content_extractor.py
- notebook_executor.py
- notebook_scanner.py
- page_router.py
- post_text_parser.py
- pre_publish_validator.py
- preview_post.py
- run_automation.py
- simple_queue_check.py
- smart_scheduler.py
- social_publisher.py
- template_scanner.py
- test_facebook_token.py
- test_integration.py
- test_post_generation.py
- test_single_post.py
- test_specific_notebook.py
- unified_queue_manager.py
- validate_queue.py

**Status:** [ ] Complete

#### 2.2 Add Documentation Files
```bash
cd /home/user/computational-pipeline
git add social-media-automation/*.md
```

Files to be added (14+ files):
- README.md
- SETUP.md
- QUICK_START.md
- ARCHITECTURE.md
- OPERATIONS.md
- QUALITY_STANDARDS.md
- NOTEBOOK_PLOT_NAMING_STANDARD.md
- DUAL_SYSTEM_GUIDE.md
- IMPLEMENTATION_SUMMARY.md
- IMPLEMENTATION_REPORT.md
- INTEGRATION_SUMMARY.md
- INCIDENT_REPORT_2025-11-25.md
- POST_FAILURE_DIAGNOSIS.md
- REFRESH_FACEBOOK_TOKEN.md
- DUAL_REPO_SYNC_ANALYSIS.md (NEW)
- DUAL_REPO_WORKFLOW.md (NEW)
- INITIAL_SYNC_CHECKLIST.md (this file)

**Status:** [ ] Complete

#### 2.3 Add Configuration Files
```bash
cd /home/user/computational-pipeline
git add social-media-automation/.env.example
git add social-media-automation/requirements.txt
git add social-media-automation/setup.sh
```

**Status:** [ ] Complete

#### 2.4 Add Sync Scripts
```bash
cd /home/user/computational-pipeline
git add social-media-automation/sync_to_public.sh
git add social-media-automation/sync_to_private.sh
git add social-media-automation/sync_both.sh
```

**Status:** [ ] Complete

#### 2.5 Commit and Push
```bash
cd /home/user/computational-pipeline
git status
git commit -m "Add complete social media automation system

This commit adds the full social media automation codebase to the public repository:

- 30+ Python modules for automation pipeline
- Comprehensive documentation (setup, architecture, operations)
- Configuration templates and setup scripts
- Dual-repository sync utilities

The system automates:
- Notebook execution and validation
- Content extraction from notebooks
- Social media post generation
- Facebook/Instagram posting
- Quality validation and error handling

Documentation includes:
- Setup and installation guides
- Architecture and system design
- Operations and maintenance procedures
- Quality standards and best practices
- Dual-repository workflow management

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

**Status:** [ ] Complete

### Phase 3: Verify Public Repository

#### 3.1 Check Repository on GitHub
Visit: https://github.com/Ok-landscape/computational-pipeline

Verify visible:
- [ ] /social-media-automation/ directory
- [ ] Python files are present
- [ ] Documentation files are present
- [ ] README.md is readable

Verify NOT visible:
- [ ] .env file (secrets)
- [ ] repo-data/ directory
- [ ] Generated output files

**Status:** [ ] Complete

#### 3.2 Clone Test (Optional but Recommended)
```bash
cd /tmp
git clone https://github.com/Ok-landscape/computational-pipeline.git test-clone
cd test-clone
ls -la social-media-automation/
# Should see Python files and docs
# Should NOT see .env or repo-data/
cd ..
rm -rf test-clone
```

**Status:** [ ] Complete

### Phase 4: Verify Private Repository

#### 4.1 Check Private Repo Status
```bash
cd /home/user/computational-pipeline/social-media-automation/repo-data
git status
git log --oneline -5
```

Should be clean and up to date.

**Status:** [ ] Complete

#### 4.2 Verify Private Content Intact
```bash
cd /home/user/computational-pipeline/social-media-automation/repo-data
ls -la notebooks/published/*.png  # Should see plots
ls -la output/social_posts/       # Should see post files
ls -la orchestration/              # Should see logs
```

**Status:** [ ] Complete

### Phase 5: Document and Finalize

#### 5.1 Update This Checklist
Mark all items complete and note any issues.

**Status:** [ ] Complete

#### 5.2 Create Summary Report
Document what was synced and final state.

**Status:** [ ] Complete

#### 5.3 Test Sync Scripts
Try using the new sync scripts for a test commit:

```bash
cd /home/user/computational-pipeline/social-media-automation
# Make a small change
echo "# Test" >> README.md
# Test sync
./sync_to_public.sh "Test sync script"
# Verify it worked
cd /home/user/computational-pipeline
git log --oneline -1
# Undo the test
git reset --soft HEAD~1
git checkout README.md
```

**Status:** [ ] Complete

## Post-Sync Checklist

After completing all phases:

- [ ] Public repo has all code and documentation
- [ ] Public repo has NO secrets or sensitive data
- [ ] Public repo has NO generated outputs (except what's appropriate)
- [ ] Private repo still has all outputs intact
- [ ] Sync scripts are executable and working
- [ ] Documentation is clear and complete
- [ ] Both repositories are pushed and up to date

## Rollback Plan (If Needed)

If something goes wrong:

1. **Don't panic** - Git makes everything recoverable
2. **Stop immediately** - Don't make more commits
3. **Assess the damage** - What went wrong?
4. **Rollback options:**
   ```bash
   # Undo last commit (keep changes)
   git reset --soft HEAD~1

   # Undo last commit (discard changes)
   git reset --hard HEAD~1

   # Undo push (DANGEROUS - use with caution)
   git push origin main --force
   ```

## Success Criteria

When complete, you should be able to:

1. ✅ View the automation code on GitHub (public)
2. ✅ Read the documentation on GitHub (public)
3. ✅ Clone the public repo and have a working codebase
4. ✅ Run the sync scripts to commit to either repo
5. ✅ Have all outputs safe in the private repo
6. ✅ Have no secrets exposed in the public repo

## Notes and Issues

(Document any problems encountered during sync)

---

**Next Steps After Initial Sync:**

1. Use sync_to_public.sh for code/doc changes
2. Use sync_to_private.sh for output changes
3. Use sync_both.sh when both are affected
4. Follow DUAL_REPO_WORKFLOW.md for ongoing maintenance
5. Review DUAL_REPO_SYNC_ANALYSIS.md for strategy details
