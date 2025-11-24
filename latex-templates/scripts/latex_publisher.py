#!/usr/bin/env python3
"""
File: latex_publisher.py
Purpose: Automated Git publishing for LaTeX template collection
Description: Commits source .tex files and compiled PDFs, pushes to GitHub
Adapted for: latex-templates repository structure
"""

import subprocess
import os
import sys
import datetime
import json
from pathlib import Path

# Configuration - adapted for latex-templates structure
BASE_DIR = Path("/home/user/latex-templates")
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"
STATE_FILE = BASE_DIR / "publishing_state.json"

# Git configuration (will be set during setup)
REPO_URL = "https://github.com/YOUR_USERNAME/latex-templates.git"  # Update this

def log(message, level="INFO"):
    """Print and log message."""
    timestamp = datetime.datetime.now().isoformat()
    formatted_msg = f"[{level}] {timestamp} - {message}"
    print(formatted_msg)

    # Append to log file
    log_file = LOGS_DIR / "publishing.log"
    with open(log_file, 'a') as f:
        f.write(formatted_msg + "\n")

def save_state(stage, files):
    """Save current publishing state."""
    state = {
        "stage": stage,
        "files": files,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def find_template_files(pattern=None):
    """
    Find template files to publish.

    Args:
        pattern: Optional glob pattern (e.g., 'aerospace/*.tex')

    Returns:
        list: List of Path objects for .tex files
    """
    if pattern:
        files = list(TEMPLATES_DIR.glob(pattern))
    else:
        files = list(TEMPLATES_DIR.glob("**/*.tex"))

    return sorted(files)

def find_compiled_pdfs():
    """Find all PDFs in output directory."""
    if not OUTPUT_DIR.exists():
        return []
    return sorted(OUTPUT_DIR.glob("*.pdf"))

def git_add_commit_push(files_to_add, commit_message, dry_run=False):
    """
    Add files to git, commit, and push.

    Args:
        files_to_add: List of file paths (relative to BASE_DIR)
        commit_message: Commit message
        dry_run: If True, don't actually push

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        os.chdir(BASE_DIR)

        # Check git status
        result = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, "Git not initialized"

        # Add files
        log(f"Adding {len(files_to_add)} files to git")
        for file_path in files_to_add:
            result = subprocess.run(
                ["git", "add", str(file_path)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                log(f"Warning: Failed to add {file_path}", "WARN")

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )

        if result.returncode == 0:
            return True, "No changes to commit"

        # Commit
        log(f"Committing changes")
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Commit failed: {result.stderr}"

        if dry_run:
            return True, "Dry run: Changes committed locally only"

        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip() or "main"

        # Push
        log(f"Pushing to {branch}...")
        result = subprocess.run(
            ["git", "push", "origin", branch],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            if "authentication" in result.stderr.lower() or "denied" in result.stderr.lower():
                return False, "Authentication failed. Configure SSH keys or PAT."
            else:
                return False, f"Push failed: {result.stderr}"

        log("Successfully pushed to GitHub")
        return True, f"Successfully pushed to {branch}"

    except subprocess.TimeoutExpired:
        return False, "Git push timeout"
    except Exception as e:
        return False, f"Git operation failed: {str(e)}"

def publish_single_template(tex_file, include_pdf=True):
    """
    Publish a single template and its PDF.

    Args:
        tex_file: Path to .tex file
        include_pdf: Whether to include corresponding PDF

    Returns:
        bool: Success status
    """
    tex_path = Path(tex_file)

    if not tex_path.exists():
        log(f"Template not found: {tex_path}", "ERROR")
        return False

    # Get relative path from BASE_DIR
    try:
        rel_path = tex_path.relative_to(BASE_DIR)
    except ValueError:
        log(f"File not in base directory: {tex_path}", "ERROR")
        return False

    files_to_commit = [str(rel_path)]

    # Find corresponding PDF
    if include_pdf:
        basename = tex_path.stem
        pdf_path = OUTPUT_DIR / f"{basename}.pdf"

        if pdf_path.exists():
            files_to_commit.append(str(pdf_path.relative_to(BASE_DIR)))
            log(f"Including PDF: {pdf_path.name}")
        else:
            log(f"PDF not found: {pdf_path.name}", "WARN")

    # Create commit message
    commit_msg = f"""LaTeX: Add {tex_path.name}

- Template: {rel_path}
- Category: {tex_path.parent.name}
- Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated by automated LaTeX pipeline
"""

    # Publish
    log(f"Publishing {tex_path.name}")
    save_state("publishing", files_to_commit)

    success, message = git_add_commit_push(files_to_commit, commit_msg)

    if success:
        log(f"Successfully published: {tex_path.name}", "SUCCESS")
        save_state("complete", files_to_commit)
        return True
    else:
        log(f"Publishing failed: {message}", "ERROR")
        save_state("failed", files_to_commit)
        return False

def publish_batch(template_pattern="**/*.tex", include_pdfs=True, dry_run=False):
    """
    Publish multiple templates in batch.

    Args:
        template_pattern: Glob pattern for templates
        include_pdfs: Whether to include PDFs
        dry_run: If True, don't push to GitHub

    Returns:
        dict: Statistics about publishing
    """
    log(f"Starting batch publish: {template_pattern}")

    # Find templates
    templates = find_template_files(template_pattern)

    if not templates:
        log("No templates found", "WARN")
        return {"total": 0, "success": 0, "failed": 0}

    log(f"Found {len(templates)} templates")

    # Collect all files to commit
    files_to_commit = []

    for tex_file in templates:
        try:
            rel_path = tex_file.relative_to(BASE_DIR)
            files_to_commit.append(str(rel_path))
        except ValueError:
            continue

    # Add PDFs if requested
    if include_pdfs:
        pdfs = find_compiled_pdfs()
        log(f"Found {len(pdfs)} PDFs")

        for pdf_file in pdfs:
            try:
                rel_path = pdf_file.relative_to(BASE_DIR)
                files_to_commit.append(str(rel_path))
            except ValueError:
                continue

    if not files_to_commit:
        log("No files to commit", "WARN")
        return {"total": 0, "success": 0, "failed": 0}

    # Create commit message
    commit_msg = f"""LaTeX: Batch publish templates

- Templates: {len([f for f in files_to_commit if f.endswith('.tex')])}
- PDFs: {len([f for f in files_to_commit if f.endswith('.pdf')])}
- Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated by automated LaTeX pipeline
"""

    # Publish
    log(f"Publishing {len(files_to_commit)} files")
    save_state("batch_publishing", files_to_commit)

    success, message = git_add_commit_push(files_to_commit, commit_msg, dry_run)

    stats = {
        "total": len(files_to_commit),
        "success": len(files_to_commit) if success else 0,
        "failed": 0 if success else len(files_to_commit)
    }

    if success:
        log(f"Batch publish complete: {message}", "SUCCESS")
        save_state("complete", files_to_commit)
    else:
        log(f"Batch publish failed: {message}", "ERROR")
        save_state("failed", files_to_commit)

    return stats

def publish_new_or_modified():
    """
    Publish only new or modified files.

    Returns:
        dict: Statistics
    """
    log("Checking for new or modified files")

    try:
        os.chdir(BASE_DIR)

        # Get git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            log("Git status failed", "ERROR")
            return {"total": 0, "success": 0, "failed": 0}

        # Parse status
        modified_files = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            status = line[:2]
            filepath = line[3:].strip()

            # Check if it's a template or PDF
            if filepath.endswith('.tex') or filepath.endswith('.pdf'):
                if status != '  ':  # Not unmodified
                    modified_files.append(filepath)

        if not modified_files:
            log("No new or modified files", "SUCCESS")
            return {"total": 0, "success": 0, "failed": 0}

        log(f"Found {len(modified_files)} modified files")

        # Create commit message
        commit_msg = f"""LaTeX: Update templates and PDFs

Modified files:
{chr(10).join(f'  - {f}' for f in modified_files[:10])}
{f'  ... and {len(modified_files) - 10} more' if len(modified_files) > 10 else ''}

Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Publish
        success, message = git_add_commit_push(modified_files, commit_msg)

        stats = {
            "total": len(modified_files),
            "success": len(modified_files) if success else 0,
            "failed": 0 if success else len(modified_files)
        }

        if success:
            log(f"Published {len(modified_files)} files", "SUCCESS")
        else:
            log(f"Publish failed: {message}", "ERROR")

        return stats

    except Exception as e:
        log(f"Error checking for modifications: {e}", "ERROR")
        return {"total": 0, "success": 0, "failed": 0}

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Publish LaTeX templates and PDFs to GitHub"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Single template
    single_parser = subparsers.add_parser('single', help='Publish single template')
    single_parser.add_argument('tex_file', help='Path to .tex file')
    single_parser.add_argument('--no-pdf', action='store_true', help='Do not include PDF')

    # Batch publish
    batch_parser = subparsers.add_parser('batch', help='Publish multiple templates')
    batch_parser.add_argument('--pattern', default='**/*.tex', help='Glob pattern for templates')
    batch_parser.add_argument('--no-pdfs', action='store_true', help='Do not include PDFs')
    batch_parser.add_argument('--dry-run', action='store_true', help='Commit locally but do not push')

    # Publish new/modified
    new_parser = subparsers.add_parser('new', help='Publish new or modified files')

    # Status
    status_parser = subparsers.add_parser('status', help='Show git status')

    args = parser.parse_args()

    # Verify environment
    if not BASE_DIR.exists():
        log(f"Base directory not found: {BASE_DIR}", "ERROR")
        sys.exit(1)

    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)

    # Execute command
    if args.command == 'single':
        tex_path = Path(args.tex_file)
        if not tex_path.is_absolute():
            tex_path = BASE_DIR / args.tex_file

        success = publish_single_template(tex_path, include_pdf=not args.no_pdf)
        sys.exit(0 if success else 1)

    elif args.command == 'batch':
        stats = publish_batch(
            template_pattern=args.pattern,
            include_pdfs=not args.no_pdfs,
            dry_run=args.dry_run
        )
        log(f"Batch complete: {stats['success']}/{stats['total']} successful")
        sys.exit(0 if stats['success'] == stats['total'] else 1)

    elif args.command == 'new':
        stats = publish_new_or_modified()
        log(f"Published: {stats['success']}/{stats['total']} files")
        sys.exit(0 if stats['failed'] == 0 else 1)

    elif args.command == 'status':
        os.chdir(BASE_DIR)
        subprocess.run(["git", "status"])
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
