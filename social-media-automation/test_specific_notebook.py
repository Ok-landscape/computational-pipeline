"""Test with a specific notebook."""

from pathlib import Path
from post_text_parser import PostTextParser
from notebook_content_extractor import NotebookContentExtractor

# Test with finite element method (original format)
print("=" * 80)
print("Testing: finite_element_method_heat_transfer")
print("=" * 80)

post_file = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts/finite_element_method_heat_transfer_posts.txt"
notebook_file = "/home/user/computational-pipeline/social-media-automation/repo-data/notebooks/published/finite_element_method_heat_transfer.ipynb"

# Parse posts
parser = PostTextParser(post_file)
fb_post = parser.get_facebook_post()

print(f"\nFacebook Post ({len(fb_post) if fb_post else 0} chars):")
print("-" * 80)
if fb_post:
    print(fb_post)
else:
    print("NOT FOUND")

# Extract content
extractor = NotebookContentExtractor(notebook_file)
images = extractor.extract_images()

print(f"\n\nImages: {len(images)}")
print(f"Title: {extractor.get_notebook_title()}")

# Show all platforms
all_posts = parser.get_all_posts()
print(f"\nAvailable platforms:")
for platform, content in all_posts.items():
    status = "✓" if content else "✗"
    char_count = len(content) if content else 0
    print(f"  {status} {platform.capitalize():<12} {char_count:>5} chars")
