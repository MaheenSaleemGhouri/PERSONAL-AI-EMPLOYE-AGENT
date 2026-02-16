# whatsapp_watcher.py — Monitor WhatsApp Web for urgent keyword messages
# Uses Playwright to automate WhatsApp Web browser session
# NOTE: Review WhatsApp's Terms of Service before deploying in production

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os


class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str = None):
        super().__init__(vault_path, check_interval=30)
        self.session_path = os.getenv('WHATSAPP_SESSION_PATH', './whatsapp_session')
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote']
        self.processed_messages = set()
        self.logger.info(f"📱 WhatsApp Watcher initialized | Keywords: {self.keywords}")

    def check_for_updates(self) -> list:
        """Fetch unread urgent messages from WhatsApp Web"""
        urgent_messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=True,
                    args=['--no-sandbox']
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', timeout=30000)

                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=20000)
                except PlaywrightTimeout:
                    self.logger.warning("⚠️ WhatsApp Web load timeout — session likely expired, please log in again")
                    browser.close()
                    return []

                unread_chats = page.query_selector_all('[data-testid="cell-frame-container"]')

                for chat in unread_chats:
                    try:
                        unread_badge = chat.query_selector('[aria-label*="unread"]')
                        if not unread_badge:
                            continue

                        chat_text = chat.inner_text().lower()
                        sender_el = chat.query_selector('[data-testid="cell-frame-title"]')
                        sender_name = sender_el.inner_text() if sender_el else "Unknown"

                        matched_keywords = [kw for kw in self.keywords if kw in chat_text]
                        if matched_keywords:
                            msg_id = f"{sender_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                            if msg_id not in self.processed_messages:
                                urgent_messages.append({
                                    'sender': sender_name,
                                    'preview': chat_text[:200],
                                    'keywords': matched_keywords,
                                    'id': msg_id
                                })
                    except Exception as e:
                        self.logger.debug(f"Chat parse error: {e}")
                        continue

                browser.close()
        except Exception as e:
            self.logger.error(f"❌ WhatsApp Watcher error: {e}")

        return urgent_messages

    def create_action_file(self, message: dict) -> Path:
        """Create an action file for an urgent WhatsApp message"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_sender = message['sender'][:20].replace(' ', '_')
        filename = f"WHATSAPP_{timestamp}_{safe_sender}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: whatsapp_message
sender: "{message['sender']}"
received: {datetime.now().isoformat()}
keywords_matched: {message['keywords']}
priority: high
status: pending
dry_run: {self.dry_run}
---

# 📱 Urgent WhatsApp Message

**From:** {message['sender']}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Priority:** 🔴 HIGH (keyword match: {', '.join(message['keywords'])})

## Message Preview
{message['preview']}

## Suggested Actions
- [ ] Read the full message in WhatsApp
- [ ] Draft a reply (requires human approval before sending)
- [ ] Check if invoice/payment related → create a payment follow-up plan
- [ ] Update Dashboard.md

## Instructions for Claude Code
1. Read Company_Handbook.md WhatsApp Rules
2. Draft an appropriate reply in /Plans/WHATSAPP_REPLY_{timestamp}.md
3. Create an approval file in /Pending_Approval/WHATSAPP_{timestamp}.md
4. Update Dashboard.md WhatsApp section
5. NEVER reply on WhatsApp without explicit human approval
6. Move this file to /Done/ once the plan is created
"""
        filepath.write_text(content, encoding='utf-8')
        self.processed_messages.add(message['id'])
        self.logger.info(f"✅ WhatsApp action file created: {filename}")
        return filepath


if __name__ == "__main__":
    watcher = WhatsAppWatcher()
    watcher.run()
