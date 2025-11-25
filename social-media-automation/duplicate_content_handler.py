#!/usr/bin/env python3
"""
Duplicate Content Handler

Handles content that goes to multiple pages (CoCalc + SageMath).
Ensures duplicates are spread across different days with tailored messaging.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

from page_router import PageRoute

logger = logging.getLogger(__name__)


@dataclass
class DuplicateSchedule:
    """Represents scheduling for duplicate content"""
    original_time: datetime
    schedules: List[Dict]  # List of {page_id, page_name, scheduled_time}
    duplicate_group_id: str
    min_day_gap: int = 2


class DuplicateContentHandler:
    """Handles scheduling and messaging for duplicate content"""

    def __init__(self, min_day_gap: int = 2):
        """
        Initialize duplicate content handler

        Args:
            min_day_gap: Minimum days between duplicate posts (default: 2)
        """
        self.min_day_gap = min_day_gap
        logger.info(f"Duplicate Content Handler initialized (min gap: {min_day_gap} days)")

    def schedule_duplicate_content(self,
                                   routes: List[PageRoute],
                                   base_time: datetime) -> DuplicateSchedule:
        """
        Create schedule for content going to multiple pages

        Args:
            routes: List of page routes for this content
            base_time: Original scheduled time

        Returns:
            DuplicateSchedule with staggered times
        """
        if len(routes) <= 1:
            # Not a duplicate, use base time
            return DuplicateSchedule(
                original_time=base_time,
                schedules=[{
                    'page_id': routes[0].page_id,
                    'page_name': routes[0].page_name,
                    'scheduled_time': base_time
                }] if routes else [],
                duplicate_group_id=str(uuid.uuid4()),
                min_day_gap=0
            )

        # Sort routes by priority (higher first)
        sorted_routes = sorted(routes, key=lambda r: r.priority, reverse=True)

        # Create staggered schedule
        schedules = []
        current_time = base_time

        for i, route in enumerate(sorted_routes):
            schedules.append({
                'page_id': route.page_id,
                'page_name': route.page_name,
                'scheduled_time': current_time,
                'is_original': (i == 0)
            })

            # Increment time for next page
            if i < len(sorted_routes) - 1:
                current_time = current_time + timedelta(days=self.min_day_gap)

        duplicate_group_id = str(uuid.uuid4())

        logger.info(
            f"Created duplicate schedule: {len(schedules)} pages over "
            f"{(schedules[-1]['scheduled_time'] - schedules[0]['scheduled_time']).days} days"
        )

        return DuplicateSchedule(
            original_time=base_time,
            schedules=schedules,
            duplicate_group_id=duplicate_group_id,
            min_day_gap=self.min_day_gap
        )

    def tailor_message_for_page(self,
                               base_content: str,
                               page_id: str,
                               page_name: str,
                               content_type: str) -> str:
        """
        Tailor message for specific page audience

        Args:
            base_content: Original content text
            page_id: Target page ID
            page_name: Target page name
            content_type: 'template' or 'notebook'

        Returns:
            Tailored content
        """
        # Add page-specific introduction or framing
        if 'SageMath' in page_name:
            # SageMath audience - emphasize mathematical/symbolic aspects
            prefix = self._get_sagemath_prefix(content_type)
            tailored = f"{prefix}\n\n{base_content}"
        else:
            # CoCalc audience - broader computational science focus
            prefix = self._get_cocalc_prefix(content_type)
            tailored = f"{prefix}\n\n{base_content}"

        logger.debug(f"Tailored message for {page_name}")
        return tailored

    def _get_sagemath_prefix(self, content_type: str) -> str:
        """Get page-specific prefix for SageMath page"""
        prefixes = {
            'template': [
                "Mathematical computation at its finest!",
                "Symbolic mathematics made easy with SageMath.",
                "Explore pure mathematics with computational power.",
                "Advanced mathematical templates for serious researchers."
            ],
            'notebook': [
                "Mathematical exploration with SageMath!",
                "Dive into computational mathematics.",
                "Symbolic computation in action.",
                "Mathematical insights powered by SageMath."
            ]
        }

        import random
        return random.choice(prefixes.get(content_type, prefixes['template']))

    def _get_cocalc_prefix(self, content_type: str) -> str:
        """Get page-specific prefix for CoCalc page"""
        prefixes = {
            'template': [
                "New computational template available!",
                "Reproducible research made easy.",
                "Professional LaTeX templates for scientists.",
                "Computational science templates on CoCalc."
            ],
            'notebook': [
                "Computational notebook showcase!",
                "Interactive research in the cloud.",
                "Explore this computational workflow.",
                "Reproducible science with CoCalc notebooks."
            ]
        }

        import random
        return random.choice(prefixes.get(content_type, prefixes['template']))

    def adjust_hashtags_for_page(self,
                                base_hashtags: List[str],
                                page_name: str) -> List[str]:
        """
        Adjust hashtags for specific page audience

        Args:
            base_hashtags: Original hashtags
            page_name: Target page name

        Returns:
            Adjusted hashtags
        """
        hashtags = base_hashtags.copy()

        if 'SageMath' in page_name:
            # Add SageMath-specific tags
            sagemath_tags = ['SageMath', 'SymbolicMath', 'PureMath', 'MathematicalComputing']
            for tag in sagemath_tags:
                if tag not in hashtags:
                    hashtags.insert(0, tag)  # Add at beginning

            # Remove non-mathematical tags if present
            remove_tags = ['Engineering', 'Physics', 'DataScience']
            hashtags = [tag for tag in hashtags if tag not in remove_tags]

        else:
            # CoCalc page - keep broader tags
            cocalc_tags = ['CoCalc', 'ComputationalScience', 'ReproducibleResearch']
            for tag in cocalc_tags:
                if tag not in hashtags:
                    hashtags.insert(0, tag)

        # Limit to reasonable number
        return hashtags[:10]

    def create_variation_text(self,
                            base_content: str,
                            variation_number: int) -> str:
        """
        Create slight variation of content text to avoid exact duplicates

        Args:
            base_content: Original content
            variation_number: Which variation (0, 1, 2, etc.)

        Returns:
            Varied content
        """
        if variation_number == 0:
            return base_content

        # Add minor variations
        variations = [
            f"Check this out: {base_content}",
            f"Don't miss: {base_content}",
            f"Worth exploring: {base_content}",
            f"Take a look: {base_content}"
        ]

        if variation_number <= len(variations):
            return variations[variation_number - 1]

        return base_content

    def should_spread_duplicates(self, routes: List[PageRoute]) -> bool:
        """
        Determine if content should be spread across days

        Args:
            routes: List of page routes

        Returns:
            True if should spread
        """
        return len(routes) > 1

    def get_optimal_spread_pattern(self,
                                  num_pages: int,
                                  start_date: datetime) -> List[datetime]:
        """
        Get optimal spread pattern for multiple pages

        Args:
            num_pages: Number of pages to post to
            start_date: Starting date

        Returns:
            List of optimal posting times
        """
        times = [start_date]

        for i in range(1, num_pages):
            # Spread evenly with minimum gap
            next_time = start_date + timedelta(days=i * self.min_day_gap)
            times.append(next_time)

        logger.debug(f"Optimal spread: {num_pages} pages over {times[-1] - times[0]}")
        return times


def main():
    """Test duplicate content handler"""
    import logging
    from page_router import PageRoute

    logging.basicConfig(level=logging.INFO)

    handler = DuplicateContentHandler(min_day_gap=2)

    # Test scheduling
    print("\n" + "="*60)
    print("Testing Duplicate Scheduling")
    print("="*60)

    routes = [
        PageRoute(
            page_id='698630966948910',
            page_name='CoCalc',
            reason='All content',
            priority=10
        ),
        PageRoute(
            page_id='26593144945',
            page_name='SageMath',
            reason='Math content',
            priority=8
        )
    ]

    base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    schedule = handler.schedule_duplicate_content(routes, base_time)

    print(f"\nOriginal time: {schedule.original_time}")
    print(f"Duplicate group ID: {schedule.duplicate_group_id}")
    print(f"\nSchedule:")

    for sched in schedule.schedules:
        print(f"  {sched['page_name']}:")
        print(f"    Time: {sched['scheduled_time']}")
        print(f"    Original: {sched.get('is_original', False)}")

    # Test message tailoring
    print("\n" + "="*60)
    print("Testing Message Tailoring")
    print("="*60)

    base_content = "Explore symbolic algebra with this comprehensive template."

    for route in routes:
        tailored = handler.tailor_message_for_page(
            base_content,
            route.page_id,
            route.page_name,
            'template'
        )
        print(f"\n{route.page_name}:")
        print(f"  {tailored[:100]}...")

    # Test hashtag adjustment
    print("\n" + "="*60)
    print("Testing Hashtag Adjustment")
    print("="*60)

    base_hashtags = ['LaTeX', 'SageTeX', 'Mathematics', 'ComputationalScience']

    for route in routes:
        adjusted = handler.adjust_hashtags_for_page(base_hashtags, route.page_name)
        print(f"\n{route.page_name}:")
        print(f"  {', '.join(adjusted)}")


if __name__ == "__main__":
    main()
