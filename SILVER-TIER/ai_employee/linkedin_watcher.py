# linkedin_watcher.py — Monitor /Approved/ for approved LinkedIn posts
# Also handles creating weekly draft requests on a schedule

from base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import os
import schedule
import time


class LinkedInWatcher(BaseWatcher):
    def __init__(self, vault_path: str = None):
        super().__init__(vault_path, check_interval=3600)
        self.linkedin_drafts = self.vault_path / 'Social' / 'LinkedIn_Drafts'
        self.linkedin_posted = self.vault_path / 'Social' / 'Posted'
        self.approved_folder = self.vault_path / 'Approved'
        self.post_days = os.getenv('LINKEDIN_POST_DAYS', 'monday,wednesday,friday').split(',')
        self.post_time = os.getenv('LINKEDIN_POST_TIME', '10:00')

        self.linkedin_drafts.mkdir(parents=True, exist_ok=True)
        self.linkedin_posted.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"🔗 LinkedIn Watcher initialized | Post days: {self.post_days}")

    def check_for_updates(self) -> list:
        """Check for any approved LinkedIn posts ready to be published"""
        return list(self.approved_folder.glob("LINKEDIN_*.md"))

    def create_action_file(self, approved_file: Path) -> Path:
        """Convert an approved LinkedIn post into an action file for Claude"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"POST_LINKEDIN_{timestamp}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: linkedin_post_action
source_file: {approved_file.name}
scheduled_for: {datetime.now().isoformat()}
status: ready_to_post
dry_run: {self.dry_run}
---

# 🔗 LinkedIn Post — Ready to Execute

**Source:** {approved_file.name}
**Action:** Publish via LinkedIn API

## Instructions for Claude Code
1. Read the approved post content from: {approved_file}
2. If DRY_RUN=false → Publish via LinkedIn API using the linkedin-api package
3. If DRY_RUN=true → Log the intent only (no real post will be made)
4. On success: move source file to /Social/Posted/ with a timestamp
5. Update Dashboard.md LinkedIn section (posts this week, last post date)
6. Log the action to /Logs/ with timestamp and post preview
7. Move this action file to /Done/
"""
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"✅ LinkedIn action file created: {filename}")
        return filepath

    def create_weekly_draft_request(self):
        """Create a task file asking Claude to write a LinkedIn post draft"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SCHEDULED_LinkedInDraft_{timestamp}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: scheduled_task
task_name: linkedin_draft
day: {datetime.now().strftime('%A')}
scheduled_for: {datetime.now().isoformat()}
status: pending
---

# 🔗 Scheduled Task: Create LinkedIn Post Draft

**Day:** {datetime.now().strftime('%A')}
**Time:** {datetime.now().strftime('%H:%M')}

## Instructions for Claude Code
1. Read Business_Goals.md for the current business focus and objectives
2. Scan /Social/Posted/ — note the last 5 post topics to avoid repeating them
3. Choose a fresh, helpful, and relevant topic
4. Write a professional LinkedIn post (150–300 words)
5. Add 3–5 relevant hashtags at the very end of the post
6. End the post with a question or a clear call-to-action
7. Save the draft to: /Social/LinkedIn_Drafts/DRAFT_{timestamp}.md
8. Create an approval request: /Pending_Approval/LINKEDIN_{timestamp}.md
9. Update the Dashboard.md LinkedIn section to reflect 1 pending draft
10. Move this task file to /Done/
"""
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"📝 LinkedIn draft request created: {filename}")
        return filepath


if __name__ == "__main__":
    watcher = LinkedInWatcher()

    # Schedule weekly draft creation
    for day in watcher.post_days:
        getattr(schedule.every(), day.strip()).at(watcher.post_time).do(
            watcher.create_weekly_draft_request
        )
    watcher.logger.info(f"📅 LinkedIn drafts scheduled for: {watcher.post_days} at {watcher.post_time}")

    while True:
        schedule.run_pending()
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
        time.sleep(60)
