#!/usr/bin/env python3
"""
Main Automation Runner

Unified interface for running the social media automation system.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

from template_scanner import TemplateScanner
from content_generator import ContentGenerator
from media_extractor import MediaExtractor
from social_publisher import SocialMediaPublisher
from smart_scheduler import SmartScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scan_templates():
    """Scan and index all templates"""
    print("Scanning LaTeX templates...")
    scanner = TemplateScanner()
    templates = scanner.scan_all_templates()
    scanner.save_index()

    stats = scanner.get_statistics()
    print(f"\nScanned {stats['total_templates']} templates across {stats['total_categories']} categories")
    print(f"Templates with visualizations: {stats['templates_with_plots']}")
    return True


def generate_queue(days=7):
    """Generate posting queue"""
    print(f"Generating {days}-day posting queue...")
    scheduler = SmartScheduler()

    if days == 7:
        posts = scheduler.generate_weekly_schedule()
    else:
        # Generate custom duration
        posts = scheduler.generate_weekly_schedule()
        # Trim to requested days if needed

    scheduler.add_to_queue(posts)

    status = scheduler.get_queue_status()
    print(f"\nQueue generated:")
    print(f"  Total posts: {status['total_queued']}")
    print(f"  By platform: {status['by_platform']}")
    print(f"  Next 24 hours: {status['next_24_hours']}")

    return True


def show_queue():
    """Display current queue status"""
    scheduler = SmartScheduler()
    status = scheduler.get_queue_status()

    print("="*60)
    print("Current Queue Status")
    print("="*60)
    print(f"Total queued posts: {status['total_queued']}")
    print(f"Posts in next 24 hours: {status['next_24_hours']}")

    print("\nBy platform:")
    for platform, count in status['by_platform'].items():
        print(f"  {platform}: {count} posts")

    if status['next_post']:
        print(f"\nNext scheduled post:")
        print(f"  Template: {status['next_post']['template']}")
        print(f"  Platform: {status['next_post']['platform']}")
        print(f"  Time: {status['next_post']['scheduled']}")

    return True


def publish_now(platform=None):
    """Publish due posts immediately"""
    scheduler = SmartScheduler()

    print("Checking for due posts...")
    due_posts = scheduler.get_posts_due(within_minutes=60)

    if platform:
        due_posts = [p for p in due_posts if p.platform == platform]

    if not due_posts:
        print("No posts due for publishing")
        return True

    print(f"Found {len(due_posts)} posts due for publishing")

    for post in due_posts:
        print(f"\nPublishing {post.platform} post: {post.template.template_name}")
        success = scheduler.publish_post(post)

        if success:
            print("  ✓ Published successfully")
        else:
            print("  ✗ Publishing failed")

    return True


def test_post(template_name=None):
    """Generate and display test post without publishing"""
    scanner = TemplateScanner()

    if not scanner.load_index():
        print("Building template index...")
        scanner.scan_all_templates()
        scanner.save_index()

    # Get template
    if template_name:
        # Find specific template
        template = None
        for templates in scanner.templates.values():
            for t in templates:
                if t.template_name == template_name:
                    template = t
                    break
            if template:
                break

        if not template:
            print(f"Template '{template_name}' not found")
            return False
    else:
        # Random template
        template = scanner.get_random_template()

    if not template:
        print("No templates available")
        return False

    # Generate content
    generator = ContentGenerator()

    print("="*60)
    print(f"Template: {template.template_name}")
    print(f"Category: {template.category}")
    print(f"Title: {template.title}")
    print("="*60)

    for platform in ['facebook', 'threads', 'instagram']:
        print(f"\n{'='*60}")
        print(f"{platform.upper()} POST")
        print("="*60)

        if platform == 'facebook':
            post = generator.generate_facebook_post(template)
        elif platform == 'threads':
            post = generator.generate_threads_post(template)
        else:
            post = generator.generate_instagram_post(template)

        print(post.content)
        print(f"\nCharacters: {post.char_count}")
        print(f"Link: {post.link}")
        print(f"Hashtags: {' '.join(post.hashtags[:5])}...")

    return True


def validate_setup():
    """Validate system setup and credentials"""
    print("Validating Social Media Automation Setup")
    print("="*60)

    all_valid = True

    # Check directories
    print("\n1. Checking directories...")
    required_dirs = ['data', 'media', 'config', 'logs']
    for dir_name in required_dirs:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            all_valid = False

    # Check template directory
    print("\n2. Checking template directory...")
    templates_dir = Path("/home/user/latex-templates/templates")
    if templates_dir.exists():
        tex_files = list(templates_dir.glob("**/*.tex"))
        print(f"  ✓ Templates directory exists ({len(tex_files)} .tex files)")
    else:
        print(f"  ✗ Templates directory not found")
        all_valid = False

    # Check credentials
    print("\n3. Validating credentials...")
    try:
        publisher = SocialMediaPublisher()
        validation = publisher.validate_credentials()

        for platform, valid in validation.items():
            status = "✓ Valid" if valid else "✗ Invalid"
            print(f"  {platform}: {status}")
            if not valid:
                all_valid = False
    except Exception as e:
        print(f"  ✗ Error validating credentials: {e}")
        all_valid = False

    # Check template index
    print("\n4. Checking template index...")
    index_file = Path(__file__).parent / "data" / "template_index.json"
    if index_file.exists():
        scanner = TemplateScanner()
        if scanner.load_index():
            stats = scanner.get_statistics()
            print(f"  ✓ Index loaded ({stats['total_templates']} templates)")
        else:
            print(f"  ⚠ Index exists but couldn't load")
    else:
        print(f"  ⚠ No index found (run: python run_automation.py scan)")

    print("\n" + "="*60)
    if all_valid:
        print("✓ Setup validation passed!")
    else:
        print("✗ Setup validation failed. Please fix issues above.")

    return all_valid


def run_scheduler():
    """Run continuous scheduler"""
    print("Starting scheduler...")
    print("Press Ctrl+C to stop")

    scheduler = SmartScheduler()
    scheduler.run_scheduler_loop()


def main():
    parser = argparse.ArgumentParser(
        description='LaTeX Template Social Media Automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  scan          Scan and index all LaTeX templates
  queue         Generate weekly posting queue
  show          Show current queue status
  publish       Publish posts that are due now
  test          Generate test post without publishing
  validate      Validate setup and credentials
  scheduler     Run continuous scheduler

Examples:
  python run_automation.py scan
  python run_automation.py queue
  python run_automation.py publish --platform facebook
  python run_automation.py test --template sound_propagation
  python run_automation.py scheduler
        """
    )

    parser.add_argument('command', choices=[
        'scan', 'queue', 'show', 'publish', 'test', 'validate', 'scheduler'
    ], help='Command to run')

    parser.add_argument('--platform', choices=['facebook', 'threads', 'instagram'],
                       help='Target platform for publish command')

    parser.add_argument('--template', type=str,
                       help='Template name for test command')

    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for queue generation')

    args = parser.parse_args()

    # Execute command
    try:
        if args.command == 'scan':
            success = scan_templates()
        elif args.command == 'queue':
            success = generate_queue(args.days)
        elif args.command == 'show':
            success = show_queue()
        elif args.command == 'publish':
            success = publish_now(args.platform)
        elif args.command == 'test':
            success = test_post(args.template)
        elif args.command == 'validate':
            success = validate_setup()
        elif args.command == 'scheduler':
            run_scheduler()
            success = True
        else:
            parser.print_help()
            success = False

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running command: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
