"""
gmail_watcher.py — Gmail Watcher for AI Employee (Silver Tier)

Monitors Gmail for unread emails and creates structured .md action files
in /Needs_Action so Claude Code can process them with /process-gmail.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRST-TIME SETUP (do this once):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Go to https://console.cloud.google.com
2. Create a project (or select existing one)
3. Enable the Gmail API:
   APIs & Services → Library → search "Gmail API" → Enable
4. Create OAuth credentials:
   APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: Desktop app
   - Download JSON → save as credentials.json in this project root
5. First run opens your browser to sign in — token saved as token.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    # Run from the Silver tier project root
    python watchers/gmail_watcher.py
    python watchers/gmail_watcher.py --vault AI_Employee_Vault --interval 120
    python watchers/gmail_watcher.py --query "is:unread is:important"

Install dependencies:
    pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# ─── load .env if present ────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─── ensure base_watcher is importable ───────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# ─── Google API imports (optional — fail gracefully) ─────────────────────────
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_OK = True
except ImportError:
    GOOGLE_LIBS_OK = False

# ─── constants ────────────────────────────────────────────────────────────────
# Request only read access — never touches your sent mail or drafts
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Keywords that bump a message to priority: high
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "action required",
    "invoice", "payment", "overdue", "past due",
    "contract", "agreement", "deadline",
    "proposal", "quote", "estimate",
    "follow up", "follow-up",
    "meeting", "call me",
]


# ─────────────────────────────────────────────────────────────────────────────
class GmailWatcher(BaseWatcher):
    """
    Polls Gmail for unread emails and writes structured .md action files
    to AI_Employee_Vault/Needs_Action/.
    """

    def __init__(
        self,
        vault_path: str,
        credentials_path: str = "credentials.json",
        token_path: str = "token.json",
        check_interval: int = 120,
        query: str = "is:unread",
    ):
        super().__init__(vault_path, check_interval=check_interval)
        self.credentials_path = Path(credentials_path).resolve()
        self.token_path = Path(token_path).resolve()
        self.query = query
        self.service = None

        # Persist which message IDs we've already handled so we never
        # create duplicate action files after a restart.
        self._processed_ids: set[str] = self._load_processed_ids()

    # ──────────────────────────────────────────────────────────────────────────
    # Processed-IDs persistence
    # ──────────────────────────────────────────────────────────────────────────
    @property
    def _ids_file(self) -> Path:
        return self.vault_path / ".gmail_processed_ids.json"

    def _load_processed_ids(self) -> set[str]:
        if self._ids_file.exists():
            try:
                return set(json.loads(self._ids_file.read_text(encoding="utf-8")))
            except Exception:
                pass
        return set()

    def _save_processed_ids(self) -> None:
        self._ids_file.write_text(
            json.dumps(sorted(self._processed_ids), indent=2),
            encoding="utf-8",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # OAuth2 Authentication
    # ──────────────────────────────────────────────────────────────────────────
    def _authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        - If token.json exists and is valid → reuse it.
        - If token is expired but has a refresh token → auto-refresh.
        - If no valid token → open browser for first-time sign-in.
        Returns True on success, False on failure.
        """
        if not GOOGLE_LIBS_OK:
            self.logger.error(
                "\n"
                "  ✗ Google API libraries not installed.\n"
                "  Fix: pip install google-auth google-auth-oauthlib google-api-python-client\n"
            )
            return False

        # Validate that credentials.json exists and is non-empty
        if not self.credentials_path.exists() or self.credentials_path.stat().st_size == 0:
            self.logger.error(
                f"\n"
                f"  ✗ credentials.json not found or is empty at:\n"
                f"    {self.credentials_path}\n"
                f"\n"
                f"  To fix this:\n"
                f"  1. Go to https://console.cloud.google.com\n"
                f"  2. APIs & Services → Credentials → Create Credentials → OAuth client ID\n"
                f"  3. Application type: Desktop app\n"
                f"  4. Download JSON and save it as:\n"
                f"     {self.credentials_path}\n"
            )
            return False

        # Validate that the JSON is parseable
        try:
            creds_data = json.loads(self.credentials_path.read_text(encoding="utf-8"))
            if not creds_data:
                raise ValueError("Empty JSON object")
        except Exception as e:
            self.logger.error(
                f"  ✗ credentials.json is not valid JSON: {e}\n"
                f"    Re-download it from Google Cloud Console."
            )
            return False

        creds = None

        # Try loading saved token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), SCOPES
                )
                self.logger.debug("Loaded saved token from token.json")
            except Exception as e:
                self.logger.warning(f"Could not load token.json: {e} — will re-authenticate.")
                creds = None

        # Refresh or re-authenticate as needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    self.logger.info("Access token expired — refreshing...")
                    creds.refresh(Request())
                    self.logger.info("Token refreshed successfully.")
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e} — re-authenticating.")
                    creds = None

            if not creds or not creds.valid:
                self.logger.info(
                    "\n"
                    "  → Opening browser for first-time Gmail sign-in.\n"
                    "    Sign in with your Google account and grant access.\n"
                    "    The browser will close automatically when done.\n"
                )
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"  ✗ OAuth sign-in failed: {e}")
                    return False

            # Persist the token for next run
            self.token_path.write_text(creds.to_json(), encoding="utf-8")
            self.logger.info(f"  ✓ Token saved to {self.token_path}")

        # Build the Gmail service
        try:
            self.service = build("gmail", "v1", credentials=creds)
            self.logger.info("  ✓ Gmail authenticated successfully.")
            return True
        except Exception as e:
            self.logger.error(f"  ✗ Failed to build Gmail service: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Email fetching
    # ──────────────────────────────────────────────────────────────────────────
    def check_for_updates(self) -> list[dict]:
        """Return list of new unprocessed message dicts from Gmail."""
        if self.service is None:
            return []
        try:
            response = (
                self.service.users()
                .messages()
                .list(userId="me", q=self.query, maxResults=25)
                .execute()
            )
            all_msgs = response.get("messages", [])
            new_msgs = [m for m in all_msgs if m["id"] not in self._processed_ids]
            if new_msgs:
                self.logger.info(f"Found {len(new_msgs)} new message(s) to process.")
            return new_msgs
        except HttpError as e:
            if e.resp.status == 401:
                self.logger.warning("Auth error — attempting re-authentication...")
                self._authenticate()
            else:
                self.logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error checking Gmail: {e}")
            return []

    # ──────────────────────────────────────────────────────────────────────────
    # Email body extraction
    # ──────────────────────────────────────────────────────────────────────────
    def _decode_body(self, part: dict) -> str:
        """Decode a base64url-encoded email body part."""
        data = part.get("body", {}).get("data", "")
        if not data:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
            return decoded
        except Exception:
            return ""

    def _extract_body(self, payload: dict) -> str:
        """
        Recursively extract plain-text body from a Gmail message payload.
        Prefers text/plain; falls back to stripping HTML from text/html.
        """
        mime_type = payload.get("mimeType", "")
        parts = payload.get("parts", [])

        if mime_type == "text/plain":
            text = self._decode_body(payload)
            return text.strip()

        if mime_type == "text/html":
            html = self._decode_body(payload)
            # Strip HTML tags for a readable plain-text version
            clean = re.sub(r"<[^>]+>", " ", html)
            clean = re.sub(r"\s+", " ", clean).strip()
            return clean

        # Multipart — recurse into parts
        plain_text = ""
        html_fallback = ""
        for part in parts:
            result = self._extract_body(part)
            part_type = part.get("mimeType", "")
            if part_type == "text/plain" and result and not plain_text:
                plain_text = result
            elif part_type == "text/html" and result and not html_fallback:
                html_fallback = result
            elif result and not plain_text:
                plain_text = result

        return plain_text or html_fallback or ""

    # ──────────────────────────────────────────────────────────────────────────
    # Action file creation
    # ──────────────────────────────────────────────────────────────────────────
    def create_action_file(self, message: dict) -> Path:
        """Fetch the full message and write a structured .md action file."""
        msg_id = message["id"]

        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
        except Exception as e:
            self.logger.error(f"Failed to fetch message {msg_id}: {e}")
            # Mark as processed so we don't retry forever on a bad message
            self._processed_ids.add(msg_id)
            self._save_processed_ids()
            return Path()

        # ── Parse headers ──────────────────────────────────────────────────
        raw_headers = msg.get("payload", {}).get("headers", [])
        headers: dict[str, str] = {}
        for h in raw_headers:
            headers[h["name"].lower()] = h["value"]

        sender      = headers.get("from", "unknown@unknown.com")
        subject     = headers.get("subject", "(no subject)")
        reply_to    = headers.get("reply-to", sender)
        date_str    = headers.get("date", datetime.now().isoformat())
        message_id_header = headers.get("message-id", "")

        # ── Extract body ───────────────────────────────────────────────────
        snippet = msg.get("snippet", "")[:300]
        body = self._extract_body(msg.get("payload", {}))
        # Limit body to 2000 chars to keep action files readable
        body_preview = body[:2000] + ("..." if len(body) > 2000 else "")
        if not body_preview.strip():
            body_preview = snippet  # fallback to snippet

        # ── Determine priority ─────────────────────────────────────────────
        subject_lower = subject.lower()
        body_lower = body.lower()
        is_high = any(
            kw in subject_lower or kw in body_lower
            for kw in HIGH_PRIORITY_KEYWORDS
        )
        priority = "high" if is_high else "medium"

        # ── Build filename ─────────────────────────────────────────────────
        safe_subject = re.sub(r"[^\w\-]", "_", subject[:45]).strip("_")
        timestamp    = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename     = f"EMAIL_{timestamp}_{safe_subject}.md"
        action_file  = self.needs_action / filename

        # ── Write action file ──────────────────────────────────────────────
        content = f"""---
type: email
source: gmail
message_id: "{msg_id}"
message_id_header: "{message_id_header}"
from: "{sender}"
reply_to: "{reply_to}"
subject: "{subject}"
received_at: {datetime.now().isoformat()}
date_header: "{date_str}"
priority: {priority}
status: pending
---

## Email Details

| Field   | Value |
|---------|-------|
| From    | {sender} |
| Subject | {subject} |
| Date    | {date_str} |
| Priority | {priority.upper()} |

## Body

{body_preview}

---

## Triage Notes

_To be filled by Claude during `/process-gmail`_

## Available Actions

- **Draft reply** → `/draft-email-reply {filename}` → creates approval in /Pending_Approval/
- **Mark as FYI** → move to /Done/ with note
- **Create plan** → `/create-plan {filename}` for multi-step follow-up
- **Escalate** → set `status: needs_human`
"""

        action_file.write_text(content, encoding="utf-8")

        # Mark as processed
        self._processed_ids.add(msg_id)
        self._save_processed_ids()

        self.logger.info(
            f"  ✓ Created: {filename}  [{priority.upper()}]  "
            f"from={sender[:40]}"
        )
        self.log_action(
            "EMAIL_RECEIVED",
            f"New email from {sender} — subject: {subject[:60]}",
        )
        return action_file

    # ──────────────────────────────────────────────────────────────────────────
    # Run loop (auth first, then poll)
    # ──────────────────────────────────────────────────────────────────────────
    def run(self):
        self.logger.info("=" * 60)
        self.logger.info("  Gmail Watcher — AI Employee Silver Tier")
        self.logger.info("=" * 60)
        self.logger.info(f"  Vault:    {self.vault_path}")
        self.logger.info(f"  Creds:    {self.credentials_path}")
        self.logger.info(f"  Token:    {self.token_path}")
        self.logger.info(f"  Query:    {self.query}")
        self.logger.info(f"  Interval: {self.check_interval}s")
        self.logger.info("=" * 60)

        if not self._authenticate():
            self.logger.error("Cannot start — authentication failed. See errors above.")
            sys.exit(1)

        super().run()


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Gmail Watcher — monitors Gmail and creates action files for Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python watchers/gmail_watcher.py
  python watchers/gmail_watcher.py --vault AI_Employee_Vault --interval 60
  python watchers/gmail_watcher.py --query "is:unread is:important"
  python watchers/gmail_watcher.py --creds /path/to/credentials.json
        """,
    )
    parser.add_argument(
        "--vault",
        default=os.getenv("VAULT_PATH", "AI_Employee_Vault"),
        help="Path to the Obsidian vault root (default: AI_Employee_Vault)",
    )
    parser.add_argument(
        "--creds",
        default=os.getenv("GMAIL_CREDS", "credentials.json"),
        help="Path to Google OAuth credentials.json (default: credentials.json)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GMAIL_TOKEN", "token.json"),
        help="Path to save/load the OAuth token (default: token.json)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("GMAIL_INTERVAL", "120")),
        help="Polling interval in seconds (default: 120)",
    )
    parser.add_argument(
        "--query",
        default=os.getenv("GMAIL_QUERY", "is:unread"),
        help='Gmail search query (default: "is:unread")',
    )
    args = parser.parse_args()

    watcher = GmailWatcher(
        vault_path=args.vault,
        credentials_path=args.creds,
        token_path=args.token,
        check_interval=args.interval,
        query=args.query,
    )
    watcher.run()


if __name__ == "__main__":
    main()
