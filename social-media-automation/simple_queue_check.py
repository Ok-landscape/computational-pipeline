#!/usr/bin/env python3
"""
Simple Queue Check - Quick validation of queue items

Checks links and basic properties of queued items.
"""

import sys
import requests
sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from unified_queue_manager import UnifiedQueueManager


def check_queue():
    """Simple queue check"""
    print("=" * 80)
    print("QUEUE CHECK REPORT")
    print("=" * 80)
    print()

    # Load queue
    qm = UnifiedQueueManager()
    queue = qm.queue

    print(f"Total items in queue: {len(queue)}")
    print()

    notebooks = [q for q in queue if q.content_type == 'notebook']
    templates = [q for q in queue if q.content_type == 'template']

    print(f"  Notebooks: {len(notebooks)}")
    print(f"  Templates: {len(templates)}")
    print()

    print("-" * 80)
    print("LINK ACCESSIBILITY CHECK")
    print("-" * 80)
    print()

    link_ok = []
    link_404 = []
    link_error = []

    for item in queue:
        name = item.source_name
        link = item.link
        content_type = item.content_type

        try:
            response = requests.head(link, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                link_ok.append((name, content_type))
                print(f"✓ {name} ({content_type})")
            elif response.status_code == 404:
                link_404.append((name, content_type, link))
                print(f"✗ {name} ({content_type}) - 404 NOT FOUND")
            else:
                link_error.append((name, content_type, response.status_code))
                print(f"⚠ {name} ({content_type}) - HTTP {response.status_code}")
        except Exception as e:
            link_error.append((name, content_type, str(e)[:50]))
            print(f"✗ {name} ({content_type}) - ERROR: {str(e)[:50]}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    print(f"Links OK (200):     {len(link_ok)}")
    print(f"Links 404:          {len(link_404)}")
    print(f"Links Error/Other:  {len(link_error)}")
    print()

    if link_404:
        print("ITEMS WITH 404 LINKS:")
        print("-" * 80)
        for name, ctype, link in link_404:
            print(f"  {name} ({ctype})")
            print(f"    URL: {link}")
        print()

    if link_error:
        print("ITEMS WITH LINK ERRORS:")
        print("-" * 80)
        for name, ctype, error in link_error[:10]:
            print(f"  {name} ({ctype}): {error}")
        if len(link_error) > 10:
            print(f"  ... and {len(link_error) - 10} more")
        print()

    # Check for notebooks (need execution)
    if notebooks:
        print("=" * 80)
        print("NOTEBOOK ITEMS (Need to check for outputs)")
        print("=" * 80)
        print()
        for nb in notebooks:
            print(f"  - {nb.source_name}")
        print()
        print("Note: Cannot check if notebooks have saved outputs from queue alone")
        print("Need to inspect source files directly")
        print()

    print("=" * 80)


if __name__ == '__main__':
    check_queue()
