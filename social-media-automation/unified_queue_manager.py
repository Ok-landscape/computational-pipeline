#!/usr/bin/env python3
"""
Unified Queue Manager

Manages posting queue for both templates and notebooks.
Ensures proper mix of content types and prevents same-day duplicates across pages.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class QueuedContent:
    """Represents content in the publishing queue"""
    content_id: str  # Unique identifier
    content_type: str  # 'template' or 'notebook'
    page_id: str  # Target Facebook page ID
    page_name: str  # Human-readable page name
    platform: str  # 'facebook', 'threads', 'instagram'

    # Content details
    content_text: str
    hashtags: List[str]
    link: str
    image_path: Optional[str]
    alt_text: Optional[str]

    # Metadata
    source_name: str  # Template name or notebook basename
    category: str

    # Scheduling
    scheduled_time: str  # ISO format
    priority: int = 5
    created_at: str = ""

    # Duplicate tracking
    is_duplicate: bool = False  # True if goes to multiple pages
    duplicate_group_id: Optional[str] = None  # Links related duplicates

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'QueuedContent':
        return cls(**data)


class UnifiedQueueManager:
    """Manages unified queue for templates and notebooks"""

    def __init__(self, queue_file: str = None):
        """
        Initialize queue manager

        Args:
            queue_file: Path to queue file (default: data/unified_queue.json)
        """
        self.base_dir = Path("/home/user/computational-pipeline/social-media-automation")

        if queue_file:
            self.queue_file = Path(queue_file)
        else:
            self.queue_file = self.base_dir / "data" / "unified_queue.json"

        # Load existing queue
        self.queue: List[QueuedContent] = self._load_queue()

        # Track what's been posted
        self.posting_history_file = self.base_dir / "data" / "unified_posting_history.json"
        self.posting_history = self._load_posting_history()

        logger.info(f"Unified Queue Manager initialized with {len(self.queue)} items")

    def add_content(self, content: QueuedContent):
        """
        Add single content to queue

        Args:
            content: QueuedContent object
        """
        self.queue.append(content)
        self._sort_queue()
        self._save_queue()
        logger.info(f"Added {content.content_type} '{content.source_name}' to queue")

    def add_batch(self, contents: List[QueuedContent]):
        """
        Add multiple content items to queue

        Args:
            contents: List of QueuedContent objects
        """
        self.queue.extend(contents)
        self._sort_queue()
        self._save_queue()
        logger.info(f"Added {len(contents)} items to queue")

    def get_due_content(self, within_minutes: int = 5) -> List[QueuedContent]:
        """
        Get content due for posting

        Args:
            within_minutes: Look ahead window in minutes

        Returns:
            List of due content
        """
        now = datetime.now()
        cutoff = now + timedelta(minutes=within_minutes)

        due = []
        for content in self.queue:
            try:
                scheduled = datetime.fromisoformat(content.scheduled_time)
                if now <= scheduled <= cutoff:
                    due.append(content)
            except Exception as e:
                logger.error(f"Error parsing scheduled time: {e}")
                continue

        logger.info(f"Found {len(due)} content items due within {within_minutes} minutes")
        return due

    def remove_content(self, content_id: str) -> bool:
        """
        Remove content from queue by ID

        Args:
            content_id: Unique content identifier

        Returns:
            True if removed
        """
        original_len = len(self.queue)
        self.queue = [c for c in self.queue if c.content_id != content_id]

        if len(self.queue) < original_len:
            self._save_queue()
            logger.info(f"Removed content {content_id} from queue")
            return True

        logger.warning(f"Content {content_id} not found in queue")
        return False

    def mark_posted(self, content: QueuedContent, post_id: str):
        """
        Mark content as successfully posted

        Args:
            content: QueuedContent that was posted
            post_id: Social media platform post ID
        """
        # Remove from queue
        self.remove_content(content.content_id)

        # Add to history
        history_entry = {
            'content_id': content.content_id,
            'content_type': content.content_type,
            'source_name': content.source_name,
            'page_id': content.page_id,
            'page_name': content.page_name,
            'platform': content.platform,
            'post_id': post_id,
            'scheduled_time': content.scheduled_time,
            'posted_at': datetime.now().isoformat(),
            'is_duplicate': content.is_duplicate,
            'duplicate_group_id': content.duplicate_group_id
        }

        self.posting_history.append(history_entry)
        self._save_posting_history()

        logger.info(f"Marked {content.content_type} '{content.source_name}' as posted")

    def reschedule_content(self, content_id: str, new_time: datetime):
        """
        Reschedule content to new time

        Args:
            content_id: Content to reschedule
            new_time: New scheduled time
        """
        for content in self.queue:
            if content.content_id == content_id:
                content.scheduled_time = new_time.isoformat()
                self._sort_queue()
                self._save_queue()
                logger.info(f"Rescheduled {content_id} to {new_time}")
                return True

        logger.warning(f"Content {content_id} not found for rescheduling")
        return False

    def get_content_by_date_range(self, start: datetime, end: datetime) -> List[QueuedContent]:
        """
        Get content scheduled within a date range

        Args:
            start: Start datetime
            end: End datetime

        Returns:
            List of content in range
        """
        in_range = []
        for content in self.queue:
            try:
                scheduled = datetime.fromisoformat(content.scheduled_time)
                if start <= scheduled <= end:
                    in_range.append(content)
            except:
                continue

        return in_range

    def get_content_by_page(self, page_id: str) -> List[QueuedContent]:
        """
        Get all content for a specific page

        Args:
            page_id: Facebook page ID

        Returns:
            List of content for that page
        """
        return [c for c in self.queue if c.page_id == page_id]

    def get_content_by_type(self, content_type: str) -> List[QueuedContent]:
        """
        Get all content of specific type

        Args:
            content_type: 'template' or 'notebook'

        Returns:
            List of content of that type
        """
        return [c for c in self.queue if c.content_type == content_type]

    def get_daily_schedule(self, date: datetime) -> Dict[str, List[QueuedContent]]:
        """
        Get posting schedule for a specific day, organized by page

        Args:
            date: Date to get schedule for

        Returns:
            Dict mapping page_id to list of content
        """
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        day_content = self.get_content_by_date_range(start, end)

        # Organize by page
        by_page = defaultdict(list)
        for content in day_content:
            by_page[content.page_id].append(content)

        return dict(by_page)

    def validate_no_same_day_duplicates(self) -> List[str]:
        """
        Validate that duplicate content is not scheduled on same day

        Returns:
            List of warnings about same-day duplicates
        """
        warnings = []

        # Group by duplicate_group_id
        duplicate_groups = defaultdict(list)
        for content in self.queue:
            if content.is_duplicate and content.duplicate_group_id:
                duplicate_groups[content.duplicate_group_id].append(content)

        # Check each group
        for group_id, group_contents in duplicate_groups.items():
            dates = []
            for content in group_contents:
                try:
                    scheduled = datetime.fromisoformat(content.scheduled_time)
                    date_str = scheduled.strftime('%Y-%m-%d')
                    dates.append((date_str, content))
                except:
                    continue

            # Check for duplicates on same day
            date_counts = defaultdict(list)
            for date_str, content in dates:
                date_counts[date_str].append(content)

            for date_str, contents_on_day in date_counts.items():
                if len(contents_on_day) > 1:
                    sources = [c.source_name for c in contents_on_day]
                    warnings.append(
                        f"WARNING: Duplicate content '{sources[0]}' scheduled "
                        f"multiple times on {date_str}"
                    )

        return warnings

    def get_statistics(self) -> Dict:
        """
        Get queue statistics

        Returns:
            Dictionary with various stats
        """
        stats = {
            'total_queued': len(self.queue),
            'by_content_type': defaultdict(int),
            'by_page': defaultdict(int),
            'by_platform': defaultdict(int),
            'duplicates': 0,
            'next_24h': 0,
            'next_7days': 0
        }

        now = datetime.now()
        day_cutoff = now + timedelta(days=1)
        week_cutoff = now + timedelta(days=7)

        for content in self.queue:
            stats['by_content_type'][content.content_type] += 1
            stats['by_page'][content.page_name] += 1
            stats['by_platform'][content.platform] += 1

            if content.is_duplicate:
                stats['duplicates'] += 1

            try:
                scheduled = datetime.fromisoformat(content.scheduled_time)
                if now <= scheduled <= day_cutoff:
                    stats['next_24h'] += 1
                if now <= scheduled <= week_cutoff:
                    stats['next_7days'] += 1
            except:
                continue

        # Convert defaultdicts to regular dicts
        stats['by_content_type'] = dict(stats['by_content_type'])
        stats['by_page'] = dict(stats['by_page'])
        stats['by_platform'] = dict(stats['by_platform'])

        return stats

    def _sort_queue(self):
        """Sort queue by scheduled time and priority"""
        self.queue.sort(key=lambda x: (x.scheduled_time, -x.priority))

    def _load_queue(self) -> List[QueuedContent]:
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    return [QueuedContent.from_dict(item) for item in data]
            except Exception as e:
                logger.error(f"Error loading queue: {e}")
                return []
        return []

    def _save_queue(self):
        """Save queue to file"""
        try:
            self.queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.queue_file, 'w') as f:
                data = [c.to_dict() for c in self.queue]
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving queue: {e}")

    def _load_posting_history(self) -> List[Dict]:
        """Load posting history"""
        if self.posting_history_file.exists():
            try:
                with open(self.posting_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return []
        return []

    def _save_posting_history(self):
        """Save posting history"""
        try:
            self.posting_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.posting_history_file, 'w') as f:
                json.dump(self.posting_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")


def main():
    """Test unified queue manager"""
    import logging
    logging.basicConfig(level=logging.INFO)

    manager = UnifiedQueueManager()

    # Display stats
    print("\n" + "="*60)
    print("Unified Queue Statistics")
    print("="*60)

    stats = manager.get_statistics()
    print(f"\nTotal queued: {stats['total_queued']}")
    print(f"Next 24 hours: {stats['next_24h']}")
    print(f"Next 7 days: {stats['next_7days']}")
    print(f"Duplicate content items: {stats['duplicates']}")

    print("\nBy content type:")
    for content_type, count in stats['by_content_type'].items():
        print(f"  {content_type}: {count}")

    print("\nBy page:")
    for page, count in stats['by_page'].items():
        print(f"  {page}: {count}")

    print("\nBy platform:")
    for platform, count in stats['by_platform'].items():
        print(f"  {platform}: {count}")

    # Validate
    warnings = manager.validate_no_same_day_duplicates()
    if warnings:
        print("\n" + "="*60)
        print("Validation Warnings")
        print("="*60)
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("\nNo validation issues found!")


if __name__ == "__main__":
    main()
