"""
Post Text Parser Module

Parses the social media post text files and extracts platform-specific content.
"""

import re
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PostTextParser:
    """Parses social media post text files and extracts platform-specific content."""

    # Platform separator patterns - handles multiple formats
    PLATFORM_PATTERNS = {
        'twitter': [
            r'={70,}\s*TWITTER/X.*?={70,}',
            r'-{70,}\s*1\.\s*TWITTER/X.*?-{70,}',
            r'###\s*Twitter/X',
        ],
        'bluesky': [
            r'={70,}\s*BLUESKY.*?={70,}',
            r'-{70,}\s*2\.\s*BLUESKY.*?-{70,}',
            r'###\s*Bluesky',
        ],
        'threads': [
            r'={70,}\s*THREADS.*?={70,}',
            r'-{70,}\s*3\.\s*THREADS.*?-{70,}',
            r'###\s*Threads',
        ],
        'mastodon': [
            r'={70,}\s*MASTODON.*?={70,}',
            r'-{70,}\s*4\.\s*MASTODON.*?-{70,}',
            r'###\s*Mastodon',
        ],
        'reddit': [
            r'={70,}\s*REDDIT.*?={70,}',
            r'-{70,}\s*5\.\s*REDDIT.*?-{70,}',
            r'###\s*Reddit',
        ],
        'facebook': [
            r'={70,}\s*FACEBOOK.*?={70,}',
            r'-{70,}\s*6\.\s*FACEBOOK.*?-{70,}',
            r'###\s*Facebook',
        ],
        'linkedin': [
            r'={70,}\s*LINKEDIN.*?={70,}',
            r'-{70,}\s*7\.\s*LINKEDIN.*?-{70,}',
            r'###\s*LinkedIn',
        ],
        'instagram': [
            r'={70,}\s*INSTAGRAM.*?={70,}',
            r'-{70,}\s*8\.\s*INSTAGRAM.*?-{70,}',
            r'###\s*Instagram',
        ],
    }

    def __init__(self, post_file_path: str):
        """
        Initialize the PostTextParser.

        Args:
            post_file_path: Path to the social posts text file
        """
        self.post_file_path = Path(post_file_path)

        if not self.post_file_path.exists():
            raise FileNotFoundError(f"Post file not found: {post_file_path}")

        self.content = self._load_file()
        self.notebook_name = self._extract_notebook_name()

    def _load_file(self) -> str:
        """Load the post file content."""
        with open(self.post_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_notebook_name(self) -> Optional[str]:
        """Extract the notebook name from the file header."""
        # Look for patterns like "Generated from: notebook_name.ipynb"
        match = re.search(r'Generated from:\s*(\S+\.ipynb)', self.content, re.IGNORECASE)
        if match:
            return match.group(1).replace('.ipynb', '')

        # Fallback: extract from filename
        # e.g., "finite_element_method_heat_transfer_posts.txt" -> "finite_element_method_heat_transfer"
        filename = self.post_file_path.stem
        if filename.endswith('_posts'):
            return filename[:-6]  # Remove "_posts" suffix

        logger.warning(f"Could not extract notebook name from {self.post_file_path}")
        return None

    def _find_platform_section(self, platform: str) -> Optional[str]:
        """
        Find and extract the content for a specific platform.

        Args:
            platform: Platform name (e.g., 'facebook', 'twitter')

        Returns:
            The platform-specific content or None if not found
        """
        platform_lower = platform.lower()

        if platform_lower not in self.PLATFORM_PATTERNS:
            logger.warning(f"Unknown platform: {platform}")
            return None

        patterns = self.PLATFORM_PATTERNS[platform_lower]

        for pattern in patterns:
            # Find the section header
            matches = list(re.finditer(pattern, self.content, re.IGNORECASE | re.DOTALL))

            if matches:
                # Get the end position of the header
                header_end = matches[0].end()

                # Find the next section header (any platform)
                next_section_start = len(self.content)
                for next_patterns in self.PLATFORM_PATTERNS.values():
                    for next_pattern in next_patterns:
                        next_matches = re.finditer(next_pattern, self.content[header_end:], re.IGNORECASE | re.DOTALL)
                        for next_match in next_matches:
                            potential_start = header_end + next_match.start()
                            if potential_start < next_section_start:
                                next_section_start = potential_start
                            break

                # Extract content between this header and next section
                section_content = self.content[header_end:next_section_start]

                # Clean up the content
                cleaned = section_content.strip()

                # Remove any trailing separator lines
                cleaned = re.sub(r'[-=]{70,}\s*$', '', cleaned).strip()

                return cleaned

        logger.warning(f"No {platform} section found in {self.post_file_path}")
        return None

    def get_facebook_post(self) -> Optional[str]:
        """Extract Facebook post content."""
        return self._find_platform_section('facebook')

    def get_twitter_post(self) -> Optional[str]:
        """Extract Twitter/X post content."""
        return self._find_platform_section('twitter')

    def get_linkedin_post(self) -> Optional[str]:
        """Extract LinkedIn post content."""
        return self._find_platform_section('linkedin')

    def get_instagram_post(self) -> Optional[str]:
        """Extract Instagram post content."""
        return self._find_platform_section('instagram')

    def get_all_posts(self) -> Dict[str, Optional[str]]:
        """
        Extract all platform posts.

        Returns:
            Dictionary mapping platform names to post content
        """
        return {
            'facebook': self.get_facebook_post(),
            'twitter': self.get_twitter_post(),
            'linkedin': self.get_linkedin_post(),
            'instagram': self.get_instagram_post(),
            'threads': self._find_platform_section('threads'),
            'mastodon': self._find_platform_section('mastodon'),
            'bluesky': self._find_platform_section('bluesky'),
            'reddit': self._find_platform_section('reddit'),
        }

    def get_cocalc_url(self) -> Optional[str]:
        """
        Extract the CoCalc notebook URL from the content.

        Returns:
            The CoCalc URL or constructs one from the notebook name
        """
        # Look for existing URL in content
        url_match = re.search(r'https://cocalc\.com/github/[^\s\)]+', self.content)
        if url_match:
            return url_match.group(0)

        # Construct URL from notebook name
        if self.notebook_name:
            return f"https://cocalc.com/github/Ok-landscape/computational-pipeline/blob/main/notebooks/published/{self.notebook_name}.ipynb"

        return None


def main():
    """Test the PostTextParser."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Test with a sample file
    test_file = "/home/user/computational-pipeline/social-media-automation/repo-data/output/social_posts/finite_element_method_heat_transfer_posts.txt"

    try:
        parser = PostTextParser(test_file)

        print(f"\n=== Parsing: {parser.post_file_path.name} ===")
        print(f"Notebook name: {parser.notebook_name}")
        print(f"CoCalc URL: {parser.get_cocalc_url()}")

        print("\n=== Facebook Post ===")
        fb_post = parser.get_facebook_post()
        if fb_post:
            print(f"Length: {len(fb_post)} chars")
            print(f"Content preview:\n{fb_post[:200]}...")
        else:
            print("Not found")

        print("\n=== Twitter Post ===")
        twitter_post = parser.get_twitter_post()
        if twitter_post:
            print(f"Length: {len(twitter_post)} chars")
            print(f"Content:\n{twitter_post}")
        else:
            print("Not found")

        print("\n=== All Platforms ===")
        all_posts = parser.get_all_posts()
        for platform, content in all_posts.items():
            status = "✓" if content else "✗"
            char_count = len(content) if content else 0
            print(f"{status} {platform.capitalize()}: {char_count} chars")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
