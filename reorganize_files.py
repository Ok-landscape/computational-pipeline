#!/usr/bin/env python3
"""
File Reorganization Script
Reorganizes notebooks, plots, and posts into subdirectories.
"""

import os
import shutil
from pathlib import Path
import subprocess

# Directories
NOTEBOOKS_DIR = Path("/home/user/computational-pipeline/notebooks/published")
POSTS_DIR = Path("/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts")

def get_notebook_list():
    """Get list of all notebooks"""
    return sorted(NOTEBOOKS_DIR.glob("*.ipynb"))

def get_plot_for_notebook(notebook_name):
    """Find plot files for a notebook"""
    # Most common patterns
    patterns = [
        f"{notebook_name}_analysis.png",
        f"{notebook_name}_comprehensive_analysis.png",
        f"{notebook_name}.png",
        # Handle special cases
    ]

    plots = []
    for pattern in patterns:
        plot_path = NOTEBOOKS_DIR / pattern
        if plot_path.exists():
            plots.append(plot_path)

    # Also check for any PNG with notebook name prefix
    for png in NOTEBOOKS_DIR.glob(f"{notebook_name}*.png"):
        if png not in plots:
            plots.append(png)

    return plots

def get_post_for_notebook(notebook_name):
    """Find post file for a notebook"""
    post_file = POSTS_DIR / f"{notebook_name}_posts.txt"
    return post_file if post_file.exists() else None

def create_subdirectory(notebook_path):
    """Create subdirectory for notebook"""
    notebook_name = notebook_path.stem
    subdir = NOTEBOOKS_DIR / notebook_name
    subdir.mkdir(exist_ok=True)
    return subdir

def move_file_with_git(source, dest):
    """Move file using git mv to preserve history"""
    try:
        subprocess.run(["git", "mv", str(source), str(dest)], check=True,
                      cwd=source.parent, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Git mv failed for {source.name}, trying regular move: {e}")
        try:
            shutil.move(str(source), str(dest))
            return True
        except Exception as e2:
            print(f"  ERROR moving {source.name}: {e2}")
            return False

def reorganize_notebooks():
    """Main reorganization function"""
    notebooks = get_notebook_list()

    stats = {
        'notebooks_processed': 0,
        'plots_moved': 0,
        'posts_moved': 0,
        'errors': []
    }

    print(f"Found {len(notebooks)} notebooks to reorganize\n")

    for i, notebook_path in enumerate(notebooks, 1):
        notebook_name = notebook_path.stem
        print(f"[{i}/{len(notebooks)}] Processing: {notebook_name}")

        try:
            # Create subdirectory
            subdir = create_subdirectory(notebook_path)
            print(f"  Created/verified: {subdir.name}/")

            # Move notebook
            dest_notebook = subdir / notebook_path.name
            if not dest_notebook.exists():
                if move_file_with_git(notebook_path, dest_notebook):
                    print(f"  ✓ Moved notebook")
                    stats['notebooks_processed'] += 1
            else:
                print(f"  ✓ Notebook already in place")
                stats['notebooks_processed'] += 1

            # Move plots
            plots = get_plot_for_notebook(notebook_name)
            for plot in plots:
                dest_plot = subdir / plot.name
                if not dest_plot.exists():
                    if move_file_with_git(plot, dest_plot):
                        print(f"  ✓ Moved plot: {plot.name}")
                        stats['plots_moved'] += 1
                else:
                    print(f"  ✓ Plot already in place: {plot.name}")
                    stats['plots_moved'] += 1

            # Move post
            post = get_post_for_notebook(notebook_name)
            if post:
                dest_post = subdir / post.name
                if not dest_post.exists():
                    if move_file_with_git(post, dest_post):
                        print(f"  ✓ Moved post")
                        stats['posts_moved'] += 1
                else:
                    print(f"  ✓ Post already in place")
                    stats['posts_moved'] += 1
            else:
                print(f"  ⚠ No post file found (expected: {notebook_name}_posts.txt)")

        except Exception as e:
            error_msg = f"Error processing {notebook_name}: {e}"
            print(f"  ✗ {error_msg}")
            stats['errors'].append(error_msg)

    return stats

def organize_template_posts():
    """Move template posts to templates/ subdirectory"""
    templates_dir = POSTS_DIR / "templates"
    templates_dir.mkdir(exist_ok=True)

    print("\n" + "="*60)
    print("Organizing template posts")
    print("="*60)

    # Get all remaining posts (should be template posts)
    remaining_posts = list(POSTS_DIR.glob("*_posts.txt"))
    remaining_posts = [p for p in remaining_posts if not p.name.endswith('.backup')]

    stats = {'moved': 0, 'errors': []}

    for post in remaining_posts:
        dest = templates_dir / post.name
        if not dest.exists():
            try:
                if move_file_with_git(post, dest):
                    print(f"  ✓ Moved: {post.name}")
                    stats['moved'] += 1
            except Exception as e:
                error_msg = f"Error moving {post.name}: {e}"
                print(f"  ✗ {error_msg}")
                stats['errors'].append(error_msg)

    return stats

def print_summary(notebook_stats, template_stats):
    """Print reorganization summary"""
    print("\n" + "="*60)
    print("REORGANIZATION SUMMARY")
    print("="*60)
    print(f"\nNotebooks:")
    print(f"  Processed: {notebook_stats['notebooks_processed']}")
    print(f"  Plots moved: {notebook_stats['plots_moved']}")
    print(f"  Posts moved: {notebook_stats['posts_moved']}")

    print(f"\nTemplate Posts:")
    print(f"  Moved to templates/: {template_stats['moved']}")

    total_errors = len(notebook_stats['errors']) + len(template_stats['errors'])
    print(f"\nErrors: {total_errors}")

    if notebook_stats['errors']:
        print("\nNotebook errors:")
        for error in notebook_stats['errors']:
            print(f"  - {error}")

    if template_stats['errors']:
        print("\nTemplate errors:")
        for error in template_stats['errors']:
            print(f"  - {error}")

    print("="*60)

if __name__ == "__main__":
    print("COMPUTATIONAL PIPELINE FILE REORGANIZATION")
    print("="*60)
    print("\nThis script will:")
    print("1. Create subdirectories for each notebook")
    print("2. Move notebooks, plots, and posts into subdirectories")
    print("3. Move template posts to templates/ subdirectory")
    print("4. Preserve git history using 'git mv' where possible")
    print("\n" + "="*60 + "\n")

    # Reorganize notebooks
    notebook_stats = reorganize_notebooks()

    # Organize template posts
    template_stats = organize_template_posts()

    # Print summary
    print_summary(notebook_stats, template_stats)
