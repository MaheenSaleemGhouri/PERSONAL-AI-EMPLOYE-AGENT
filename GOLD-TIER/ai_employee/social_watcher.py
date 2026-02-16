# social_watcher.py — Monitor /Approved/ for Facebook, Instagram, Twitter posts
# Also creates weekly social summary task on Sundays

from base_watcher import BaseWatcher
from audit_logger import log_action
from error_handler import with_retry, graceful_degradation
from pathlib import Path
from datetime import datetime
import os
import schedule
import time


class SocialWatcher(BaseWatcher):
    def __init__(self, vault_path: str = None):
        super().__init__(vault_path, check_interval=300)  # Check every 5 minutes
        self.facebook_drafts = self.vault_path / 'Social' / 'Facebook_Drafts'
        self.instagram_drafts = self.vault_path / 'Social' / 'Instagram_Drafts'
        self.twitter_drafts = self.vault_path / 'Social' / 'Twitter_Drafts'
        self.social_summaries = self.vault_path / 'Social' / 'Social_Summaries'
        self.approved = self.vault_path / 'Approved'

        for folder in [self.facebook_drafts, self.instagram_drafts,
                       self.twitter_drafts, self.social_summaries]:
            folder.mkdir(parents=True, exist_ok=True)

        self.logger.info("Social Watcher initialized (Facebook + Instagram + Twitter/X)")

    def check_for_updates(self) -> list:
        """Check /Approved/ for social media posts ready to publish"""
        platforms = ['FACEBOOK_', 'INSTAGRAM_', 'TWITTER_']
        approved = []
        for prefix in platforms:
            approved.extend(list(self.approved.glob(f"{prefix}*.md")))
        return approved

    def create_action_file(self, approved_file: Path) -> Path:
        """Convert approved social post into an executable action file"""
        filename_upper = approved_file.name.upper()
        if 'FACEBOOK' in filename_upper:
            platform = 'facebook'
            mcp_tool = 'post_facebook'
        elif 'INSTAGRAM' in filename_upper:
            platform = 'instagram'
            mcp_tool = 'post_instagram'
        else:
            platform = 'twitter'
            mcp_tool = 'post_tweet'

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"POST_{platform.upper()}_{timestamp}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: social_post_action
platform: {platform}
mcp_tool: {mcp_tool}
source_file: {approved_file.name}
scheduled_for: {datetime.now().isoformat()}
status: ready_to_post
dry_run: {self.dry_run}
---

# Social Post — Ready to Publish ({platform.title()})

**Source:** {approved_file.name}
**Platform:** {platform.title()}

## Instructions for Claude Code
1. Read the approved post content from: {approved_file}
2. Call MCP tool: `{mcp_tool}` with the post content
3. If DRY_RUN=false -> publish to {platform.title()}
4. If DRY_RUN=true -> log intent only, no real post
5. On success: move source file to /Social/Posted/
6. Log action to /Logs/ via audit_logger
7. Update Dashboard.md social section
8. Move this action file to /Done/
"""
        filepath.write_text(content, encoding='utf-8')
        log_action(
            action_type="social_action_file_created",
            actor="social_watcher",
            target=platform,
            parameters={"source_file": approved_file.name},
            approval_status="approved",
            result="success"
        )
        self.logger.info(f"Social action file created: {filename}")
        return filepath

    def create_weekly_social_summary_task(self):
        """Create task for Claude to generate weekly social media summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SCHEDULED_SocialSummary_{timestamp}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: scheduled_task
task_name: weekly_social_summary
scheduled_for: {datetime.now().isoformat()}
status: pending
---

# Scheduled Task: Weekly Social Media Summary

## Instructions for Claude Code
1. Count all files in /Social/Posted/ created this week (by date)
2. Break down by platform: LinkedIn, Facebook, Instagram, Twitter
3. Note any posts that got manual engagement notes
4. Generate a summary and save to:
   /Social/Social_Summaries/SUMMARY_{datetime.now().strftime('%Y-%m-%d')}.md
5. This summary will be included in the Monday CEO Briefing
6. Move this task file to /Done/
"""
        filepath.write_text(content, encoding='utf-8')
        self.logger.info("Weekly social summary task created")
        return filepath


if __name__ == "__main__":
    watcher = SocialWatcher()
    schedule.every().sunday.at("19:00").do(watcher.create_weekly_social_summary_task)

    watcher.logger.info("Social Watcher running...")
    while True:
        schedule.run_pending()
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
        time.sleep(60)
