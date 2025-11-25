#!/usr/bin/env python3
"""
Validate Queue - Check all queued content before posting

Runs validation on all items in the posting queue and generates a report.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('/home/user/computational-pipeline/social-media-automation/.env')
sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from pre_publish_validator import PrePublishValidator
from unified_queue_manager import UnifiedQueueManager
from post_text_parser import PostTextParser


def validate_queue():
    """Validate all items in the queue"""
    print("=" * 80)
    print("QUEUE VALIDATION REPORT")
    print("=" * 80)
    print()

    # Load queue
    queue_manager = UnifiedQueueManager()
    # Access the queue directly
    queue = queue_manager.queue

    print(f"Total items in queue: {len(queue)}")
    print()

    # Initialize validator
    validator = PrePublishValidator()

    # Prepare validation items
    # For now, skip detailed file validation since queue doesn't have source paths
    # Focus on what we can validate: links and text
    print("Note: Queue doesn't contain source file paths - validating links and text only")
    print()

    link_validations = []
    for item in queue:
        print(f"Checking: {item.source_name} ({item.content_type})")

        # Basic validation: link accessibility
        link = item.link
        link_ok = False

        if link and link.startswith('https://cocalc.com/'):
            try:
                response = requests.head(link, timeout=10, allow_redirects=True)
                link_ok = (response.status_code == 200)
                status = "✓" if link_ok else f"✗ (HTTP {response.status_code})"
            except Exception as e:
                status = f"✗ ({str(e)[:50]})"
        else:
            status = "✗ (Invalid URL format)"

        print(f"  Link: {status}")

        link_validations.append({
            'id': item.content_id,
            'name': item.source_name,
            'type': item.content_type,
            'link': link,
            'link_ok': link_ok,
            'text_length': len(item.content_text) if item.content_text else 0
        })

    print()
    print("-" * 80)
    print()

    # Skip the full validation batch since we don't have paths
    # Instead, create simple results based on what we checked
    results = {}

    # Run validation
    print("Running validation checks...")
    print("-" * 80)
    print()

    results = validator.validate_batch(validation_items)

    # Generate report
    report = validator.generate_validation_report(results)
    print(report)

    # Detailed breakdown
    print()
    print("=" * 80)
    print("DETAILED BREAKDOWN")
    print("=" * 80)
    print()

    # Group by failure reason
    missing_on_github = []
    no_outputs = []
    no_images = []
    link_404 = []
    passed = []

    for item_id, result in results.items():
        if result.is_valid:
            passed.append(item_id)
        else:
            # Check specific failures
            if not result.checks_passed.get('GitHub file exists', True):
                missing_on_github.append(item_id)
            if not result.checks_passed.get('Notebook has outputs', True):
                no_outputs.append(item_id)
            if not result.checks_passed.get('Notebook has images', True):
                no_images.append(item_id)
            if not result.checks_passed.get('CoCalc link accessible', True):
                link_404.append(item_id)

    # Print groups
    print(f"PASSED: {len(passed)} items")
    if passed:
        for item in passed[:5]:
            print(f"  ✓ {item}")
        if len(passed) > 5:
            print(f"  ... and {len(passed) - 5} more")
    print()

    print(f"MISSING ON GITHUB: {len(missing_on_github)} items")
    if missing_on_github:
        for item in missing_on_github:
            print(f"  ✗ {item}")
    print()

    print(f"NO SAVED OUTPUTS: {len(no_outputs)} items")
    if no_outputs:
        for item in no_outputs:
            print(f"  ✗ {item}")
    print()

    print(f"NO IMAGES: {len(no_images)} items")
    if no_images:
        for item in no_images[:10]:
            print(f"  ⚠ {item}")
        if len(no_images) > 10:
            print(f"  ... and {len(no_images) - 10} more")
    print()

    print(f"COCALC LINK 404: {len(link_404)} items")
    if link_404:
        for item in link_404:
            print(f"  ✗ {item}")
    print()

    # Summary with recommendations
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()

    if missing_on_github:
        print(f"1. SYNC TO GITHUB: {len(missing_on_github)} files need to be pushed")
        print(f"   These files exist locally but not on GitHub:")
        for item in missing_on_github[:3]:
            print(f"   - {item}")
        if len(missing_on_github) > 3:
            print(f"   ... and {len(missing_on_github) - 3} more")
        print()

    if no_outputs:
        print(f"2. EXECUTE NOTEBOOKS: {len(no_outputs)} notebooks need execution")
        print(f"   These notebooks have no saved outputs:")
        for item in no_outputs[:3]:
            print(f"   - {item}")
        if len(no_outputs) > 3:
            print(f"   ... and {len(no_outputs) - 3} more")
        print()

    if link_404:
        print(f"3. WAIT FOR SYNC: {len(link_404)} CoCalc links return 404")
        print(f"   Wait 5-15 minutes for GitHub->CoCalc sync")
        print()

    if passed:
        print(f"4. READY TO POST: {len(passed)} items passed all checks")
        print(f"   You can safely post these items")
        print()

    # Save report to file
    report_file = Path("/home/user/computational-pipeline/social-media-automation/data/validation_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    report_data = {
        'timestamp': results[list(results.keys())[0]].to_dict()['timestamp'] if results else None,
        'total_items': len(results),
        'passed': len(passed),
        'failed': len(results) - len(passed),
        'missing_on_github': missing_on_github,
        'no_outputs': no_outputs,
        'no_images': no_images,
        'link_404': link_404,
        'passed_items': passed,
        'detailed_results': {k: v.to_dict() for k, v in results.items()}
    }

    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"Report saved to: {report_file}")
    print("=" * 80)


if __name__ == '__main__':
    validate_queue()
