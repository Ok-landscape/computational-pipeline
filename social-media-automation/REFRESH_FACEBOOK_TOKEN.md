# Facebook Access Token Refresh Guide

## Quick Reference

**App ID:** 1616656702631697
**App Secret:** 997ec886ebf260ab617ec94be7e090e7

---

## Method 1: Using Graph API Explorer (Recommended - Easiest)

### Step 1: Get Short-Lived User Token

1. Go to: https://developers.facebook.com/tools/explorer/
2. **Select App:** Click "Meta App" dropdown → Select your app (ID: 1616656702631697)
3. **Add Permissions:**
   - Click "Permissions" tab or "Add a Permission"
   - Add: `pages_show_list`
   - Add: `pages_read_engagement`
   - Add: `pages_manage_posts`
4. **Generate Token:** Click "Generate Access Token" button
5. **Copy the token** that appears (starts with `EAAW...`)

### Step 2: Exchange for Long-Lived User Token (60 days)

Paste this in your terminal (replace `SHORT_LIVED_TOKEN` with the token from Step 1):

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=1616656702631697&client_secret=997ec886ebf260ab617ec94be7e090e7&fb_exchange_token=SHORT_LIVED_TOKEN"
```

**Example output:**
```json
{"access_token":"EAAWZBVz...(long token)...","token_type":"bearer","expires_in":5183944}
```

Copy the new `access_token` value.

### Step 3: Get Page Access Tokens (Never Expires!)

Paste this in your terminal (replace `LONG_LIVED_USER_TOKEN` with token from Step 2):

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token=LONG_LIVED_USER_TOKEN"
```

**Example output:**
```json
{
  "data": [
    {
      "access_token": "EAAWZBVzh77x...(page token)...",
      "category": "Software",
      "id": "698630966948910",
      "name": "CoCalc"
    },
    {
      "access_token": "EAAWZBVzh77x...(different page token)...",
      "category": "Software",
      "id": "26593144945",
      "name": "Sage Mathematical Software System"
    }
  ]
}
```

### Step 4: Update .env File

Copy the Page Access Tokens and update your `.env` file:

```bash
# Edit the .env file
nano /home/user/computational-pipeline/social-media-automation/.env

# Update these lines with the NEW tokens:
FB_PAGE_ACCESS_TOKEN=(CoCalc page token from Step 3)
FB_PAGE_TOKEN=(same as above)
```

### Step 5: Test the New Token

```bash
python /home/user/computational-pipeline/social-media-automation/test_facebook_token.py
```

You should see: "✓ Token is VALID"

---

## Method 2: Using Access Token Debugger (Verification)

After getting your tokens, verify them:

1. Go to: https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your Page Access Token
3. Check:
   - ✓ "Expires:" should say "Never" (for Page tokens)
   - ✓ "Scopes:" should include `pages_manage_posts`
   - ✓ "User ID:" should match the page owner

---

## Important Notes

### Page Access Tokens vs User Access Tokens

- **User Access Token:** Expires in 60 days (even long-lived ones)
- **Page Access Token:** Never expires (as long as the user token used to generate it is valid)

**Always use Page Access Tokens for posting!**

### Token Expiration

- Short-lived tokens: ~1-2 hours
- Long-lived user tokens: 60 days
- Page access tokens: Never (but need to be regenerated if user token used to create them expires)

### Security

- Never commit tokens to git
- Keep `.env` file secret
- Regenerate immediately if exposed

---

## Troubleshooting

### "Error validating access token"
→ Token expired. Follow steps above to generate new one.

### "Invalid OAuth access token"
→ Wrong token type or malformed. Regenerate.

### "The user hasn't authorized the application to perform this action"
→ Missing permissions. Ensure you added all three permissions in Step 1.

### "Unsupported post request"
→ Using User token instead of Page token. Complete Step 3.

---

## Quick Test After Token Update

```bash
# Test token validity
python test_facebook_token.py

# Try a real post
python test_single_post.py
```

---

## When to Refresh

**Automatic signs:**
- 400 error when posting
- "Session has expired" message
- Token debugger shows "INVALID"

**Preventive:**
- Refresh every 50 days (before 60-day expiration)
- Set a calendar reminder

---

## Alternative: Meta Business Suite

You can also post manually through Meta Business Suite to test:
- Visit: https://business.facebook.com/
- Navigate to your CoCalc or SageMath page
- Click "Create post"
- Test posting manually to verify page access

This doesn't solve the API issue but confirms your account permissions are correct.
