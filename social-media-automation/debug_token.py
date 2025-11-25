#!/usr/bin/env python3
"""Debug Facebook token permissions"""

import os
import requests
from dotenv import load_dotenv

load_dotenv('/home/user/computational-pipeline/social-media-automation/.env')

token = os.getenv('FB_PAGE_TOKEN')

# Check token info
url = f"https://graph.facebook.com/v24.0/debug_token?input_token={token}&access_token={token}"
response = requests.get(url)
print("Token Debug Info:")
print(response.json())
print("\n" + "="*80 + "\n")

# Check pages
url = f"https://graph.facebook.com/v24.0/me/accounts?access_token={token}"
response = requests.get(url)
print("Pages accessible:")
print(response.json())
print("\n" + "="*80 + "\n")

# Check specific page permissions
page_id = "698630966948910"
url = f"https://graph.facebook.com/v24.0/{page_id}?fields=id,name,access_token&access_token={token}"
response = requests.get(url)
print(f"CoCalc page info (ID: {page_id}):")
print(response.json())
