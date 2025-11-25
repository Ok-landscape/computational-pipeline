"""
Notebook Scanner Module

Scans the GitHub repository for available notebooks and manages notebook metadata.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NotebookScanner:
    """Scans and manages computational notebooks from the GitHub repository."""

    def __init__(self, notebooks_dir: str, output_dir: str):
        """
        Initialize the NotebookScanner.

        Args:
            notebooks_dir: Path to the notebooks directory
            output_dir: Path to the social posts output directory
        """
        self.notebooks_dir = Path(notebooks_dir)
        self.output_dir = Path(output_dir)

        if not self.notebooks_dir.exists():
            raise FileNotFoundError(f"Notebooks directory not found: {notebooks_dir}")

        if not self.output_dir.exists():
            raise FileNotFoundError(f"Output directory not found: {output_dir}")

    def scan_published_notebooks(self) -> List[Dict[str, str]]:
        """
        Scan the published notebooks directory.

        Returns:
            List of dictionaries containing notebook metadata
        """
        published_dir = self.notebooks_dir / "published"

        if not published_dir.exists():
            logger.warning(f"Published directory not found: {published_dir}")
            return []

        notebooks = []
        for notebook_file in published_dir.glob("*.ipynb"):
            notebook_info = {
                'filename': notebook_file.name,
                'basename': notebook_file.stem,
                'path': str(notebook_file),
                'size': notebook_file.stat().st_size,
                'modified': notebook_file.stat().st_mtime
            }

            # Check if corresponding social post file exists
            post_file = self.output_dir / f"{notebook_file.stem}_posts.txt"
            notebook_info['has_posts'] = post_file.exists()
            notebook_info['post_file'] = str(post_file) if post_file.exists() else None

            notebooks.append(notebook_info)

        logger.info(f"Found {len(notebooks)} published notebooks")
        logger.info(f"Notebooks with posts: {sum(1 for n in notebooks if n['has_posts'])}")

        return sorted(notebooks, key=lambda x: x['modified'], reverse=True)

    def get_notebooks_with_posts(self) -> List[Dict[str, str]]:
        """
        Get only notebooks that have associated social posts.

        Returns:
            List of notebook metadata for notebooks with posts
        """
        all_notebooks = self.scan_published_notebooks()
        with_posts = [n for n in all_notebooks if n['has_posts']]

        logger.info(f"Found {len(with_posts)} notebooks with social posts")
        return with_posts

    def get_unposted_notebooks(self, posted_basenames: List[str]) -> List[Dict[str, str]]:
        """
        Get notebooks that have posts but haven't been published yet.

        Args:
            posted_basenames: List of notebook basenames that have been posted

        Returns:
            List of notebook metadata for unposted notebooks
        """
        available = self.get_notebooks_with_posts()
        unposted = [n for n in available if n['basename'] not in posted_basenames]

        logger.info(f"Found {len(unposted)} unposted notebooks")
        return unposted

    def get_notebook_by_basename(self, basename: str) -> Optional[Dict[str, str]]:
        """
        Get metadata for a specific notebook by its basename.

        Args:
            basename: The basename of the notebook (without .ipynb extension)

        Returns:
            Notebook metadata or None if not found
        """
        all_notebooks = self.scan_published_notebooks()
        for notebook in all_notebooks:
            if notebook['basename'] == basename:
                return notebook

        logger.warning(f"Notebook not found: {basename}")
        return None

    def get_available_post_files(self) -> List[str]:
        """
        Get all available social post text files.

        Returns:
            List of post file paths
        """
        post_files = list(self.output_dir.glob("*_posts.txt"))
        logger.info(f"Found {len(post_files)} social post files")
        return [str(f) for f in post_files]


def main():
    """Test the NotebookScanner."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test paths
    notebooks_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks"
    output_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts"

    try:
        scanner = NotebookScanner(notebooks_dir, output_dir)

        print("\n=== Scanning Published Notebooks ===")
        all_notebooks = scanner.scan_published_notebooks()
        print(f"Total notebooks: {len(all_notebooks)}")

        print("\n=== Notebooks with Posts ===")
        with_posts = scanner.get_notebooks_with_posts()
        print(f"Total with posts: {len(with_posts)}")

        if with_posts:
            print("\nFirst 5 notebooks with posts:")
            for nb in with_posts[:5]:
                print(f"  - {nb['basename']}")
                print(f"    Post file: {nb['post_file']}")

        print("\n=== Available Post Files ===")
        post_files = scanner.get_available_post_files()
        print(f"Total post files: {len(post_files)}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
