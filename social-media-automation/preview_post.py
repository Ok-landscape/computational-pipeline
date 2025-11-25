#!/usr/bin/env python3
"""
Generate a preview of a specific post before publishing
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from notebook_scanner import NotebookScanner
from post_text_parser import PostTextParser
from notebook_content_extractor import NotebookContentExtractor
from page_router import PageRouter

def preview_finite_element_post():
    """Preview the Finite Element Method post"""

    print("=" * 80)
    print("POST PREVIEW: Finite Element Method for Heat Transfer")
    print("Target: CoCalc Facebook Page")
    print("=" * 80)
    print()

    # File paths
    notebook_path = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"
    post_file = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts/finite_element_method_heat_transfer_posts.txt"
    images_dir = "/home/user/computational-pipeline/social-media-automation/extracted_images"

    # Ensure images directory exists
    Path(images_dir).mkdir(parents=True, exist_ok=True)

    # Step 1: Parse the post text
    print("[1] PARSING POST TEXT")
    print("-" * 80)
    parser = PostTextParser(post_file)
    posts = parser.get_all_posts()

    fb_post = posts.get('facebook', '')
    if fb_post:
        print(f"✓ Facebook post found ({len(fb_post)} characters)")
    else:
        print("✗ Facebook post not found!")
        return None

    # Step 2: Extract images from notebook
    print("\n[2] EXTRACTING IMAGES FROM NOTEBOOK")
    print("-" * 80)
    extractor = NotebookContentExtractor(notebook_path)

    print(f"Notebook title: {extractor.get_notebook_title()}")
    print(f"Has images: {extractor.has_images()}")

    images = extractor.extract_images(output_dir=images_dir)
    print(f"✓ Extracted {len(images)} images")

    image_paths = []
    if images:
        for i, img in enumerate(images, 1):
            saved_path = img.get('saved_path', '')
            if saved_path and os.path.exists(saved_path):
                file_size = os.path.getsize(saved_path) / 1024
                print(f"  {i}. {img['filename']} ({file_size:.1f} KB)")
                print(f"     → {saved_path}")
                image_paths.append(saved_path)

    # Step 3: Determine page routing
    print("\n[3] PAGE ROUTING DECISION")
    print("-" * 80)
    router = PageRouter()

    notebook_metadata = {
        'title': 'Finite Element Method for Heat Transfer',
        'path': notebook_path,
        'notebook_name': 'finite_element_method_heat_transfer',
        'topic': 'FEM and Heat Transfer',
        'tags': ['FEM', 'numerical methods', 'heat transfer', 'engineering']
    }

    routes = router.route_notebook(notebook_metadata)

    # Use the first (highest priority) route for CoCalc
    page_decision = None
    for route in routes:
        if route.page_name == 'CoCalc':
            page_decision = {
                'page_name': route.page_name,
                'page_id': route.page_id,
                'reason': route.reason,
                'priority': route.priority
            }
            break

    if not page_decision and routes:
        # Fallback to first route
        route = routes[0]
        page_decision = {
            'page_name': route.page_name,
            'page_id': route.page_id,
            'reason': route.reason,
            'priority': route.priority
        }

    if not page_decision:
        # Hardcode CoCalc for now
        page_decision = {
            'page_name': 'CoCalc',
            'page_id': '698630966948910',
            'reason': 'Default routing for computational content',
            'priority': 5
        }

    print(f"Target Page: {page_decision['page_name']}")
    print(f"Page ID: {page_decision['page_id']}")
    print(f"Reason: {page_decision['reason']}")

    # Step 4: Show complete preview
    print("\n" + "=" * 80)
    print("COMPLETE POST PREVIEW")
    print("=" * 80)
    print()
    print(f"📱 Platform: Facebook")
    print(f"📄 Page: {page_decision['page_name']} (ID: {page_decision['page_id']})")
    print()
    print("📝 POST TEXT:")
    print("-" * 80)
    print(fb_post)
    print("-" * 80)
    print()
    print(f"🖼️  MEDIA: {len(image_paths)} image(s)")
    if image_paths:
        for i, path in enumerate(image_paths, 1):
            size_kb = os.path.getsize(path) / 1024
            print(f"  {i}. {os.path.basename(path)} ({size_kb:.1f} KB)")
    print()
    print("🔗 NOTEBOOK LINK:")
    print(f"  {parser.get_cocalc_url()}")
    print()
    print("=" * 80)

    return {
        'page_id': page_decision['page_id'],
        'page_name': page_decision['page_name'],
        'text': fb_post,
        'media': image_paths,
        'notebook_url': parser.get_cocalc_url()
    }

if __name__ == '__main__':
    post_data = preview_finite_element_post()

    if post_data:
        print("\n✓ Post preview generated successfully!")
        print(f"  Ready to publish to {post_data['page_name']}")
    else:
        print("\n✗ Failed to generate post preview")
        sys.exit(1)
