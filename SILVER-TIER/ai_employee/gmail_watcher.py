"""gmail_watcher.py — Monitors Gmail for important unread emails"""

import os
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from base_watcher import BaseWatcher

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailWatcher(BaseWatcher):
    def __init__(
        self,
        vault_path: str = None,
        credentials_path: str = "credentials/credentials.json",
    ):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        self.credentials_path = credentials_path
        self.token_path = os.getenv("GMAIL_TOKEN_PATH", "credentials/token.json")
        self.processed_ids: set[str] = set()
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if Path(self.token_path).exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
            Path(self.token_path).parent.mkdir(exist_ok=True)
            Path(self.token_path).write_text(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def check_for_updates(self) -> list:
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q="is:unread is:important")
            .execute()
        )
        messages = results.get("messages", [])
        return [m for m in messages if m["id"] not in self.processed_ids]

    def create_action_file(self, message: dict) -> Path:
        msg = (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"],
            )
            .execute()
        )

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        subject = headers.get("Subject", "No Subject")
        sender = headers.get("From", "Unknown")
        snippet = msg.get("snippet", "")

        # Determine priority from snippet keywords
        priority_keywords = ["urgent", "asap", "invoice", "payment", "important"]
        priority = (
            "high"
            if any(kw in snippet.lower() for kw in priority_keywords)
            else "normal"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_{timestamp}_{message['id'][:8]}.md"
        filepath = self.needs_action / filename
        now_fmt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        now_iso = datetime.now().isoformat()
        priority_label = "HIGH" if priority == "high" else "NORMAL"

        content = f"""---
type: email
message_id: "{message['id']}"
from: "{sender}"
subject: "{subject}"
received: {now_iso}
priority: {priority}
status: pending
dry_run: {self.dry_run}
---

# Email: {subject}

**From:** {sender}
**Received:** {now_fmt}
**Priority:** {priority_label}

## Preview
{snippet}

## Suggested Actions
- [ ] Review full email content
- [ ] Draft a reply (requires human approval to send)
- [ ] Flag or archive
- [ ] Update Dashboard.md

## Claude Code Instructions
Based on Company_Handbook.md rules:
1. If priority is HIGH -> Create a Plan.md with draft reply
2. Always update Dashboard.md with this email
3. NEVER send email without moving approval file to /Approved/
"""
        filepath.write_text(content, encoding="utf-8")
        self.processed_ids.add(message["id"])
        return filepath


if __name__ == "__main__":
    watcher = GmailWatcher()
    watcher.run()
