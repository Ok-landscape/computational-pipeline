#!/usr/bin/env python3
"""
Delete a Facebook/Instagram post by ID

Usage: python delete_post.py <post_id>
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv('/home/user/computational-pipeline/social-media-automation/.env')

def delete_facebook_post(post_id: str, access_token: str) -> bool:
    """
    Delete a Facebook post

    Args:
        post_id: The Facebook post ID
        access_token: Facebook page access token

    Returns:
        True if deleted successfully, False otherwise
    """
    url = f"https://graph.facebook.com/v24.0/{post_id}"
    params = {'access_token': access_token}

    try:
        response = requests.delete(url, params=params, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✓ Successfully deleted post {post_id}")
                return True
            else:
                print(f"✗ Delete returned success=false for post {post_id}")
                print(f"Response: {result}")
                return False
        else:
            print(f"✗ Failed to delete post {post_id}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Error deleting post: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python delete_post.py <post_id>")
        print("\nExample:")
        print("  python delete_post.py 1165281759114193")
        sys.exit(1)

    post_id = sys.argv[1]
    access_token = os.getenv('FB_PAGE_TOKEN')

    if not access_token:
        print("✗ FB_PAGE_TOKEN not found in environment")
        sys.exit(1)

    print(f"Attempting to delete post: {post_id}")
    print("-" * 80)

    success = delete_facebook_post(post_id, access_token)

    if success:
        print("\n" + "=" * 80)
        print("POST DELETED SUCCESSFULLY")
        print("=" * 80)
        print("\nReason for deletion: Image contained empty subplots")
        print("Action required: Fix notebook and re-execute before posting again")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("DELETION FAILED")
        print("=" * 80)
        print("\nYou may need to delete manually via Facebook")
        sys.exit(1)


if __name__ == "__main__":
    main()
