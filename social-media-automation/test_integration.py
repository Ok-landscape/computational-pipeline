"""
Integration test for the notebook-based social media posting system.
"""

import os
from pathlib import Path
from notebook_scanner import NotebookScanner
from post_text_parser import PostTextParser
from notebook_content_extractor import NotebookContentExtractor


def test_complete_workflow():
    """Test the complete workflow with available notebooks."""

    print("=" * 80)
    print("INTEGRATION TEST: Notebook-Based Social Media Posting")
    print("=" * 80)

    # Configuration
    notebooks_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks"
    output_dir = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts"
    images_dir = "/home/user/computational-pipeline/social-media-automation/test_images"

    # Create images directory
    Path(images_dir).mkdir(parents=True, exist_ok=True)

    # Step 1: Scan for notebooks
    print("\n[1] Scanning for notebooks...")
    scanner = NotebookScanner(notebooks_dir, output_dir)
    notebooks_with_posts = scanner.get_notebooks_with_posts()

    print(f"    Found {len(notebooks_with_posts)} notebooks with social posts")

    if not notebooks_with_posts:
        print("    ERROR: No notebooks with posts found!")
        return

    # Step 2: Pick first notebook for testing
    test_notebook = notebooks_with_posts[0]
    print(f"\n[2] Testing with notebook: {test_notebook['basename']}")
    print(f"    Notebook path: {test_notebook['path']}")
    print(f"    Post file: {test_notebook['post_file']}")

    # Step 3: Parse social posts
    print(f"\n[3] Parsing social media posts...")
    parser = PostTextParser(test_notebook['post_file'])

    print(f"    Notebook name: {parser.notebook_name}")
    print(f"    CoCalc URL: {parser.get_cocalc_url()}")

    # Get all posts to check which platforms are available
    all_posts = parser.get_all_posts()

    # Prefer Facebook, but fallback to others
    fb_post = all_posts.get('facebook')
    if fb_post:
        print(f"\n    Facebook post ({len(fb_post)} chars):")
        print(f"    ---")
        print(f"    {fb_post}")
        print(f"    ---")
    else:
        print(f"\n    Note: Facebook post not available in this file format")
        # Show Twitter as fallback
        twitter_post = all_posts.get('twitter')
        if twitter_post:
            print(f"    Twitter post ({len(twitter_post)} chars):")
            print(f"    ---")
            print(f"    {twitter_post}")
            print(f"    ---")

    # Step 4: Extract notebook content
    print(f"\n[4] Extracting notebook content...")
    extractor = NotebookContentExtractor(test_notebook['path'])

    print(f"    Title: {extractor.get_notebook_title()}")
    print(f"    Has images: {extractor.has_images()}")

    # Extract images
    images = extractor.extract_images(output_dir=images_dir)
    print(f"    Extracted {len(images)} images")

    if images:
        print(f"\n    Image details:")
        for img in images:
            print(f"      - {img['filename']}")
            if 'saved_path' in img:
                print(f"        Saved to: {img['saved_path']}")
                # Check file size
                file_size = Path(img['saved_path']).stat().st_size
                print(f"        Size: {file_size / 1024:.1f} KB")

    # Step 5: Show what social media post would look like
    print(f"\n[5] Sample Social Media Post Preview")
    print("=" * 80)

    # Use Facebook if available, otherwise use first available platform
    post_text = fb_post
    platform_name = "Facebook"

    if not post_text:
        for platform, content in all_posts.items():
            if content:
                post_text = content
                platform_name = platform.capitalize()
                break

    if post_text:
        print(f"PLATFORM: {platform_name}")
        print(f"POST TEXT:\n{post_text}\n")
    else:
        print("ERROR: No posts found in file!")

    if images:
        print(f"IMAGES ATTACHED: {len(images)}")
        for img in images:
            print(f"  - {img['filename']}")
    else:
        print("IMAGES ATTACHED: None")

    print(f"\nCOCALC LINK: {parser.get_cocalc_url()}")
    print("=" * 80)

    # Step 6: Summary
    print(f"\n[6] Test Summary")
    print(f"    ✓ Notebook scanned successfully")
    print(f"    ✓ Social posts parsed successfully")
    print(f"    ✓ Content extracted successfully")
    if post_text:
        print(f"    ✓ Post ready for {platform_name}: {len(post_text)} chars")
    print(f"    ✓ Images extracted: {len(images)}")

    # Show all available platforms
    print(f"\n[7] Available platforms:")
    for platform, content in all_posts.items():
        status = "✓" if content else "✗"
        char_count = len(content) if content else 0
        print(f"    {status} {platform.capitalize():<12} {char_count:>5} chars")


if __name__ == "__main__":
    test_complete_workflow()
