#!/usr/bin/env python3
"""
Check which notebooks in the queue have saved outputs
"""

import sys
import json
import nbformat
from pathlib import Path

sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')
from unified_queue_manager import UnifiedQueueManager


def check_notebook_outputs(notebook_path):
    """Check if notebook has outputs"""
    try:
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        has_outputs = False
        has_images = False
        output_count = 0
        image_count = 0

        for cell in nb.cells:
            if cell.cell_type == 'code':
                if cell.get('outputs'):
                    output_count += len(cell.outputs)
                    has_outputs = True

                    for output in cell.outputs:
                        if output.get('output_type') in ['display_data', 'execute_result']:
                            data = output.get('data', {})
                            if 'image/png' in data or 'image/jpeg' in data:
                                image_count += 1
                                has_images = True

        return {
            'exists': True,
            'has_outputs': has_outputs,
            'has_images': has_images,
            'output_count': output_count,
            'image_count': image_count
        }

    except FileNotFoundError:
        return {
            'exists': False,
            'has_outputs': False,
            'has_images': False,
            'output_count': 0,
            'image_count': 0
        }
    except Exception as e:
        return {
            'exists': True,
            'error': str(e),
            'has_outputs': False,
            'has_images': False,
            'output_count': 0,
            'image_count': 0
        }


def main():
    print("=" * 80)
    print("NOTEBOOK OUTPUT CHECK")
    print("=" * 80)
    print()

    # Load queue
    qm = UnifiedQueueManager()
    notebooks = [q for q in qm.queue if q.content_type == 'notebook']

    print(f"Checking {len(notebooks)} notebook items in queue...")
    print()

    # Base path for notebooks
    base_path = Path("/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published")

    results = {
        'with_outputs': [],
        'with_images': [],
        'without_outputs': [],
        'not_found': []
    }

    # Get unique notebook names
    unique_notebooks = list(set(nb.source_name for nb in notebooks))
    print(f"Unique notebooks: {len(unique_notebooks)}")
    print()

    for nb_name in sorted(unique_notebooks):
        nb_path = base_path / f"{nb_name}.ipynb"
        check = check_notebook_outputs(nb_path)

        print(f"{nb_name}:")
        print(f"  Path: {nb_path}")
        print(f"  Exists: {check['exists']}")

        if check['exists']:
            print(f"  Outputs: {check['output_count']}")
            print(f"  Images: {check['image_count']}")

            if check['has_outputs']:
                results['with_outputs'].append(nb_name)
                if check['has_images']:
                    results['with_images'].append(nb_name)
                    print(f"  Status: ✓ Ready (has outputs and images)")
                else:
                    print(f"  Status: ⚠ Has outputs but no images")
            else:
                results['without_outputs'].append(nb_name)
                print(f"  Status: ✗ Needs execution (no outputs)")
        else:
            results['not_found'].append(nb_name)
            print(f"  Status: ✗ File not found")

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Notebooks with outputs and images: {len(results['with_images'])}")
    print(f"Notebooks with outputs (no images): {len(results['with_outputs']) - len(results['with_images'])}")
    print(f"Notebooks without outputs:         {len(results['without_outputs'])}")
    print(f"Notebooks not found:               {len(results['not_found'])}")
    print()

    if results['without_outputs']:
        print("NEEDS EXECUTION:")
        print("-" * 80)
        for nb in results['without_outputs']:
            print(f"  - {nb}")
        print()

    if results['not_found']:
        print("NOT FOUND:")
        print("-" * 80)
        for nb in results['not_found']:
            print(f"  - {nb}")
        print()

    if results['with_images']:
        print("READY TO POST (has images):")
        print("-" * 80)
        for nb in results['with_images']:
            print(f"  ✓ {nb}")
        print()

    print("=" * 80)


if __name__ == '__main__':
    main()
