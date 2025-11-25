#!/usr/bin/env python3
"""
Smart Scheduler and Queue Management System

Manages posting schedule, content queue, and prevents duplicates.
Implements intelligent template selection and optimal posting times.
"""

import os
import json
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import schedule
import time

from template_scanner import TemplateScanner, TemplateMetadata
from content_generator import ContentGenerator
from media_extractor import MediaExtractor
from social_publisher import SocialMediaPublisher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueuedPost:
    """Queued post waiting to be published"""
    template: TemplateMetadata
    platform: str
    content: str
    hashtags: List[str]
    link: str
    image_path: Optional[str]
    alt_text: Optional[str]
    scheduled_time: str
    priority: int = 5
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert template to dict
        data['template'] = self.template.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'QueuedPost':
        """Create QueuedPost from dictionary"""
        template_data = data.pop('template')
        template = TemplateMetadata(**template_data)
        return cls(template=template, **data)


class SmartScheduler:
    """Intelligent scheduling and queue management"""

    # Optimal posting times (24-hour format)
    OPTIMAL_TIMES = {
        'facebook': ['09:00', '13:00', '19:00'],
        'threads': ['11:00', '16:00'],
        'instagram': ['10:00', '18:00']
    }

    # Day-specific content themes
    DAY_THEMES = {
        0: ['physics', 'quantum-physics', 'astrophysics'],  # Monday: Physics
        1: ['mathematics', 'numerical-analysis', 'algebra'],  # Tuesday: Math
        2: ['machine-learning', 'computer-science', 'ai'],  # Wednesday: ML/AI
        3: ['engineering', 'robotics', 'control-theory'],  # Thursday: Engineering
        4: ['biology', 'chemistry', 'bioinformatics'],  # Friday: Life Sciences
        5: ['mixed'],  # Saturday: Popular topics
        6: ['mixed']  # Sunday: Introductory topics
    }

    def __init__(self):
        """Initialize scheduler"""
        self.base_dir = Path("/home/user/computational-pipeline/social-media-automation")
        self.queue_file = self.base_dir / "data" / "post_queue.json"
        self.config_file = self.base_dir / "config" / "scheduler_config.json"

        # Initialize components
        self.scanner = TemplateScanner()
        self.generator = ContentGenerator()
        self.extractor = MediaExtractor()
        self.publisher = SocialMediaPublisher()

        # Load or create queue
        self.queue: List[QueuedPost] = self._load_queue()

        # Load configuration
        self.config = self._load_config()

        # Recently used templates (avoid duplicates)
        self.recent_templates: Dict[str, List[str]] = {
            'facebook': [],
            'threads': [],
            'instagram': []
        }

        self._load_recent_templates()

        logger.info("Smart Scheduler initialized")

    def generate_weekly_schedule(self) -> List[QueuedPost]:
        """
        Generate a week's worth of scheduled posts

        Returns:
            List of queued posts
        """
        logger.info("Generating weekly schedule...")

        scheduled_posts = []
        start_date = datetime.now()

        # Load template index
        if not self.scanner.templates:
            logger.info("Loading template index...")
            if not self.scanner.load_index():
                logger.info("Building new index...")
                self.scanner.scan_all_templates()
                self.scanner.save_index()

        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            weekday = current_date.weekday()

            # Get theme for this day
            themes = self.DAY_THEMES.get(weekday, ['mixed'])

            # Schedule posts for each platform
            for platform, times in self.OPTIMAL_TIMES.items():
                for post_time in times:
                    # Check if we should post (max posts per day per platform)
                    max_daily = self.config.get('max_posts_per_day', {}).get(platform, 2)

                    # Get suitable template
                    template = self._select_template_for_day(themes, platform)

                    if template:
                        # Generate scheduled time
                        hour, minute = map(int, post_time.split(':'))
                        scheduled_dt = current_date.replace(hour=hour, minute=minute, second=0)

                        # Generate content
                        post = self._generate_post_for_platform(template, platform, scheduled_dt)

                        if post:
                            scheduled_posts.append(post)
                            logger.info(f"Scheduled {platform} post: {template.template_name} at {scheduled_dt}")

                            # Add to recent list
                            if template.template_name not in self.recent_templates[platform]:
                                self.recent_templates[platform].append(template.template_name)

        logger.info(f"Generated {len(scheduled_posts)} scheduled posts")
        return scheduled_posts

    def _select_template_for_day(self, themes: List[str], platform: str) -> Optional[TemplateMetadata]:
        """
        Select appropriate template for the day's theme

        Args:
            themes: List of category themes for the day
            platform: Target platform

        Returns:
            TemplateMetadata or None
        """
        # Get templates matching themes
        candidates = []

        if 'mixed' in themes:
            # Any template
            for templates in self.scanner.templates.values():
                candidates.extend(templates)
        else:
            # Filter by theme
            for category, templates in self.scanner.templates.items():
                for theme in themes:
                    if theme in category or category.startswith(theme):
                        candidates.extend(templates)

        if not candidates:
            # Fallback to any template
            for templates in self.scanner.templates.values():
                candidates.extend(templates)

        # Filter out recently used
        recent = self.recent_templates.get(platform, [])
        candidates = [t for t in candidates if t.template_name not in recent[-30:]]  # Last 30 posts

        if not candidates:
            # All templates used recently, start fresh
            self.recent_templates[platform] = []
            candidates = []
            for templates in self.scanner.templates.values():
                candidates.extend(templates)

        # Select random from candidates
        return random.choice(candidates) if candidates else None

    def _generate_post_for_platform(self,
                                   template: TemplateMetadata,
                                   platform: str,
                                   scheduled_time: datetime) -> Optional[QueuedPost]:
        """
        Generate complete post for platform

        Args:
            template: Template metadata
            platform: Target platform
            scheduled_time: When to post

        Returns:
            QueuedPost or None
        """
        try:
            # Generate content
            if platform == 'facebook':
                post = self.generator.generate_facebook_post(template)
            elif platform == 'threads':
                post = self.generator.generate_threads_post(template)
            elif platform == 'instagram':
                post = self.generator.generate_instagram_post(template)
            else:
                logger.error(f"Unknown platform: {platform}")
                return None

            # Extract/prepare media
            image_path = None
            alt_text = None

            if template.pdf_file and Path(template.pdf_file).exists():
                media = self.extractor.extract_from_pdf(
                    template.pdf_file,
                    template.template_name,
                    template.category,
                    platforms=[platform]
                )

                if platform in media:
                    image_path = media[platform].image_path
                    alt_text = media[platform].alt_text

            # Create queued post
            return QueuedPost(
                template=template,
                platform=platform,
                content=post.content,
                hashtags=post.hashtags,
                link=post.link,
                image_path=image_path,
                alt_text=alt_text,
                scheduled_time=scheduled_time.isoformat(),
                priority=self._calculate_priority(template, platform)
            )

        except Exception as e:
            logger.error(f"Error generating post: {e}")
            return None

    def _calculate_priority(self, template: TemplateMetadata, platform: str) -> int:
        """
        Calculate post priority (1-10, higher is more important)

        Args:
            template: Template metadata
            platform: Target platform

        Returns:
            Priority score
        """
        priority = 5  # Base priority

        # Boost for complex templates
        if template.complexity_score >= 4:
            priority += 2
        elif template.complexity_score >= 3:
            priority += 1

        # Boost for templates with visualizations
        if template.plot_files and len(template.plot_files) > 0:
            priority += 1

        # Boost for computational templates
        if template.has_pythontex or template.has_sagetex:
            priority += 1

        # Platform-specific adjustments
        if platform == 'instagram' and template.plot_files:
            priority += 1  # Instagram loves visuals

        return min(priority, 10)

    def add_to_queue(self, posts: List[QueuedPost]):
        """Add posts to queue"""
        self.queue.extend(posts)
        self.queue.sort(key=lambda x: (x.scheduled_time, -x.priority))
        self._save_queue()
        logger.info(f"Added {len(posts)} posts to queue. Total: {len(self.queue)}")

    def get_posts_due(self, within_minutes: int = 5) -> List[QueuedPost]:
        """
        Get posts that are due to be published

        Args:
            within_minutes: Look ahead this many minutes

        Returns:
            List of due posts
        """
        now = datetime.now()
        cutoff = now + timedelta(minutes=within_minutes)

        due_posts = []
        for post in self.queue:
            try:
                scheduled = datetime.fromisoformat(post.scheduled_time)
                if now <= scheduled <= cutoff:
                    due_posts.append(post)
            except:
                continue

        return due_posts

    def publish_post(self, post: QueuedPost) -> bool:
        """
        Publish a queued post

        Args:
            post: QueuedPost to publish

        Returns:
            True if successful
        """
        logger.info(f"Publishing {post.platform} post for {post.template.template_name}")

        try:
            if post.platform == 'facebook':
                result = self.publisher.publish_to_facebook(
                    content=post.content,
                    link=post.link,
                    image_path=post.image_path,
                    template_name=post.template.template_name
                )
            elif post.platform == 'threads':
                result = self.publisher.publish_to_threads(
                    content=post.content,
                    link=post.link,
                    image_path=post.image_path,
                    template_name=post.template.template_name
                )
            elif post.platform == 'instagram':
                if not post.image_path:
                    logger.error("Instagram requires image")
                    return False

                result = self.publisher.publish_to_instagram(
                    content=post.content,
                    image_path=post.image_path,
                    template_name=post.template.template_name
                )
            else:
                logger.error(f"Unknown platform: {post.platform}")
                return False

            if result.success:
                # Remove from queue
                self.queue = [p for p in self.queue if p != post]
                self._save_queue()
                logger.info(f"Successfully published: {result.post_id}")
                return True
            else:
                logger.error(f"Publish failed: {result.error_message}")
                # Reschedule for later
                self._reschedule_post(post)
                return False

        except Exception as e:
            logger.error(f"Exception publishing post: {e}")
            self._reschedule_post(post)
            return False

    def _reschedule_post(self, post: QueuedPost):
        """Reschedule failed post for later"""
        try:
            old_time = datetime.fromisoformat(post.scheduled_time)
            new_time = old_time + timedelta(hours=1)
            post.scheduled_time = new_time.isoformat()
            logger.info(f"Rescheduled post to {new_time}")
            self._save_queue()
        except Exception as e:
            logger.error(f"Error rescheduling post: {e}")

    def run_scheduler_loop(self):
        """
        Run continuous scheduling loop

        Checks for due posts every minute
        """
        logger.info("Starting scheduler loop...")

        def check_and_publish():
            """Check for due posts and publish them"""
            due_posts = self.get_posts_due(within_minutes=1)

            for post in due_posts:
                self.publish_post(post)

        # Schedule the check every minute
        schedule.every(1).minutes.do(check_and_publish)

        # Also regenerate queue weekly
        def regenerate_queue():
            """Regenerate weekly schedule"""
            logger.info("Regenerating weekly queue...")
            new_posts = self.generate_weekly_schedule()
            self.add_to_queue(new_posts)

        schedule.every().sunday.at("00:00").do(regenerate_queue)

        # Initial queue generation if empty
        if len(self.queue) == 0:
            logger.info("Queue empty, generating initial schedule...")
            initial_posts = self.generate_weekly_schedule()
            self.add_to_queue(initial_posts)

        # Main loop
        logger.info("Scheduler loop running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

    def _load_queue(self) -> List[QueuedPost]:
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    return [QueuedPost.from_dict(p) for p in data]
            except Exception as e:
                logger.error(f"Error loading queue: {e}")
                return []
        return []

    def _save_queue(self):
        """Save queue to file"""
        try:
            self.queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.queue_file, 'w') as f:
                data = [p.to_dict() for p in self.queue]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving queue: {e}")

    def _load_config(self) -> Dict:
        """Load scheduler configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")

        # Default configuration
        return {
            'max_posts_per_day': {
                'facebook': 3,
                'threads': 2,
                'instagram': 1
            },
            'avoid_duplicate_days': 60,
            'prioritize_visuals': True
        }

    def _load_recent_templates(self):
        """Load recently used templates from publish history"""
        history = self.publisher.get_recently_published(days=60)

        for record in history:
            platform = record.get('platform')
            template_name = record.get('template_name')

            if platform and template_name:
                if platform not in self.recent_templates:
                    self.recent_templates[platform] = []
                if template_name not in self.recent_templates[platform]:
                    self.recent_templates[platform].append(template_name)

    def get_queue_status(self) -> Dict:
        """Get queue statistics"""
        stats = {
            'total_queued': len(self.queue),
            'by_platform': {},
            'next_24_hours': 0,
            'next_post': None
        }

        for post in self.queue:
            platform = post.platform
            if platform not in stats['by_platform']:
                stats['by_platform'][platform] = 0
            stats['by_platform'][platform] += 1

        # Count posts in next 24 hours
        now = datetime.now()
        cutoff = now + timedelta(days=1)

        for post in self.queue:
            try:
                scheduled = datetime.fromisoformat(post.scheduled_time)
                if now <= scheduled <= cutoff:
                    stats['next_24_hours'] += 1
            except:
                continue

        # Next post
        if self.queue:
            stats['next_post'] = {
                'template': self.queue[0].template.template_name,
                'platform': self.queue[0].platform,
                'scheduled': self.queue[0].scheduled_time
            }

        return stats


def main():
    """Main execution"""
    scheduler = SmartScheduler()

    # Show queue status
    status = scheduler.get_queue_status()
    print("="*60)
    print("Queue Status")
    print("="*60)
    print(f"Total queued posts: {status['total_queued']}")
    print(f"Posts in next 24 hours: {status['next_24_hours']}")
    print("\nBy platform:")
    for platform, count in status['by_platform'].items():
        print(f"  {platform}: {count} posts")

    if status['next_post']:
        print(f"\nNext post:")
        print(f"  Template: {status['next_post']['template']}")
        print(f"  Platform: {status['next_post']['platform']}")
        print(f"  Scheduled: {status['next_post']['scheduled']}")

    # Generate weekly schedule if queue is low
    if status['total_queued'] < 10:
        print("\nQueue low, generating weekly schedule...")
        posts = scheduler.generate_weekly_schedule()
        scheduler.add_to_queue(posts)
        print(f"Added {len(posts)} posts to queue")

    # Option to run scheduler loop
    print("\nStart scheduler loop? (y/n): ", end='')
    response = input().strip().lower()

    if response == 'y':
        scheduler.run_scheduler_loop()


if __name__ == "__main__":
    main()
