"""
linkedin_watcher.py — LinkedIn Watcher for AI Employee (Silver Tier)

Does two things every cycle:
  1. PUBLISH  — Scans /Approved/ folder for approved LinkedIn posts and publishes them.
  2. MONITOR  — Checks LinkedIn notifications for new messages, connection requests,
                and post mentions; creates .md action files in /Needs_Action/.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRST-TIME SETUP (do this once):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Install Playwright:
     pip install playwright
     playwright install chromium

2. Run --setup to save your LinkedIn session:
     python watchers/linkedin_watcher.py --setup

3. Sign in to LinkedIn in the browser that opens.
   Wait ~3 seconds after the home feed loads, then close the window.
   Your session is saved in ./linkedin_profile/ for headless future runs.

4. Normal operation (headless):
     python watchers/linkedin_watcher.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    python watchers/linkedin_watcher.py [--vault PATH] [--interval SECS] [--headed] [--setup]

Environment variables (.env):
    VAULT_PATH=./AI_Employee_Vault
    LINKEDIN_PROFILE=./linkedin_profile
    LINKEDIN_CHECK_INTERVAL=300
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# ─── Playwright (optional — fail gracefully) ──────────────────────────────────
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False

LINKEDIN_URL = "https://www.linkedin.com"
FEED_URL     = "https://www.linkedin.com/feed/"
NOTIF_URL    = "https://www.linkedin.com/notifications/"


# ─────────────────────────────────────────────────────────────────────────────
class LinkedInWatcher(BaseWatcher):
    """
    Silver-tier LinkedIn automation:
      • Publishes approved posts from /Approved/ to LinkedIn.
      • Monitors LinkedIn notifications → writes action files to /Needs_Action/.
    """

    def __init__(
        self,
        vault_path: str,
        profile_dir: str | None = None,
        check_interval: int = 300,
        headless: bool = False,  # LinkedIn requires headed mode (bot detection)
    ):
        super().__init__(vault_path, check_interval=check_interval)
        self.profile_dir = Path(
            profile_dir or os.getenv("LINKEDIN_PROFILE", "./linkedin_profile")
        ).resolve()
        self.headless = headless

        # Vault folders
        self.approved_dir   = self.vault_path / "Approved"
        self.done_dir       = self.vault_path / "Done"
        self.pending_dir    = self.vault_path / "Pending_Approval"
        self.approved_dir.mkdir(parents=True, exist_ok=True)

        # Persist already-handled notification IDs
        self._seen_notifs: set[str] = self._load_seen()

        # Playwright handles
        self._playwright = None
        self._browser    = None
        self._page       = None

    # ──────────────────────────────────────────────────────────────────────────
    # Seen-notification persistence
    # ──────────────────────────────────────────────────────────────────────────
    @property
    def _seen_file(self) -> Path:
        return self.vault_path / ".linkedin_seen.json"

    def _load_seen(self) -> set[str]:
        if self._seen_file.exists():
            try:
                return set(json.loads(self._seen_file.read_text(encoding="utf-8")))
            except Exception:
                pass
        return set()

    def _save_seen(self) -> None:
        self._seen_file.write_text(
            json.dumps(sorted(self._seen_notifs), indent=2),
            encoding="utf-8",
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Browser management
    # ──────────────────────────────────────────────────────────────────────────
    def _start_browser(self) -> bool:
        if not PLAYWRIGHT_OK:
            self.logger.error(
                "\n"
                "  ✗ Playwright not installed.\n"
                "  Fix:\n"
                "    pip install playwright\n"
                "    playwright install chromium\n"
            )
            return False

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()

        # LinkedIn aggressively blocks headless browsers even with saved profiles.
        # We always run in headed (visible) mode — the user can minimize the window.
        # headless=False is intentional and required for reliable LinkedIn automation.
        self._browser = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=False,   # LinkedIn bot-detection requires headed mode
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
            ignore_default_args=["--enable-automation"],
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        if self._browser.pages:
            self._page = self._browser.pages[0]
        else:
            self._page = self._browser.new_page()

        # Hide the webdriver flag that LinkedIn checks for
        self._page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.logger.info("  ✓ Browser started (headed — you can minimize the window).")
        return True

    def _close_browser(self) -> None:
        try:
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._browser    = None
        self._playwright = None
        self._page       = None

    def _is_logged_in(self) -> bool:
        """Navigate to LinkedIn and check if we're authenticated."""
        try:
            self._page.goto(FEED_URL, wait_until="domcontentloaded", timeout=40_000)
            time.sleep(3)  # let JS hydrate

            # Check URL — if we got redirected to /login or /checkpoint, we're not in
            current_url = self._page.url
            if "/login" in current_url or "/checkpoint" in current_url or "/authwall" in current_url:
                self.logger.warning(
                    "  ✗ Not logged in (redirected to login page).\n"
                    "  Run: python watchers/linkedin_watcher.py --setup"
                )
                return False

            # Try several selectors that appear when logged in
            logged_in_selectors = [
                "nav.global-nav",                          # top nav bar
                "[data-global-nav-search-typeahead]",      # search bar in nav
                ".global-nav__me-photo",                   # profile photo
                "img.global-nav__me-photo",
                "[aria-label='LinkedIn Home']",
                ".feed-identity-module",                   # left sidebar identity block
                ".scaffold-layout",                        # main layout
            ]
            for sel in logged_in_selectors:
                if self._page.query_selector(sel):
                    self.logger.info("  ✓ LinkedIn session active.")
                    return True

            # Last check: if the page title contains "Feed" or "LinkedIn"
            title = self._page.title()
            if "feed" in title.lower() or ("linkedin" in title.lower() and "sign" not in title.lower()):
                self.logger.info("  ✓ LinkedIn session active (via page title).")
                return True

            self.logger.warning(
                "  ✗ Not logged in to LinkedIn.\n"
                "  Run: python watchers/linkedin_watcher.py --setup"
            )
            return False
        except PWTimeout:
            self.logger.error("  ✗ Timed out loading LinkedIn. Check your internet connection.")
            return False
        except Exception as e:
            self.logger.error(f"  ✗ Error checking LinkedIn login: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # First-time setup — open browser so user can sign in
    # ──────────────────────────────────────────────────────────────────────────
    def setup_session(self) -> None:
        """Open a headed browser so the user can sign in and save the session."""
        if not PLAYWRIGHT_OK:
            self.logger.error("Playwright not installed — cannot run setup.")
            return

        self.headless = False
        if not self._start_browser():
            return

        self.logger.info(
            "\n"
            "  ┌──────────────────────────────────────────────────┐\n"
            "  │  LinkedIn Setup — Sign In                        │\n"
            "  ├──────────────────────────────────────────────────┤\n"
            "  │  1. The browser has opened LinkedIn.             │\n"
            "  │  2. Sign in with your LinkedIn credentials.      │\n"
            "  │  3. Wait until your home feed fully loads.       │\n"
            "  │  4. Close the browser window when done.          │\n"
            "  │     (Session is saved automatically.)            │\n"
            "  └──────────────────────────────────────────────────┘\n"
        )

        try:
            self._page.goto(LINKEDIN_URL, wait_until="domcontentloaded", timeout=30_000)
            # Block until the user closes the browser (or feed loads + 5 sec pause)
            try:
                self._page.wait_for_selector(
                    '[data-global-nav-search-typeahead]', timeout=300_000
                )
                self.logger.info("  ✓ Signed in — saving session...")
                time.sleep(4)
            except PWTimeout:
                self.logger.warning("  ! Timed out waiting for sign-in.")
        finally:
            self._close_browser()

        self.logger.info(
            f"  ✓ Session saved to: {self.profile_dir}\n"
            f"  You can now run the watcher normally:\n"
            f"    python watchers/linkedin_watcher.py\n"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLISHER — find and post approved LinkedIn posts
    # ──────────────────────────────────────────────────────────────────────────
    def _get_approved_posts(self) -> list[Path]:
        """Return all approved LinkedIn post files from /Approved/."""
        posts = []
        for f in sorted(self.approved_dir.glob("*LinkedIn*")):
            if f.suffix == ".md" and f.is_file():
                posts.append(f)
        return posts

    def _parse_post_content(self, filepath: Path) -> str | None:
        """Extract the 'Draft Post' section from an approval file."""
        text = filepath.read_text(encoding="utf-8")

        # Try to find the Draft Post section
        patterns = [
            r"## Draft Post\s*\n+([\s\S]+?)(?=\n##|\Z)",
            r"## Post Content\s*\n+([\s\S]+?)(?=\n##|\Z)",
            r"## Content\s*\n+([\s\S]+?)(?=\n##|\Z)",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                content = m.group(1).strip()
                if content:
                    return content

        # Fallback: look for any block of text that looks like a post
        lines = [l for l in text.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("#")]
        if lines:
            return "\n".join(lines[:20])

        return None

    def _publish_post(self, post_text: str) -> bool:
        """
        Navigate to LinkedIn and publish a post.
        Returns True on success, False on failure.
        """
        try:
            self._page.goto(FEED_URL, wait_until="domcontentloaded", timeout=30_000)

            # ── Open compose modal ─────────────────────────────────────────
            compose_selectors = [
                '[data-artdeco-is-focused="true"] button',
                'button[aria-label*="Start a post"]',
                'button[aria-label*="Create a post"]',
                '.share-box-feed-entry__trigger',
                '[data-test-id="share-button"]',
                '.artdeco-button--muted',
            ]
            compose_btn = None
            for sel in compose_selectors:
                compose_btn = self._page.query_selector(sel)
                if compose_btn:
                    break

            if not compose_btn:
                # Try clicking the share text box area
                self._page.click('div[role="textbox"][aria-label*="start a post" i], '
                                  '.share-box__open')
            else:
                compose_btn.click()

            # Wait for the modal / compose area to appear
            self._page.wait_for_selector(
                'div[role="textbox"], .ql-editor, [contenteditable="true"]',
                timeout=10_000,
            )
            time.sleep(1)

            # ── Type post content ──────────────────────────────────────────
            editor = self._page.query_selector(
                'div[role="textbox"], .ql-editor, [contenteditable="true"]'
            )
            if not editor:
                self.logger.error("  ✗ Could not locate LinkedIn post editor.")
                return False

            editor.click()
            editor.fill("")  # clear any placeholder
            # Type slowly to avoid detection
            self._page.keyboard.type(post_text, delay=20)
            time.sleep(1)

            # ── Verify content ─────────────────────────────────────────────
            typed = editor.inner_text()
            if not typed.strip():
                self.logger.error("  ✗ Post text did not appear in editor.")
                return False

            # ── Click Post button ──────────────────────────────────────────
            post_btn_selectors = [
                'button[aria-label="Post"]',
                'button.share-actions__primary-action',
                'button[data-control-name="share.post"]',
                'button:has-text("Post")',
            ]
            post_btn = None
            for sel in post_btn_selectors:
                post_btn = self._page.query_selector(sel)
                if post_btn and post_btn.is_enabled():
                    break

            if not post_btn:
                self.logger.error("  ✗ Could not find the Post button.")
                return False

            post_btn.click()

            # ── Wait for confirmation ──────────────────────────────────────
            try:
                self._page.wait_for_selector(
                    '[data-test-artdeco-dialog-negate], '
                    '.artdeco-toast-item, '
                    '.post-reshare-confirm-modal',
                    timeout=10_000,
                )
            except PWTimeout:
                pass  # Some LinkedIn versions don't show an explicit confirm

            time.sleep(2)
            self.logger.info("  ✓ Post published to LinkedIn.")
            return True

        except PWTimeout as e:
            self.logger.error(f"  ✗ Timeout while publishing: {e}")
            return False
        except Exception as e:
            self.logger.error(f"  ✗ Error publishing post: {e}")
            return False

    def _process_approved_posts(self) -> None:
        """Find approved LinkedIn posts and publish them one by one."""
        approved_posts = self._get_approved_posts()
        if not approved_posts:
            return

        self.logger.info(f"Found {len(approved_posts)} approved LinkedIn post(s) to publish.")

        for post_file in approved_posts:
            post_text = self._parse_post_content(post_file)
            if not post_text:
                self.logger.warning(f"  ! Could not extract post content from {post_file.name}")
                continue

            self.logger.info(f"  Publishing: {post_file.name}")
            success = self._publish_post(post_text)

            if success:
                # Update the file's status
                content = post_file.read_text(encoding="utf-8")
                content = re.sub(r"(status:\s*)[\w_]+", r"\1done", content)
                content += f"\n\n## Execution Summary\n\nPublished to LinkedIn at {datetime.now().isoformat()} by LinkedIn Watcher.\n"
                post_file.write_text(content, encoding="utf-8")

                # Move to Done
                dest = self.done_dir / post_file.name
                shutil.move(str(post_file), str(dest))

                self.log_action(
                    "LINKEDIN_POST_PUBLISHED",
                    f"Post published and moved to Done: {post_file.name}",
                )
            else:
                # Mark as failed so it doesn't retry endlessly
                content = post_file.read_text(encoding="utf-8")
                content = re.sub(r"(status:\s*)[\w_]+", r"\1failed", content)
                content += (
                    f"\n\n## Failure Note\n\n"
                    f"Publish attempt failed at {datetime.now().isoformat()}. "
                    f"Please review and re-approve, or post manually.\n"
                )
                post_file.write_text(content, encoding="utf-8")
                self.log_action(
                    "LINKEDIN_POST_FAILED",
                    f"Failed to publish: {post_file.name}",
                    status="error",
                )

    # ──────────────────────────────────────────────────────────────────────────
    # MONITOR — check LinkedIn notifications
    # ──────────────────────────────────────────────────────────────────────────
    def _get_notification_badge_count(self) -> int:
        """
        Check the notification bell badge on the main nav.
        Returns the count of unread notifications (0 if none or unreadable).
        This is more reliable than navigating to the full notifications page.
        """
        try:
            # Stay on the feed page — badge is always visible in the nav
            if "linkedin.com/feed" not in self._page.url:
                self._page.goto(FEED_URL, wait_until="domcontentloaded", timeout=30_000)
                time.sleep(2)

            badge_selectors = [
                '[data-control-name="nav.notifications"] .notification-badge__count',
                '[href*="/notifications/"] .notification-badge',
                '.nav-item--notifications .badge-count',
                '[aria-label*="notification" i] .count-value',
            ]
            for sel in badge_selectors:
                el = self._page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text.isdigit():
                        return int(text)
            return 0
        except Exception:
            return 0

    def _scrape_notifications(self) -> list[dict]:
        """
        Check LinkedIn notifications.
        Strategy: read the badge count on the main nav first (reliable).
        If there are new notifications, navigate to the page and scrape them.
        If navigation fails, log it gracefully — this does not stop the watcher.
        """
        notifications = []
        try:
            badge_count = self._get_notification_badge_count()
            if badge_count == 0:
                self.logger.info("  No new LinkedIn notifications.")
                return []

            self.logger.info(f"  {badge_count} new LinkedIn notification(s) — reading...")

            # Navigate to notifications page with error handling
            try:
                self._page.goto(NOTIF_URL, wait_until="domcontentloaded", timeout=35_000)
                time.sleep(4)
            except Exception as nav_err:
                self.logger.warning(f"  ! Could not load notifications page: {nav_err}")
                # Create a generic "you have notifications" action file so user knows
                notif_id = f"badge_{badge_count}_{datetime.now().strftime('%Y%m%d%H%M')}"
                if notif_id not in self._seen_notifs:
                    notifications.append({
                        "id":   notif_id,
                        "text": f"You have {badge_count} new LinkedIn notification(s). Check LinkedIn manually.",
                        "urn":  "",
                    })
                return notifications

            # If redirected away, return generic notification
            if "notifications" not in self._page.url:
                notif_id = f"badge_{badge_count}_{datetime.now().strftime('%Y%m%d%H%M')}"
                if notif_id not in self._seen_notifs:
                    notifications.append({
                        "id":   notif_id,
                        "text": f"You have {badge_count} new LinkedIn notification(s). Check LinkedIn manually.",
                        "urn":  "",
                    })
                return notifications

            # Try to read notification cards
            card_selectors = [
                ".nt-card", ".notification-card",
                ".artdeco-list__item", "[data-urn]", "main li",
            ]
            items = []
            for sel in card_selectors:
                items = self._page.query_selector_all(sel)
                if items:
                    break

            for item in items[:20]:
                try:
                    text = item.inner_text()[:300].strip()
                    if not text or len(text) < 5:
                        continue
                    urn = item.get_attribute("data-urn") or ""
                    notif_id = urn if urn else re.sub(r"\s+", "_", text[:80])
                    if notif_id in self._seen_notifs:
                        continue
                    is_new = bool(item.query_selector('[class*="unseen"],[class*="unread"],[class*="new-"]'))
                    if not is_new and not urn:
                        continue
                    notifications.append({"id": notif_id, "text": text, "urn": urn})
                except Exception:
                    continue

        except Exception as e:
            self.logger.warning(f"  ! Notification check skipped: {e}")

        return notifications

    def _classify_notification(self, text: str) -> tuple[str, str]:
        """
        Return (notif_type, priority) based on notification text.
        Types: message, connection, comment, mention, reaction, job, other
        """
        t = text.lower()
        if any(w in t for w in ["sent you a message", "messaged you", "inbox"]):
            return "message", "high"
        if any(w in t for w in ["connected with you", "connection request", "wants to connect"]):
            return "connection", "medium"
        if any(w in t for w in ["commented on", "replied to", "responded to"]):
            return "comment", "medium"
        if any(w in t for w in ["mentioned you", "tagged you", "@"]):
            return "mention", "high"
        if any(w in t for w in ["reacted to", "liked your", "celebrated your"]):
            return "reaction", "low"
        if any(w in t for w in ["job", "hiring", "opportunity", "recruiter"]):
            return "job", "medium"
        return "other", "low"

    # ──────────────────────────────────────────────────────────────────────────
    # BaseWatcher interface
    # ──────────────────────────────────────────────────────────────────────────
    def check_for_updates(self) -> list[dict]:
        """
        One cycle:
          1. Publish any approved posts.
          2. Scrape new notifications.
        Returns notifications to convert to action files.
        """
        # Step 1 — publish approved posts
        self._process_approved_posts()

        # Step 2 — scrape notifications
        notifications = self._scrape_notifications()
        if notifications:
            self.logger.info(f"  Found {len(notifications)} new LinkedIn notification(s).")

        return notifications

    def create_action_file(self, notification: dict) -> Path:
        """Write a .md action file for a LinkedIn notification."""
        notif_id = notification["id"]
        text     = notification["text"]
        urn      = notification["urn"]

        notif_type, priority = self._classify_notification(text)

        safe_id  = re.sub(r"[^\w\-]", "_", notif_id[:40]).strip("_")
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename  = f"LINKEDIN_{timestamp}_{notif_type.upper()}_{safe_id}.md"
        action_file = self.needs_action / filename

        content = f"""---
type: linkedin
source: linkedin_watcher
notification_type: {notif_type}
notification_urn: "{urn}"
received_at: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

## LinkedIn Notification

**Type:** {notif_type.upper()}
**Priority:** {priority.upper()}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Content

> {text}

## Triage Notes

_To be filled by Claude during `/process-linkedin`_

## Suggested Actions

| Action | When |
|--------|------|
| Draft a reply | If type is `message` or `comment` |
| Accept connection | If type is `connection` and contact looks relevant |
| Acknowledge mention | If type is `mention` — like or reply |
| Log and ignore | If type is `reaction` or `other` |
"""

        action_file.write_text(content, encoding="utf-8")

        # Mark as seen
        self._seen_notifs.add(notif_id)
        self._save_seen()

        self.logger.info(f"  ✓ Created: {filename}  [{priority.upper()}]  type={notif_type}")
        self.log_action("LINKEDIN_NOTIFICATION", f"New {notif_type}: {text[:80]}")
        return action_file

    # ──────────────────────────────────────────────────────────────────────────
    # Run loop
    # ──────────────────────────────────────────────────────────────────────────
    def run(self) -> None:
        self.logger.info("=" * 60)
        self.logger.info("  LinkedIn Watcher — AI Employee Silver Tier")
        self.logger.info("=" * 60)
        self.logger.info(f"  Vault:    {self.vault_path}")
        self.logger.info(f"  Profile:  {self.profile_dir}")
        self.logger.info(f"  Headless: {self.headless}")
        self.logger.info(f"  Interval: {self.check_interval}s")
        self.logger.info("=" * 60)

        if not self._start_browser():
            sys.exit(1)

        if not self._is_logged_in():
            self._close_browser()
            self.logger.error(
                "Not logged in. Run first-time setup:\n"
                "  python watchers/linkedin_watcher.py --setup"
            )
            sys.exit(1)

        try:
            super().run()
        finally:
            self._close_browser()


# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn Watcher — publishes approved posts and monitors notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time setup (opens browser to sign in):
  python watchers/linkedin_watcher.py --setup

  # Normal operation:
  python watchers/linkedin_watcher.py
  python watchers/linkedin_watcher.py --vault AI_Employee_Vault --interval 300
  python watchers/linkedin_watcher.py --headed   # visible browser for debugging
        """,
    )
    parser.add_argument(
        "--vault",
        default=os.getenv("VAULT_PATH", "AI_Employee_Vault"),
        help="Path to the Obsidian vault root",
    )
    parser.add_argument(
        "--profile",
        default=os.getenv("LINKEDIN_PROFILE", "./linkedin_profile"),
        help="Directory to save the browser session (default: ./linkedin_profile)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("LINKEDIN_CHECK_INTERVAL", "300")),
        help="Check interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (NOT recommended — LinkedIn blocks headless browsers)",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run first-time setup: open browser to sign in and save session",
    )
    args = parser.parse_args()

    watcher = LinkedInWatcher(
        vault_path=args.vault,
        profile_dir=args.profile,
        check_interval=args.interval,
        headless=args.headless,   # default is False (headed mode required for LinkedIn)
    )

    if args.setup:
        watcher.setup_session()
    else:
        watcher.run()


if __name__ == "__main__":
    main()
