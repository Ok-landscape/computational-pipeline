#!/usr/bin/env python3
"""
Test posting a single piece of content to Facebook
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/user/computational-pipeline/social-media-automation/.env')

sys.path.insert(0, '/home/user/computational-pipeline/social-media-automation')

from social_publisher import SocialMediaPublisher
from post_text_parser import PostTextParser
from notebook_content_extractor import NotebookContentExtractor
from pre_publish_validator import PrePublishValidator


def post_finite_element_method():
    """Post the Finite Element Method notebook to CoCalc page"""

    print("=" * 80)
    print("TEST POST: Finite Element Method for Heat Transfer")
    print("Target: CoCalc Facebook Page")
    print("=" * 80)
    print()

    # Configuration
    notebook_path = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"
    post_file = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts/finite_element_method_heat_transfer_posts.txt"
    page_id = "698630966948910"  # CoCalc

    # Parse post
    print("[1] Loading post content...")
    parser = PostTextParser(post_file)
    posts = parser.get_all_posts()

    fb_post = posts.get('facebook', '')
    if not fb_post:
        print("✗ No Facebook post found!")
        return False

    print(f"✓ Post loaded ({len(fb_post)} characters)")
    print()

    # Show preview
    print("[2] POST PREVIEW:")
    print("-" * 80)
    print(fb_post)
    print("-" * 80)
    print()

    # Extract images (if any)
    print("[3] Checking for images...")
    extractor = NotebookContentExtractor(notebook_path)

    images_dir = "/home/user/computational-pipeline/social-media-automation/extracted_images"
    Path(images_dir).mkdir(parents=True, exist_ok=True)

    images = extractor.extract_images(output_dir=images_dir)
    image_paths = [img.get('saved_path') for img in images if img.get('saved_path')]

    if image_paths:
        print(f"✓ Found {len(image_paths)} image(s)")
        for img_path in image_paths:
            print(f"  - {os.path.basename(img_path)}")
    else:
        print("ℹ No images (text-only post)")
    print()

    # Confirm - auto-approve for automated execution
    print("=" * 80)
    print("Auto-posting enabled (approved by user)")
    print("=" * 80)

    # Get notebook link
    cocalc_link = parser.get_cocalc_url()

    # VALIDATION CHECK (NEW)
    print("[4] Running pre-publish validation...")
    validator = PrePublishValidator()
    validation_result = validator.validate_notebook_post(
        notebook_path=notebook_path,
        cocalc_url=cocalc_link,
        post_text=fb_post
    )

    print(validation_result)

    if not validation_result.is_valid:
        print()
        print("=" * 80)
        print("VALIDATION FAILED - POST BLOCKED")
        print("=" * 80)
        print("Fix the errors above before posting.")
        return False

    if validation_result.warnings:
        print()
        print("Validation passed with warnings - proceeding anyway")

    # Initialize publisher
    print()
    print("[5] Initializing Facebook publisher...")
    publisher = SocialMediaPublisher()

    # Publish!
    print("[6] Publishing...")
    try:
        result = publisher.publish_to_facebook(
            page_id=page_id,
            content=fb_post,
            link=cocalc_link,
            image_path=image_paths[0] if image_paths else None,
            template_name="finite_element_method_heat_transfer"
        )

        if result.success:
            post_id = result.post_id
            print()
            print("=" * 80)
            print("✓ POST PUBLISHED SUCCESSFULLY!")
            print("=" * 80)
            print(f"Post ID: {post_id}")
            print(f"Page: CoCalc (ID: {page_id})")
            print()
            print("View your post:")
            print(f"https://www.facebook.com/{post_id}")
            print("=" * 80)
            return True
        else:
            print("✗ Publishing failed!")
            print(f"Error: {result.error_message}")
            return False

    except Exception as e:
        print(f"✗ Error publishing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = post_finite_element_method()
    sys.exit(0 if success else 1)
