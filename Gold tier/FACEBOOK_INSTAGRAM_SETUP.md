# Facebook & Instagram Integration Setup Guide

Complete guide to connect your Facebook Page and Instagram Business account to the AI Employee.

---

## Prerequisites

- A **Facebook Page** (not a personal profile)
- A **Meta Developer Account** — https://developers.facebook.com/
- (Optional) An **Instagram Business** or **Creator** account linked to your Facebook Page

---

## Step 1: Create a Meta App

1. Go to https://developers.facebook.com/apps/
2. Click **"Create App"**
3. Select **"Business"** as the app type
4. Fill in:
   - App name: `AI Employee Bot` (or any name)
   - Contact email: your email
5. Click **"Create App"**

---

## Step 2: Add Facebook Products

1. In your app dashboard, click **"Add Product"**
2. Add **"Facebook Login for Business"**
3. Add **"Pages API"** (under Messenger/Pages)

---

## Step 3: Generate Page Access Token

### Quick Method (Graph API Explorer)

1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app from the dropdown
3. Click **"Generate Access Token"**
4. Grant these permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `pages_messaging`
   - `pages_read_user_content`
   - `instagram_basic` (if using Instagram)
   - `instagram_manage_comments` (if using Instagram)
5. Copy the **User Access Token**

### Convert to Long-Lived Token (60 days)

The short-lived token expires in 1 hour. Convert it:

```bash
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

This returns a token valid for ~60 days.

### Get Page Access Token (never expires)

```bash
curl -s "https://graph.facebook.com/v21.0/me/accounts?\
access_token=YOUR_LONG_LIVED_USER_TOKEN"
```

Find your page in the response and copy its `access_token` — this is a **permanent Page Access Token**.

---

## Step 4: Get Your Page ID

From the same `/me/accounts` response above, copy the `id` field for your page.

Or find it on your Facebook Page → About → Page transparency → Page ID.

---

## Step 5: (Optional) Get Instagram Business Account ID

If your Instagram is linked to your Facebook Page:

```bash
curl -s "https://graph.facebook.com/v21.0/YOUR_PAGE_ID?\
fields=instagram_business_account&\
access_token=YOUR_PAGE_ACCESS_TOKEN"
```

Copy the `instagram_business_account.id` value.

---

## Step 6: Configure .env

Add to your `Gold tier/.env`:

```env
# Facebook Page
FACEBOOK_PAGE_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxx
FACEBOOK_PAGE_ID=123456789012345

# Instagram (optional — leave blank to disable)
INSTAGRAM_BUSINESS_ID=17841400123456789
```

---

## Step 7: Test the Connection

```bash
cd "Gold tier"
python watchers/facebook_watcher.py --setup
```

Expected output:
```
Testing Facebook Graph API connection...
OK — Connected to page. Found 1 recent post(s).
OK — Instagram connected. Found 3 recent media.

Setup complete! Run without --setup to start watching.
```

---

## Step 8: Start Monitoring

### Standalone
```bash
python watchers/facebook_watcher.py --vault AI_Employee_Vault --interval 120
```

### Via Orchestrator (recommended)
```bash
python watchers/orchestrator.py --vault AI_Employee_Vault
```

The orchestrator starts all 6 watchers including Facebook.

---

## Available Claude Skills

| Skill | What it does |
|-------|-------------|
| `/draft-facebook-post` | Draft a Facebook Page post for approval |
| `/publish-facebook-post <file>` | Publish an approved post via Graph API |
| `/process-facebook` | Triage FB comments, messages, IG comments |
| `/social-media-summary` | Cross-platform engagement report |

---

## What Gets Monitored

| Platform | What | Priority |
|----------|------|----------|
| Facebook | Page post comments | Medium |
| Facebook | Messenger messages | High |
| Instagram | Post comments | Medium |

All detected items land in `AI_Employee_Vault/Needs_Action/` as markdown files with `FB_` prefix.

---

## Graph API Permissions Reference

| Permission | Required For |
|-----------|-------------|
| `pages_show_list` | List pages you manage |
| `pages_read_engagement` | Read post likes, comments, shares |
| `pages_manage_posts` | Publish posts to your page |
| `pages_messaging` | Read/send Messenger messages |
| `pages_read_user_content` | Read user comments on your posts |
| `instagram_basic` | Read Instagram profile + media |
| `instagram_manage_comments` | Read Instagram comments |

---

## Troubleshooting

### "Invalid OAuth access token"
- Token may be expired. Re-generate following Step 3.
- Ensure you're using a **Page** token, not a **User** token.

### "Requires pages_read_engagement permission"
- Go to App Review in your Meta App and request the missing permission.
- For testing (before app review), you can use the Graph API Explorer.

### Instagram returns empty
- Ensure your Instagram account is a **Business** or **Creator** account.
- Ensure it's **linked** to your Facebook Page (Instagram settings → Linked Accounts).
- Verify `INSTAGRAM_BUSINESS_ID` is the Graph API ID, not your Instagram username.

### "Application does not have permission for this action"
- Your app may need **App Review** for some permissions.
- During development, only admins/developers/testers of the app can use it.

### Rate Limits
- Facebook Graph API: 200 calls per user per hour.
- The watcher checks every 2 minutes (default) = ~30 calls/hour — well within limits.
- If you hit limits, increase `--interval` to 300 (5 minutes).

---

## Security Notes

- **Never commit** your Page Access Token to git.
- Tokens are stored only in `.env` (which is in `.gitignore`).
- The Page Access Token grants full posting access — treat it like a password.
- Rotate tokens periodically (generate a new one, update `.env`).
