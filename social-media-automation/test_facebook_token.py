#!/usr/bin/env python3
"""
Test Facebook Access Token Validity and Permissions
"""

import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv('/home/user/computational-pipeline/social-media-automation/.env')

def test_token():
    """Test Facebook access token"""

    print("=" * 80)
    print("FACEBOOK ACCESS TOKEN DIAGNOSTIC")
    print("=" * 80)
    print()

    # Get credentials
    access_token = os.getenv('FB_PAGE_TOKEN') or os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id_cocalc = os.getenv('FB_PAGE_ID_COCALC')
    page_id_sagemath = os.getenv('FB_PAGE_ID_SAGEMATH')

    if not access_token:
        print("✗ No access token found in .env file")
        return False

    print(f"✓ Access token found: {access_token[:20]}...{access_token[-10:]}")
    print(f"✓ CoCalc Page ID: {page_id_cocalc}")
    print(f"✓ SageMath Page ID: {page_id_sagemath}")
    print()

    # Test 1: Check token validity
    print("[Test 1] Checking token validity...")
    debug_url = "https://graph.facebook.com/v21.0/debug_token"
    params = {
        'input_token': access_token,
        'access_token': access_token
    }

    try:
        response = requests.get(debug_url, params=params, timeout=10)
        data = response.json()

        if 'data' in data:
            token_data = data['data']
            is_valid = token_data.get('is_valid', False)

            if is_valid:
                print("  ✓ Token is VALID")
                print(f"    App ID: {token_data.get('app_id')}")
                print(f"    Type: {token_data.get('type')}")
                print(f"    Expires: {token_data.get('expires_at', 'Never' if token_data.get('expires_at') == 0 else 'Unknown')}")

                # Show permissions
                if 'scopes' in token_data:
                    print(f"    Permissions: {', '.join(token_data['scopes'])}")
            else:
                print("  ✗ Token is INVALID")
                print(f"    Error: {token_data.get('error', {}).get('message', 'Unknown')}")
                return False
        else:
            print(f"  ✗ Could not validate token: {data}")
            return False

    except Exception as e:
        print(f"  ✗ Error checking token: {e}")
        return False

    print()

    # Test 2: Check access to CoCalc page
    print("[Test 2] Checking access to CoCalc page...")
    page_url = f"https://graph.facebook.com/v21.0/{page_id_cocalc}"
    params = {
        'fields': 'id,name,access_token',
        'access_token': access_token
    }

    try:
        response = requests.get(page_url, params=params, timeout=10)
        data = response.json()

        if 'id' in data:
            print(f"  ✓ Can access page")
            print(f"    Page Name: {data.get('name')}")
            print(f"    Page ID: {data.get('id')}")
        elif 'error' in data:
            print(f"  ✗ Cannot access page")
            print(f"    Error: {data['error'].get('message')}")
            print(f"    Code: {data['error'].get('code')}")
            print(f"    Type: {data['error'].get('type')}")
            return False
        else:
            print(f"  ✗ Unexpected response: {data}")
            return False

    except Exception as e:
        print(f"  ✗ Error accessing page: {e}")
        return False

    print()

    # Test 3: Try to post (dry run - we won't actually post)
    print("[Test 3] Checking posting permissions...")
    feed_url = f"https://graph.facebook.com/v21.0/{page_id_cocalc}/feed"

    # We'll just check what would happen without actually posting
    print(f"  API Endpoint: {feed_url}")
    print(f"  Note: To actually test posting, use test_single_post.py")
    print()

    # Test 4: Check what permissions are needed
    print("[Test 4] Required permissions for posting:")
    print("  ✓ pages_read_engagement (read page data)")
    print("  ✓ pages_manage_posts (create, edit, delete posts)")
    print("  ✓ pages_show_list (access page list)")
    print()

    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)
    print()
    print("If all tests passed, your token is valid and has access.")
    print("If posting still fails, check:")
    print("  1. Token has 'pages_manage_posts' permission")
    print("  2. Token is a Page Access Token, not a User Access Token")
    print("  3. API version compatibility (currently using v21.0)")
    print()

    return True


if __name__ == '__main__':
    test_token()
