"""
whatsapp_watcher.py — WhatsApp Web Watcher for AI Employee (Silver Tier)

Uses Playwright to monitor WhatsApp Web for new messages matching keyword triggers.
When a trigger message arrives, creates a structured .md action file in /Needs_Action.

Setup:
    1. pip install playwright python-dotenv
    2. playwright install chromium
    3. Run once with --setup to save your WhatsApp Web session (scan QR code)
    4. After setup, run normally — it reuses the saved browser profile

Usage:
    # First-time setup (opens browser, scan QR code)
    python watchers/whatsapp_watcher.py --setup --vault AI_Employee_Vault

    # Normal operation (headless, monitors for triggers)
    python watchers/whatsapp_watcher.py --vault AI_Employee_Vault

    # Show browser window (useful for debugging)
    python watchers/whatsapp_watcher.py --vault AI_Employee_Vault --headed

Environment variables (.env):
    WHATSAPP_PROFILE_DIR=./whatsapp_profile   # where to save browser session
    WHATSAPP_CHECK_INTERVAL=60                # seconds between checks

Requires:
    pip install playwright python-dotenv
    playwright install chromium
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher  # noqa: E402

# ---------------------------------------------------------------------------
# Optional imports
# ---------------------------------------------------------------------------
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Keyword triggers — messages containing these words create action files
TRIGGER_KEYWORDS = [
    "pricing", "price", "cost", "quote", "invoice", "payment",
    "hire", "available", "proposal", "urgent", "asap", "help",
    "interested", "services", "book", "schedule",
]

WHATSAPP_URL = "https://web.whatsapp.com"


class WhatsAppWatcher(BaseWatcher):
    """Monitors WhatsApp Web for keyword-triggered messages via Playwright."""

    def __init__(
        self,
        vault_path: str,
        profile_dir: str | None = None,
        check_interval: int = 60,
        headless: bool = True,
    ):
        super().__init__(vault_path, check_interval=check_interval)
        self.profile_dir = Path(
            profile_dir or os.getenv("WHATSAPP_PROFILE_DIR", "./whatsapp_profile")
        ).resolve()
        self.headless = headless
        self._processed_msgs: set[str] = self._load_processed()
        self._playwright = None
        self._browser = None
        self._page = None

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _processed_file(self) -> Path:
        return self.vault_path / ".whatsapp_processed.json"

    def _load_processed(self) -> set[str]:
        f = self._processed_file()
        if f.exists():
            try:
                return set(json.loads(f.read_text()))
            except Exception:
                pass
        return set()

    def _save_processed(self) -> None:
        self._processed_file().write_text(
            json.dumps(list(self._processed_msgs), indent=2)
        )

    # ------------------------------------------------------------------
    # Browser management
    # ------------------------------------------------------------------
    def _start_browser(self) -> bool:
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
            return False

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            args=["--no-sandbox"],
        )
        self._page = self._browser.new_page()
        self.logger.info("Browser started.")
        return True

    def _ensure_logged_in(self) -> bool:
        """Navigate to WhatsApp Web and wait for the chat list to appear."""
        try:
            self._page.goto(WHATSAPP_URL, wait_until="domcontentloaded", timeout=30_000)
            # Wait for either the QR code (not logged in) or the chat list (logged in)
            self._page.wait_for_selector(
                '[data-testid="chat-list"], canvas[aria-label="Scan me!"]',
                timeout=30_000,
            )
            # Check which one appeared
            if self._page.query_selector('canvas[aria-label="Scan me!"]'):
                self.logger.warning(
                    "WhatsApp QR code detected — session not active. "
                    "Run with --setup and scan the QR code first."
                )
                return False
            self.logger.info("WhatsApp Web session active.")
            return True
        except PlaywrightTimeout:
            self.logger.error("Timed out waiting for WhatsApp Web to load.")
            return False
        except Exception as e:
            self.logger.error(f"Browser navigation error: {e}")
            return False

    def setup_session(self) -> None:
        """Open WhatsApp Web in headed mode so user can scan the QR code."""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed.")
            return
        self.headless = False
        if not self._start_browser():
            return
        self._page.goto(WHATSAPP_URL)
        self.logger.info(
            "Browser opened. Please scan the QR code on WhatsApp Web.\n"
            "Once logged in, keep this window open for ~5 seconds, then close it.\n"
            "Your session will be saved for future headless runs."
        )
        try:
            # Wait up to 5 minutes for the user to scan — try multiple selectors
            # WhatsApp Web UI changes frequently, so we check several known indicators
            self._page.wait_for_selector(
                '[data-testid="chat-list"], [aria-label="Chat list"], #pane-side, [data-testid="chatlist-header"], div[role="grid"]',
                timeout=300_000,
            )
            self.logger.info("Logged in successfully! Session saved.")
            time.sleep(5)
        except PlaywrightTimeout:
            self.logger.warning("QR scan timed out after 5 minutes. Please try again.")
        finally:
            self._close_browser()

    def _close_browser(self) -> None:
        try:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Message scraping
    # ------------------------------------------------------------------
    def _scrape_unread_messages(self) -> list[dict]:
        """Scrape unread chat previews from the WhatsApp Web chat list."""
        messages = []
        try:
            # Unread chats have a badge counter
            unread_chats = self._page.query_selector_all(
                '[data-testid="chat-list"] [data-testid*="cell-frame-container"]'
            )
            for chat in unread_chats[:10]:  # Cap at 10 to avoid overload
                try:
                    badge = chat.query_selector('[data-testid="icon-unread-count"]')
                    if not badge:
                        continue
                    # Contact name
                    name_el = chat.query_selector('[data-testid="cell-frame-title"]')
                    name = name_el.inner_text() if name_el else "Unknown"
                    # Message preview
                    preview_el = chat.query_selector(
                        '[data-testid="last-msg-status"] ~ span, '
                        '[data-testid="cell-frame-primary-detail"] span span'
                    )
                    preview = preview_el.inner_text() if preview_el else ""
                    # Timestamp
                    ts_el = chat.query_selector('[data-testid="cell-frame-primary-detail"]')
                    timestamp = ts_el.inner_text() if ts_el else ""

                    msg_key = f"{name}_{preview[:50]}"
                    if msg_key not in self._processed_msgs:
                        messages.append(
                            {
                                "contact": name,
                                "preview": preview,
                                "timestamp": timestamp,
                                "key": msg_key,
                            }
                        )
                except Exception as e:
                    self.logger.debug(f"Failed to parse chat element: {e}")
        except Exception as e:
            self.logger.error(f"Failed to scrape WhatsApp: {e}")
        return messages

    def _is_triggered(self, message: dict) -> bool:
        """Return True if the message preview contains a keyword trigger."""
        text = message.get("preview", "").lower()
        return any(kw in text for kw in TRIGGER_KEYWORDS)

    # ------------------------------------------------------------------
    # BaseWatcher interface
    # ------------------------------------------------------------------
    def check_for_updates(self) -> list:
        messages = self._scrape_unread_messages()
        triggered = [m for m in messages if self._is_triggered(m)]
        if triggered:
            self.logger.info(f"Found {len(triggered)} keyword-triggered message(s).")
        return triggered

    def create_action_file(self, message: dict) -> Path:
        contact = message.get("contact", "Unknown")
        preview = message.get("preview", "")
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        safe_contact = re.sub(r"[^\w\-]", "_", contact[:30])
        filename = f"WHATSAPP_{timestamp}_{safe_contact}.md"
        action_file = self.needs_action / filename

        # Detect which keywords matched
        matched = [kw for kw in TRIGGER_KEYWORDS if kw in preview.lower()]

        content = f"""---
type: whatsapp
source: whatsapp_web
contact: "{contact}"
received_at: {datetime.now().isoformat()}
priority: high
status: pending
triggers: {matched}
---

## WhatsApp Message

**From:** {contact}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Trigger Keywords Matched:** {', '.join(matched)}

## Message Preview

> {preview}

## Triage Notes

_To be filled by Claude during /process-whatsapp_

## Suggested Actions

- Draft a reply → creates approval file in /Pending_Approval/
- Escalate as lead → create Plan.md for follow-up
- Mark as handled → move to /Done/
"""

        action_file.write_text(content, encoding="utf-8")
        self._processed_msgs.add(message["key"])
        self._save_processed()
        self.logger.info(f"Created action file: {filename}")
        return action_file

    # ------------------------------------------------------------------
    # Run loop
    # ------------------------------------------------------------------
    def run(self):
        self.logger.info("Starting WhatsAppWatcher...")
        if not self._start_browser():
            return
        if not self._ensure_logged_in():
            self._close_browser()
            return
        try:
            super().run()
        finally:
            self._close_browser()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="WhatsApp Watcher for AI Employee")
    parser.add_argument(
        "--vault",
        default="AI_Employee_Vault",
        help="Path to the Obsidian vault root",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="Path to save the browser profile/session",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run with a visible browser window (for debugging)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Open browser for first-time QR code scan",
    )
    args = parser.parse_args()

    watcher = WhatsAppWatcher(
        vault_path=args.vault,
        profile_dir=args.profile,
        check_interval=args.interval,
        headless=not args.headed,
    )

    if args.setup:
        watcher.setup_session()
    else:
        watcher.run()


if __name__ == "__main__":
    main()
