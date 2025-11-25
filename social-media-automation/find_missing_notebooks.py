#!/usr/bin/env python3
"""
Find notebooks that exist locally but not on GitHub
"""

import requests
import json
from pathlib import Path


def get_github_notebooks():
    """Get list of notebooks on GitHub"""
    url = "https://api.github.com/repos/Ok-landscape/computational-pipeline/contents/notebooks/published"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return set(item['name'] for item in data if item['name'].endswith('.ipynb'))


def get_local_notebooks():
    """Get list of local notebooks"""
    local_dir = Path("/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published")
    return set(f.name for f in local_dir.glob("*.ipynb"))


def main():
    print("=" * 80)
    print("FINDING MISSING NOTEBOOKS")
    print("=" * 80)
    print()

    print("Fetching GitHub notebooks...")
    github_notebooks = get_github_notebooks()
    print(f"  GitHub: {len(github_notebooks)} notebooks")

    print("Scanning local notebooks...")
    local_notebooks = get_local_notebooks()
    print(f"  Local:  {len(local_notebooks)} notebooks")

    print()
    print("-" * 80)
    print()

    # Find missing
    missing = local_notebooks - github_notebooks
    extra = github_notebooks - local_notebooks

    print(f"MISSING ON GITHUB: {len(missing)} notebooks")
    print("-" * 80)
    for nb in sorted(missing):
        print(f"  - {nb}")
    print()

    if extra:
        print(f"EXTRA ON GITHUB (not local): {len(extra)} notebooks")
        print("-" * 80)
        for nb in sorted(extra)[:10]:
            print(f"  - {nb}")
        if len(extra) > 10:
            print(f"  ... and {len(extra) - 10} more")
        print()

    # Check if any of the missing notebooks are in the queue
    print("Checking which missing notebooks are in the posting queue...")

    import sys
    sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')
    from unified_queue_manager import UnifiedQueueManager

    qm = UnifiedQueueManager()
    queued_notebooks = set(q.source_name + '.ipynb' for q in qm.queue if q.content_type == 'notebook')

    missing_and_queued = missing & queued_notebooks

    if missing_and_queued:
        print(f"\n⚠ URGENT: {len(missing_and_queued)} missing notebooks are in the posting queue!")
        print("-" * 80)
        for nb in sorted(missing_and_queued):
            print(f"  ✗ {nb}")
        print()
        print("These MUST be pushed to GitHub before posting!")
    else:
        print("\n✓ None of the missing notebooks are in the posting queue")

    print()
    print("=" * 80)

    # Save list to file
    output_file = Path("/home/user/computational-pipeline/social-media-automation/data/missing_notebooks.txt")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write("Missing Notebooks on GitHub\n")
        f.write("=" * 80 + "\n\n")
        for nb in sorted(missing):
            f.write(f"{nb}\n")

    print(f"List saved to: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
