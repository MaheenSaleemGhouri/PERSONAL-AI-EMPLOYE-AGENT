# Gmail Watcher Setup Guide

Your `credentials.json` file is **currently empty**. Follow these steps to fill it in.

---

## Step 1 — Create a Google Cloud Project

1. Go to **https://console.cloud.google.com**
2. Click the project dropdown (top left) → **New Project**
3. Name it something like `AI-Employee` → **Create**

---

## Step 2 — Enable the Gmail API

1. In your project, go to **APIs & Services → Library**
2. Search for **"Gmail API"**
3. Click it → **Enable**

---

## Step 3 — Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. If prompted, configure the **OAuth consent screen** first:
   - User type: **External**
   - App name: `AI Employee`
   - Add your Gmail address as a test user
   - Save and continue through all steps
4. Back on Create Credentials:
   - Application type: **Desktop app**
   - Name: `AI Employee Desktop`
   - Click **Create**
5. A dialog shows your credentials — click **Download JSON**

---

## Step 4 — Place the credentials.json file

Copy the downloaded JSON file to this project root, replacing the empty `credentials.json`:

```
C:\Hackathon 0\Silver tier\credentials.json
```

The file should look like this (your values will differ):

```json
{
  "installed": {
    "client_id": "123456789-abc.apps.googleusercontent.com",
    "project_id": "ai-employee-xxxxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-xxxxxxxxxxxxxxxxxxxxxxx",
    "redirect_uris": ["http://localhost"]
  }
}
```

---

## Step 5 — First-time authentication

Run the Gmail watcher once. It will open your browser:

```bash
python watchers/gmail_watcher.py --vault AI_Employee_Vault
```

1. Browser opens → sign in with your Google account
2. Grant the "Read Gmail messages" permission
3. Browser closes → `token.json` is saved automatically
4. The watcher starts polling

**After the first run**, the token is saved and the watcher runs silently without opening a browser again (auto-refresh).

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `credentials.json is empty` | Follow Step 4 above |
| `credentials.json is not valid JSON` | Re-download from Google Cloud Console |
| `Error 403: access_denied` | Add your Gmail as a test user in OAuth consent screen |
| `Token refresh failed` | Delete `token.json` and re-run — it will re-authenticate |
| `Gmail API not enabled` | Go to APIs & Services → Library → Enable Gmail API |

---

## Add to .gitignore

Add these lines to your `.gitignore` to avoid committing credentials:

```
credentials.json
token.json
.env
linkedin_profile/
whatsapp_profile/
```
