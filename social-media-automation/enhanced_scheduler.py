#!/usr/bin/env python3
"""
Enhanced Smart Scheduler with Dual-Content Support

Integrates both LaTeX templates and computational notebooks into a unified posting schedule.
Implements dual-page routing with duplicate content handling.
"""

import os
import json
import uuid
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Import existing components
from template_scanner import TemplateScanner, TemplateMetadata
from notebook_scanner import NotebookScanner
from post_text_parser import PostTextParser
from content_generator import ContentGenerator
from media_extractor import MediaExtractor
from notebook_content_extractor import NotebookContentExtractor

# Import new components
from page_router import PageRouter, PageRoute
from unified_queue_manager import UnifiedQueueManager, QueuedContent
from duplicate_content_handler import DuplicateContentHandler
from pre_publish_validator import PrePublishValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedScheduler:
    """Enhanced scheduler with dual-content and dual-page support"""

    # Optimal posting times per platform
    OPTIMAL_TIMES = {
        'facebook': ['09:00', '13:00', '19:00'],
        'threads': ['11:00', '16:00'],
        'instagram': ['10:00', '18:00']
    }

    # Day themes for content selection
    DAY_THEMES = {
        0: ['physics', 'quantum', 'engineering'],  # Monday
        1: ['mathematics', 'algebra', 'calculus'],  # Tuesday
        2: ['machine-learning', 'data-science', 'ai'],  # Wednesday
        3: ['biology', 'chemistry', 'bioinformatics'],  # Thursday
        4: ['statistics', 'numerical-analysis', 'computation'],  # Friday
        5: ['mixed', 'popular'],  # Saturday
        6: ['introductory', 'tutorials']  # Sunday
    }

    def __init__(self):
        """Initialize enhanced scheduler"""
        load_dotenv()

        # Base paths
        self.base_dir = Path("/home/user/computational-pipeline/social-media-automation")
        self.template_base = Path(os.getenv('TEMPLATE_BASE_PATH', '/home/user/latex-templates/templates'))
        self.notebooks_dir = Path(os.getenv('NOTEBOOKS_DIR'))
        self.output_dir = Path(os.getenv('OUTPUT_DIR'))

        # Initialize template components
        self.template_scanner = TemplateScanner()
        self.content_generator = ContentGenerator()
        self.media_extractor = MediaExtractor()

        # Initialize notebook components
        self.notebook_scanner = NotebookScanner(
            str(self.notebooks_dir),
            str(self.output_dir)
        )
        # Note: NotebookContentExtractor is instantiated per-notebook
        self.notebook_images_dir = self.base_dir / "extracted_images"
        self.notebook_images_dir.mkdir(parents=True, exist_ok=True)

        # Initialize new components
        self.page_router = PageRouter()
        self.queue_manager = UnifiedQueueManager()
        self.duplicate_handler = DuplicateContentHandler(
            min_day_gap=int(os.getenv('DUPLICATE_SPREAD_MIN_DAYS', 2))
        )
        self.validator = PrePublishValidator()

        # Configuration
        self.posts_per_day_per_page = int(os.getenv('POSTS_PER_DAY_PER_PAGE', 2))
        self.enable_dual_routing = os.getenv('ENABLE_DUAL_PAGE_ROUTING', 'true').lower() == 'true'

        logger.info("Enhanced Scheduler initialized")
        logger.info(f"  Dual-page routing: {self.enable_dual_routing}")
        logger.info(f"  Posts per day per page: {self.posts_per_day_per_page}")

    def generate_weekly_schedule(self) -> List[QueuedContent]:
        """
        Generate a week's worth of mixed content

        Returns:
            List of QueuedContent items
        """
        logger.info("Generating weekly schedule with mixed content...")

        # Load templates
        if not self.template_scanner.templates:
            logger.info("Loading template index...")
            if not self.template_scanner.load_index():
                logger.info("Building template index...")
                self.template_scanner.scan_all_templates()
                self.template_scanner.save_index()

        # Load notebooks
        notebooks_with_posts = self.notebook_scanner.get_notebooks_with_posts()

        logger.info(f"Available content:")
        logger.info(f"  Templates: {sum(len(t) for t in self.template_scanner.templates.values())}")
        logger.info(f"  Notebooks: {len(notebooks_with_posts)}")

        all_content = []
        start_date = datetime.now()

        # Generate schedule for each day
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            weekday = current_date.weekday()

            logger.info(f"\nScheduling {current_date.strftime('%A, %Y-%m-%d')}...")

            # Get daily theme
            themes = self.DAY_THEMES.get(weekday, ['mixed'])

            # Schedule content for each page
            for page_key, page_info in self.page_router.get_all_pages().items():
                page_id = page_info['id']
                page_name = page_info['name']

                logger.info(f"  Scheduling for {page_name}...")

                # Aim for posts_per_day_per_page
                # Split between templates and notebooks (50/50)
                templates_to_schedule = self.posts_per_day_per_page // 2
                notebooks_to_schedule = self.posts_per_day_per_page - templates_to_schedule

                # Schedule templates
                template_content = self._schedule_templates_for_day(
                    current_date,
                    themes,
                    page_id,
                    page_name,
                    count=templates_to_schedule
                )
                all_content.extend(template_content)

                # Schedule notebooks
                notebook_content = self._schedule_notebooks_for_day(
                    current_date,
                    themes,
                    page_id,
                    page_name,
                    count=notebooks_to_schedule
                )
                all_content.extend(notebook_content)

        logger.info(f"\nGenerated {len(all_content)} content items")

        # Handle duplicates - spread across days
        all_content = self._handle_duplicate_spreading(all_content)

        return all_content

    def _schedule_templates_for_day(self,
                                   date: datetime,
                                   themes: List[str],
                                   page_id: str,
                                   page_name: str,
                                   count: int) -> List[QueuedContent]:
        """Schedule templates for a specific day and page"""
        scheduled = []

        for i in range(count):
            # Select template
            template = self._select_template(themes, page_name)

            if not template:
                logger.warning(f"No suitable template found for {page_name}")
                continue

            # Route template
            routes = self.page_router.route_template(template.to_dict())

            # Check if this page should get this template
            page_routes = [r for r in routes if r.page_id == page_id]

            if not page_routes:
                # This template doesn't go to this page
                continue

            # Select posting time
            hour, minute = self._get_posting_time('facebook', i)
            scheduled_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Generate content
            content_items = self._create_template_content(
                template,
                routes,
                scheduled_time
            )

            scheduled.extend(content_items)

        return scheduled

    def _schedule_notebooks_for_day(self,
                                   date: datetime,
                                   themes: List[str],
                                   page_id: str,
                                   page_name: str,
                                   count: int) -> List[QueuedContent]:
        """Schedule notebooks for a specific day and page"""
        scheduled = []

        notebooks_with_posts = self.notebook_scanner.get_notebooks_with_posts()

        for i in range(count):
            # Select notebook
            notebook = random.choice(notebooks_with_posts) if notebooks_with_posts else None

            if not notebook:
                logger.warning(f"No notebooks available")
                continue

            # Route notebook
            routes = self.page_router.route_notebook(notebook)

            # Check if this page should get this notebook
            page_routes = [r for r in routes if r.page_id == page_id]

            if not page_routes:
                continue

            # Select posting time (offset from template times)
            hour, minute = self._get_posting_time('facebook', i + count)
            scheduled_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Generate content
            content_items = self._create_notebook_content(
                notebook,
                routes,
                scheduled_time
            )

            scheduled.extend(content_items)

        return scheduled

    def _create_template_content(self,
                                template: TemplateMetadata,
                                routes: List[PageRoute],
                                base_time: datetime) -> List[QueuedContent]:
        """Create QueuedContent items for a template"""
        content_items = []

        # Generate post content
        facebook_post = self.content_generator.generate_facebook_post(template)

        # Extract media
        image_path = None
        alt_text = None

        if template.pdf_file and Path(template.pdf_file).exists():
            media = self.media_extractor.extract_from_pdf(
                template.pdf_file,
                template.template_name,
                template.category,
                platforms=['facebook']
            )

            if 'facebook' in media:
                image_path = media['facebook'].image_path
                alt_text = media['facebook'].alt_text

        # Schedule for duplicate handling
        schedule = self.duplicate_handler.schedule_duplicate_content(routes, base_time)

        # Create content for each scheduled page
        for sched in schedule.schedules:
            # Tailor content for page
            tailored_content = self.duplicate_handler.tailor_message_for_page(
                facebook_post.content,
                sched['page_id'],
                sched['page_name'],
                'template'
            )

            # Adjust hashtags
            tailored_hashtags = self.duplicate_handler.adjust_hashtags_for_page(
                facebook_post.hashtags,
                sched['page_name']
            )

            content = QueuedContent(
                content_id=str(uuid.uuid4()),
                content_type='template',
                page_id=sched['page_id'],
                page_name=sched['page_name'],
                platform='facebook',
                content_text=tailored_content,
                hashtags=tailored_hashtags,
                link=facebook_post.link,
                image_path=image_path,
                alt_text=alt_text,
                source_name=template.template_name,
                category=template.category,
                scheduled_time=sched['scheduled_time'].isoformat(),
                priority=self._calculate_template_priority(template),
                is_duplicate=len(routes) > 1,
                duplicate_group_id=schedule.duplicate_group_id if len(routes) > 1 else None
            )

            content_items.append(content)

        return content_items

    def _create_notebook_content(self,
                                notebook: Dict,
                                routes: List[PageRoute],
                                base_time: datetime) -> List[QueuedContent]:
        """Create QueuedContent items for a notebook"""
        content_items = []

        # Parse post file
        post_file = notebook.get('post_file')
        if not post_file:
            logger.warning(f"No post file for notebook {notebook['basename']}")
            return []

        try:
            parser = PostTextParser(post_file)
            facebook_content = parser.get_facebook_post()

            if not facebook_content:
                logger.warning(f"No Facebook content in {post_file}")
                return []

            # Get notebook URL
            link = parser.get_cocalc_url()

            # Extract hashtags from content
            hashtags = self._extract_hashtags_from_text(facebook_content)

            # Get image
            image_path = None
            try:
                notebook_path = notebook.get('path')
                if notebook_path and Path(notebook_path).exists():
                    extractor = NotebookContentExtractor(notebook_path)
                    images = extractor.extract_images()
                    if images:
                        image_path = images[0]  # Use first image
            except Exception as e:
                logger.warning(f"Could not extract images from {notebook['basename']}: {e}")

            # Schedule for duplicate handling
            schedule = self.duplicate_handler.schedule_duplicate_content(routes, base_time)

            # Create content for each scheduled page
            for sched in schedule.schedules:
                # Tailor content for page
                tailored_content = self.duplicate_handler.tailor_message_for_page(
                    facebook_content,
                    sched['page_id'],
                    sched['page_name'],
                    'notebook'
                )

                # Adjust hashtags
                tailored_hashtags = self.duplicate_handler.adjust_hashtags_for_page(
                    hashtags,
                    sched['page_name']
                )

                content = QueuedContent(
                    content_id=str(uuid.uuid4()),
                    content_type='notebook',
                    page_id=sched['page_id'],
                    page_name=sched['page_name'],
                    platform='facebook',
                    content_text=tailored_content,
                    hashtags=tailored_hashtags,
                    link=link or '',
                    image_path=image_path,
                    alt_text=f"Computational notebook: {notebook['basename']}",
                    source_name=notebook['basename'],
                    category='computational-notebook',
                    scheduled_time=sched['scheduled_time'].isoformat(),
                    priority=5,
                    is_duplicate=len(routes) > 1,
                    duplicate_group_id=schedule.duplicate_group_id if len(routes) > 1 else None
                )

                content_items.append(content)

        except Exception as e:
            logger.error(f"Error creating notebook content: {e}")

        return content_items

    def _handle_duplicate_spreading(self, content_items: List[QueuedContent]) -> List[QueuedContent]:
        """
        Ensure duplicate content is properly spread across days

        Args:
            content_items: List of content items

        Returns:
            Adjusted content items
        """
        # Group by duplicate_group_id
        duplicate_groups = {}
        non_duplicates = []

        for item in content_items:
            if item.is_duplicate and item.duplicate_group_id:
                if item.duplicate_group_id not in duplicate_groups:
                    duplicate_groups[item.duplicate_group_id] = []
                duplicate_groups[item.duplicate_group_id].append(item)
            else:
                non_duplicates.append(item)

        # Process each duplicate group
        adjusted_items = non_duplicates.copy()

        for group_id, group_items in duplicate_groups.items():
            # Sort by scheduled time
            group_items.sort(key=lambda x: x.scheduled_time)

            # Ensure minimum day gap
            min_gap = timedelta(days=self.duplicate_handler.min_day_gap)

            for i in range(1, len(group_items)):
                prev_time = datetime.fromisoformat(group_items[i-1].scheduled_time)
                curr_time = datetime.fromisoformat(group_items[i].scheduled_time)

                if curr_time - prev_time < min_gap:
                    # Adjust time
                    new_time = prev_time + min_gap
                    group_items[i].scheduled_time = new_time.isoformat()
                    logger.info(f"Adjusted duplicate to maintain {self.duplicate_handler.min_day_gap} day gap")

            adjusted_items.extend(group_items)

        return adjusted_items

    def _select_template(self, themes: List[str], page_name: str) -> Optional[TemplateMetadata]:
        """Select appropriate template based on themes and page"""
        candidates = []

        # Get all templates
        all_templates = []
        for templates in self.template_scanner.templates.values():
            all_templates.extend(templates)

        # Filter by theme if not mixed
        if 'mixed' not in themes:
            for template in all_templates:
                for theme in themes:
                    if theme in template.category.lower():
                        candidates.append(template)
        else:
            candidates = all_templates

        # Further filter by page requirements
        if 'SageMath' in page_name:
            # Prefer SageTeX templates for SageMath page
            sagemath_candidates = [t for t in candidates if t.has_sagetex]
            if sagemath_candidates:
                candidates = sagemath_candidates

        return random.choice(candidates) if candidates else None

    def _calculate_template_priority(self, template: TemplateMetadata) -> int:
        """Calculate priority for template"""
        priority = 5

        if template.complexity_score >= 4:
            priority += 2
        elif template.complexity_score >= 3:
            priority += 1

        if template.has_sagetex or template.has_pythontex:
            priority += 1

        return min(priority, 10)

    def _get_posting_time(self, platform: str, index: int) -> Tuple[int, int]:
        """Get posting time for platform and index"""
        times = self.OPTIMAL_TIMES.get(platform, ['10:00'])
        time_str = times[index % len(times)]
        hour, minute = map(int, time_str.split(':'))
        return hour, minute

    def _extract_hashtags_from_text(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags[:10]  # Limit

    def add_to_queue(self, content_items: List[QueuedContent]):
        """Add content to queue"""
        self.queue_manager.add_batch(content_items)
        logger.info(f"Added {len(content_items)} items to queue")

    def get_queue_statistics(self) -> Dict:
        """Get queue statistics"""
        return self.queue_manager.get_statistics()

    def validate_queue(self) -> List[str]:
        """Validate queue for issues"""
        return self.queue_manager.validate_no_same_day_duplicates()


def main():
    """Test enhanced scheduler"""
    scheduler = EnhancedScheduler()

    print("\n" + "="*60)
    print("Enhanced Scheduler Test")
    print("="*60)

    # Generate weekly schedule
    print("\nGenerating weekly schedule...")
    content_items = scheduler.generate_weekly_schedule()

    print(f"\nGenerated {len(content_items)} content items")

    # Add to queue
    scheduler.add_to_queue(content_items)

    # Get statistics
    stats = scheduler.get_queue_statistics()

    print("\n" + "="*60)
    print("Queue Statistics")
    print("="*60)
    print(f"Total queued: {stats['total_queued']}")
    print(f"Next 24 hours: {stats['next_24h']}")
    print(f"Next 7 days: {stats['next_7days']}")
    print(f"Duplicate items: {stats['duplicates']}")

    print("\nBy content type:")
    for ctype, count in stats['by_content_type'].items():
        print(f"  {ctype}: {count}")

    print("\nBy page:")
    for page, count in stats['by_page'].items():
        print(f"  {page}: {count}")

    # Validate
    print("\n" + "="*60)
    print("Validation")
    print("="*60)

    warnings = scheduler.validate_queue()
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    else:
        print("  No issues found!")

    # Show sample schedule
    print("\n" + "="*60)
    print("Sample Daily Schedule (Next 3 Days)")
    print("="*60)

    for day_offset in range(3):
        date = datetime.now() + timedelta(days=day_offset)
        daily = scheduler.queue_manager.get_daily_schedule(date)

        print(f"\n{date.strftime('%A, %B %d, %Y')}:")

        for page_id, content_list in daily.items():
            page_info = scheduler.page_router.get_page_info(page_id)
            page_name = page_info['name'] if page_info else page_id

            print(f"\n  {page_name}:")
            for content in content_list:
                time_obj = datetime.fromisoformat(content.scheduled_time)
                print(f"    {time_obj.strftime('%H:%M')} - {content.content_type}: {content.source_name}")
                if content.is_duplicate:
                    print(f"              (Duplicate content)")


if __name__ == "__main__":
    main()
