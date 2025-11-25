#!/usr/bin/env python3
"""
Batch Image Quality Check

Runs image quality validation on all executed notebooks to identify
notebooks with empty plots or other quality issues.
"""

import os
import sys
from pathlib import Path
from pre_publish_validator import PrePublishValidator
import json

def batch_quality_check(notebooks_dir: str):
    """
    Check image quality for all notebooks in directory

    Args:
        notebooks_dir: Directory containing notebooks to check
    """
    print("=" * 80)
    print("BATCH IMAGE QUALITY CHECK")
    print("=" * 80)
    print()

    notebooks_path = Path(notebooks_dir)
    notebook_files = list(notebooks_path.glob("*.ipynb"))

    # Filter out checkpoints and backups
    notebook_files = [
        f for f in notebook_files
        if not f.name.startswith('.') and
           '-checkpoint' not in f.name and
           '.bak' not in f.name
    ]

    print(f"Found {len(notebook_files)} notebooks to check")
    print()

    validator = PrePublishValidator()

    results = {
        'passed': [],
        'failed': [],
        'no_images': [],
        'errors': []
    }

    for notebook_path in sorted(notebook_files):
        notebook_name = notebook_path.stem
        print(f"Checking: {notebook_name}...", end=" ")

        try:
            # Construct CoCalc URL
            cocalc_url = f"https://cocalc.com/github/Ok-landscape/computational-pipeline/blob/main/notebooks/published/{notebook_path.name}"

            # Validate
            result = validator.validate_notebook_post(str(notebook_path), cocalc_url)

            # Check image quality specifically
            if result.metadata.get('notebook_images', 0) == 0:
                print("NO IMAGES")
                results['no_images'].append(notebook_name)
            elif result.metadata.get('images_quality_failed', 0) > 0:
                print(f"FAILED ({result.metadata['images_quality_failed']} bad images)")
                results['failed'].append({
                    'name': notebook_name,
                    'failed_count': result.metadata['images_quality_failed'],
                    'total_count': result.metadata['images_quality_checked'],
                    'errors': result.errors
                })
            else:
                print("PASSED")
                results['passed'].append(notebook_name)

        except Exception as e:
            print(f"ERROR: {str(e)[:60]}")
            results['errors'].append({
                'name': notebook_name,
                'error': str(e)
            })

    # Summary report
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total notebooks: {len(notebook_files)}")
    print(f"Passed quality checks: {len(results['passed'])}")
    print(f"Failed quality checks: {len(results['failed'])}")
    print(f"No images: {len(results['no_images'])}")
    print(f"Errors: {len(results['errors'])}")
    print()

    if results['failed']:
        print("=" * 80)
        print("NOTEBOOKS WITH QUALITY ISSUES")
        print("=" * 80)
        for item in results['failed']:
            print(f"\n{item['name']}:")
            print(f"  Failed: {item['failed_count']} of {item['total_count']} images")
            print(f"  Issues:")
            for error in item['errors'][:3]:
                print(f"    - {error}")

    if results['passed']:
        print()
        print("=" * 80)
        print("NOTEBOOKS READY FOR POSTING")
        print("=" * 80)
        for name in results['passed'][:10]:
            print(f"  ✓ {name}")
        if len(results['passed']) > 10:
            print(f"  ... and {len(results['passed']) - 10} more")

    # Save detailed report
    report_path = Path("/home/user/computational-pipeline/social-media-automation/data/quality_check_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)

    print()
    print(f"Detailed report saved to: {report_path}")
    print("=" * 80)

    return results


if __name__ == '__main__':
    notebooks_dir = sys.argv[1] if len(sys.argv) > 1 else \
        "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published"

    results = batch_quality_check(notebooks_dir)

    # Exit code: 0 if all passed, 1 if any failed
    sys.exit(0 if not results['failed'] else 1)
