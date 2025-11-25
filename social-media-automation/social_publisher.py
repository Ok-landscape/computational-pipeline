#!/usr/bin/env python3
"""
Multi-Platform Social Media Publisher

Publishes content to Facebook, Threads, and Instagram using Graph API.
Handles authentication, rate limiting, and error recovery.
"""

import os
import time
import logging
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from pre_publish_validator import PrePublishValidator, ValidationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    """Result of a publishing operation"""
    success: bool
    platform: str
    post_id: Optional[str]
    error_message: Optional[str]
    timestamp: str
    template_name: str

    def to_dict(self) -> Dict:
        return asdict(self)


class SocialMediaPublisher:
    """Multi-platform social media publisher"""

    GRAPH_API_VERSION = "v24.0"
    GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

    def __init__(self, env_file: str = "/home/user/computational-pipeline/social-media-automation/.env"):
        """
        Initialize social media publisher

        Args:
            env_file: Path to .env file with credentials
        """
        load_dotenv(env_file)

        # Facebook/Threads credentials
        self.fb_page_id = os.getenv('FB_PAGE_ID')  # Legacy default
        self.fb_page_token = os.getenv('FB_PAGE_TOKEN')

        # Dual-page configuration
        self.fb_page_id_cocalc = os.getenv('FB_PAGE_ID_COCALC', self.fb_page_id)
        self.fb_page_id_sagemath = os.getenv('FB_PAGE_ID_SAGEMATH')

        # Page-specific access tokens (fetched on demand)
        self.page_access_tokens = {}

        # Instagram credentials
        self.ig_account_id = os.getenv('IG_BUSINESS_ACCOUNT_ID')
        self.ig_access_token = os.getenv('IG_ACCESS_TOKEN', self.fb_page_token)

        # Rate limiting tracking
        self.rate_limits = {
            'facebook': {'remaining': 200, 'reset_time': time.time()},
            'instagram': {'remaining': 50, 'reset_time': time.time()},
            'threads': {'remaining': 100, 'reset_time': time.time()}
        }

        # Publishing history
        self.history_file = Path("/home/user/computational-pipeline/social-media-automation/data/publish_history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.publishing_history = self._load_history()

        logger.info("Social Media Publisher initialized")

    def _get_page_access_token(self, page_id: str) -> Optional[str]:
        """
        Get page-specific access token

        Args:
            page_id: Facebook page ID

        Returns:
            Page access token or None if not found
        """
        # Return cached token if available
        if page_id in self.page_access_tokens:
            return self.page_access_tokens[page_id]

        # Fetch page token from Graph API
        try:
            url = f"{self.GRAPH_API_BASE}/{page_id}?fields=access_token&access_token={self.fb_page_token}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'access_token' in data:
                page_token = data['access_token']
                self.page_access_tokens[page_id] = page_token
                logger.info(f"Fetched page access token for page {page_id}")
                return page_token
            else:
                logger.error(f"No access token in response for page {page_id}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch page access token: {e}")
            return None

    def publish_to_facebook(self,
                           content: str,
                           link: str,
                           image_path: Optional[str] = None,
                           template_name: str = "",
                           page_id: Optional[str] = None) -> PublishResult:
        """
        Publish post to Facebook Page

        Args:
            content: Post text content
            link: Link to include in post
            image_path: Optional path to image
            template_name: Template identifier for tracking
            page_id: Specific page ID to post to (optional, uses default if not provided)

        Returns:
            PublishResult object
        """
        # Use provided page_id or default
        target_page_id = page_id or self.fb_page_id

        if not target_page_id or not self.fb_page_token:
            logger.error("Facebook credentials not configured")
            return PublishResult(
                success=False,
                platform='facebook',
                post_id=None,
                error_message="Missing credentials",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        # Check rate limits
        if not self._check_rate_limit('facebook'):
            logger.warning("Facebook rate limit reached, waiting...")
            time.sleep(60)

        try:
            if image_path and Path(image_path).exists():
                # Post with photo
                result = self._post_facebook_photo(content, image_path, target_page_id)
            else:
                # Post with link
                result = self._post_facebook_text(content, link, target_page_id)

            if result['success']:
                logger.info(f"Published to Facebook page {target_page_id}: {result['post_id']}")
                self._record_publish('facebook', template_name, result['post_id'], target_page_id)

                return PublishResult(
                    success=True,
                    platform='facebook',
                    post_id=result['post_id'],
                    error_message=None,
                    timestamp=datetime.now().isoformat(),
                    template_name=template_name
                )
            else:
                logger.error(f"Facebook publish failed: {result['error']}")
                return PublishResult(
                    success=False,
                    platform='facebook',
                    post_id=None,
                    error_message=result['error'],
                    timestamp=datetime.now().isoformat(),
                    template_name=template_name
                )

        except Exception as e:
            logger.error(f"Exception publishing to Facebook: {e}")
            return PublishResult(
                success=False,
                platform='facebook',
                post_id=None,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

    def publish_to_threads(self,
                          content: str,
                          link: str,
                          image_path: Optional[str] = None,
                          template_name: str = "") -> PublishResult:
        """
        Publish post to Threads

        Note: Threads API uses Facebook infrastructure but different endpoints

        Args:
            content: Post text content
            link: Link to include
            image_path: Optional image
            template_name: Template identifier

        Returns:
            PublishResult object
        """
        if not self.fb_page_token:
            logger.error("Threads credentials not configured")
            return PublishResult(
                success=False,
                platform='threads',
                post_id=None,
                error_message="Missing credentials",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        # Check rate limits
        if not self._check_rate_limit('threads'):
            logger.warning("Threads rate limit reached, waiting...")
            time.sleep(60)

        try:
            # Threads posting via Graph API
            # Step 1: Create container
            url = f"{self.GRAPH_API_BASE}/me/threads"

            payload = {
                'text': content,
                'access_token': self.fb_page_token
            }

            # Add image if provided
            if image_path and Path(image_path).exists():
                payload['media_type'] = 'IMAGE'
                # For Threads, we need to upload image first or use URL
                # This is simplified - in production, implement full media upload
                payload['image_url'] = link  # Fallback to link

            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()

            if 'id' in data:
                container_id = data['id']

                # Step 2: Publish container
                publish_url = f"{self.GRAPH_API_BASE}/{container_id}/publish"
                publish_payload = {
                    'access_token': self.fb_page_token
                }

                publish_response = requests.post(publish_url, data=publish_payload)
                publish_response.raise_for_status()
                publish_data = publish_response.json()

                if 'id' in publish_data:
                    post_id = publish_data['id']
                    logger.info(f"Published to Threads: {post_id}")
                    self._record_publish('threads', template_name, post_id)

                    return PublishResult(
                        success=True,
                        platform='threads',
                        post_id=post_id,
                        error_message=None,
                        timestamp=datetime.now().isoformat(),
                        template_name=template_name
                    )

            return PublishResult(
                success=False,
                platform='threads',
                post_id=None,
                error_message="Failed to publish container",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Threads API error: {e}")
            return PublishResult(
                success=False,
                platform='threads',
                post_id=None,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )
        except Exception as e:
            logger.error(f"Exception publishing to Threads: {e}")
            return PublishResult(
                success=False,
                platform='threads',
                post_id=None,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

    def publish_to_instagram(self,
                            content: str,
                            image_path: str,
                            template_name: str = "") -> PublishResult:
        """
        Publish post to Instagram

        Instagram requires an image for all posts

        Args:
            content: Caption text
            image_path: Path to image (required)
            template_name: Template identifier

        Returns:
            PublishResult object
        """
        if not self.ig_account_id or not self.ig_access_token:
            logger.error("Instagram credentials not configured")
            return PublishResult(
                success=False,
                platform='instagram',
                post_id=None,
                error_message="Missing credentials",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        if not image_path or not Path(image_path).exists():
            logger.error("Instagram requires an image")
            return PublishResult(
                success=False,
                platform='instagram',
                post_id=None,
                error_message="Image required for Instagram",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        # Check rate limits
        if not self._check_rate_limit('instagram'):
            logger.warning("Instagram rate limit reached, waiting...")
            time.sleep(60)

        try:
            # Step 1: Create media container
            # Note: Image must be accessible via public URL
            # For local files, need to upload to temporary hosting
            # This is a simplified version

            container_url = f"{self.GRAPH_API_BASE}/{self.ig_account_id}/media"

            # In production, upload image to CDN and get URL
            # For now, we'll use direct upload (if supported) or skip
            logger.warning("Instagram publishing requires public image URL - implementation needed")

            # Placeholder for container creation
            container_payload = {
                'caption': content,
                'access_token': self.ig_access_token
            }

            # This is incomplete - Instagram API requires public image URLs
            # Full implementation would need image hosting service

            return PublishResult(
                success=False,
                platform='instagram',
                post_id=None,
                error_message="Instagram publishing requires image hosting setup",
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

        except Exception as e:
            logger.error(f"Exception publishing to Instagram: {e}")
            return PublishResult(
                success=False,
                platform='instagram',
                post_id=None,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                template_name=template_name
            )

    def _post_facebook_text(self, message: str, link: str, page_id: str = None) -> Dict:
        """Post text with link to Facebook"""
        target_page_id = page_id or self.fb_page_id

        # Get page-specific access token
        page_token = self._get_page_access_token(target_page_id)
        if not page_token:
            return {'success': False, 'error': 'Failed to get page access token'}

        url = f"{self.GRAPH_API_BASE}/{target_page_id}/feed"

        payload = {
            'message': message,
            'link': link,
            'access_token': page_token
        }

        try:
            response = requests.post(url, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'id' in data:
                return {'success': True, 'post_id': data['id']}
            else:
                return {'success': False, 'error': data.get('error', {}).get('message', 'Unknown error')}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    def _post_facebook_photo(self, message: str, image_path: str, page_id: str = None) -> Dict:
        """Post photo with caption to Facebook"""
        target_page_id = page_id or self.fb_page_id

        # Get page-specific access token
        page_token = self._get_page_access_token(target_page_id)
        if not page_token:
            return {'success': False, 'error': 'Failed to get page access token'}

        url = f"{self.GRAPH_API_BASE}/{target_page_id}/photos"

        payload = {
            'message': message,
            'access_token': page_token,
            'published': 'true'
        }

        try:
            with open(image_path, 'rb') as image_file:
                files = {
                    'source': image_file
                }

                response = requests.post(url, data=payload, files=files, timeout=60)
                response.raise_for_status()
                data = response.json()

                if 'id' in data:
                    return {'success': True, 'post_id': data['id']}
                else:
                    return {'success': False, 'error': data.get('error', {}).get('message', 'Unknown error')}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _check_rate_limit(self, platform: str) -> bool:
        """
        Check if we're within rate limits

        Args:
            platform: Platform name

        Returns:
            True if within limits, False otherwise
        """
        if platform not in self.rate_limits:
            return True

        limits = self.rate_limits[platform]

        # Reset counter if time window passed
        if time.time() > limits['reset_time']:
            limits['remaining'] = {
                'facebook': 200,
                'instagram': 50,
                'threads': 100
            }.get(platform, 100)
            limits['reset_time'] = time.time() + 3600  # 1 hour window

        if limits['remaining'] > 0:
            limits['remaining'] -= 1
            return True

        return False

    def _record_publish(self, platform: str, template_name: str, post_id: str, page_id: str = None):
        """Record successful publish to history"""
        record = {
            'platform': platform,
            'template_name': template_name,
            'post_id': post_id,
            'page_id': page_id or self.fb_page_id,
            'timestamp': datetime.now().isoformat()
        }

        self.publishing_history.append(record)
        self._save_history()

    def _load_history(self) -> List[Dict]:
        """Load publishing history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return []
        return []

    def _save_history(self):
        """Save publishing history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.publishing_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def get_recently_published(self, platform: Optional[str] = None, days: int = 30) -> List[Dict]:
        """
        Get recently published templates

        Args:
            platform: Optional platform filter
            days: Number of days to look back

        Returns:
            List of published records
        """
        cutoff = datetime.now() - timedelta(days=days)

        recent = []
        for record in self.publishing_history:
            try:
                record_time = datetime.fromisoformat(record['timestamp'])
                if record_time > cutoff:
                    if platform is None or record['platform'] == platform:
                        recent.append(record)
            except:
                continue

        return recent

    def validate_credentials(self) -> Dict[str, bool]:
        """
        Validate credentials for all platforms

        Returns:
            Dictionary mapping platform names to validation status
        """
        results = {
            'facebook': False,
            'threads': False,
            'instagram': False
        }

        # Validate Facebook
        if self.fb_page_token:
            try:
                url = f"{self.GRAPH_API_BASE}/me"
                params = {'access_token': self.fb_page_token}
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    results['facebook'] = True
                    results['threads'] = True  # Threads uses same token
                    logger.info("Facebook/Threads credentials valid")
                else:
                    logger.error(f"Facebook token invalid: {response.text}")

            except Exception as e:
                logger.error(f"Error validating Facebook token: {e}")

        # Validate Instagram
        if self.ig_account_id and self.ig_access_token:
            try:
                url = f"{self.GRAPH_API_BASE}/{self.ig_account_id}"
                params = {
                    'fields': 'username',
                    'access_token': self.ig_access_token
                }
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    results['instagram'] = True
                    logger.info("Instagram credentials valid")
                else:
                    logger.error(f"Instagram token invalid: {response.text}")

            except Exception as e:
                logger.error(f"Error validating Instagram token: {e}")

        return results


def main():
    """Test publisher"""
    publisher = SocialMediaPublisher()

    # Validate credentials
    print("Validating credentials...")
    validation = publisher.validate_credentials()

    for platform, valid in validation.items():
        status = "✓ Valid" if valid else "✗ Invalid"
        print(f"{platform}: {status}")

    # Test Facebook post
    if validation['facebook']:
        print("\nTesting Facebook post...")
        result = publisher.publish_to_facebook(
            content="Test post from LaTeX Template Social Media Automation system!",
            link="https://cocalc.com/github/Ok-landscape/computational-pipeline",
            template_name="test_template"
        )

        if result.success:
            print(f"✓ Published to Facebook: {result.post_id}")
        else:
            print(f"✗ Failed: {result.error_message}")


if __name__ == "__main__":
    main()
