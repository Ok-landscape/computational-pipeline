#!/usr/bin/env python3
"""
Test script to generate a complete post for the Finite Element Method notebook
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from notebook_content_extractor import NotebookContentExtractor
from media_extractor import MediaExtractor
from post_text_parser import PostTextParser
from page_router import PageRouter

def generate_test_post():
    """Generate a complete post for testing"""

    # Paths
    notebook_path = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"
    posts_file = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts/finite_element_method_heat_transfer_posts.txt"

    print("=" * 80)
    print("TEST POST GENERATION - Finite Element Method for Heat Transfer")
    print("=" * 80)
    print()

    # 1. Extract media from notebook
    print("Step 1: Extracting media from notebook...")
    media_extractor = MediaExtractor()
    media_files = media_extractor.extract_from_notebook(notebook_path)

    if media_files:
        print(f"  ✓ Found {len(media_files)} media files:")
        for i, media_file in enumerate(media_files, 1):
            print(f"    {i}. {media_file}")
    else:
        print("  ⚠ No media files found")
    print()

    # 2. Parse post text
    print("Step 2: Parsing Facebook post from text file...")
    post_parser = PostTextParser()
    posts = post_parser.parse_posts_file(posts_file)

    if 'facebook' in posts:
        print(f"  ✓ Found Facebook post ({len(posts['facebook'])} characters)")
        print()
        print("  Preview:")
        print("  " + "-" * 76)
        for line in posts['facebook'].split('\n'):
            print(f"  {line}")
        print("  " + "-" * 76)
    else:
        print("  ✗ No Facebook post found!")
    print()

    # 3. Determine page routing
    print("Step 3: Determining page routing...")
    router = PageRouter()

    # Create a mock content item
    content_item = {
        'type': 'notebook',
        'title': 'Finite Element Method for Heat Transfer',
        'path': notebook_path,
        'notebook_name': 'finite_element_method_heat_transfer'
    }

    page_decision = router.route_content(content_item)
    print(f"  ✓ Target page: {page_decision['page_name']} (ID: {page_decision['page_id']})")
    print(f"  ✓ Reason: {page_decision['reason']}")
    print()

    # 4. Show complete post summary
    print("=" * 80)
    print("COMPLETE POST PREVIEW FOR COCALC PAGE")
    print("=" * 80)
    print()
    print(f"Page ID: {page_decision['page_id']}")
    print(f"Page Name: {page_decision['page_name']}")
    print()
    print("POST TEXT:")
    print("-" * 80)
    print(posts.get('facebook', 'No Facebook post available'))
    print("-" * 80)
    print()
    print("MEDIA FILES:")
    if media_files:
        for i, media_file in enumerate(media_files, 1):
            file_size = os.path.getsize(media_file) / 1024  # KB
            print(f"  {i}. {os.path.basename(media_file)} ({file_size:.1f} KB)")
            print(f"     Path: {media_file}")
    else:
        print("  No media files")
    print()

    # Return the complete package
    return {
        'page_id': page_decision['page_id'],
        'page_name': page_decision['page_name'],
        'text': posts.get('facebook', ''),
        'media': media_files,
        'source_notebook': notebook_path,
        'source_posts': posts_file
    }

if __name__ == '__main__':
    post_data = generate_test_post()

    print("=" * 80)
    print("Ready to post!")
    print("=" * 80)
