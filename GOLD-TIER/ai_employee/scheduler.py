# scheduler.py — Cron-based scheduling for daily briefings and recurring tasks
# Runs independently alongside the watchers

import schedule
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | SCHEDULER | %(levelname)s | %(message)s'
)
logger = logging.getLogger("Scheduler")

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
NEEDS_ACTION = VAULT_PATH / 'Needs_Action'
SCHEDULING_DIR = VAULT_PATH / 'Scheduling'
SCHEDULING_DIR.mkdir(parents=True, exist_ok=True)

QUIET_START = int(os.getenv('QUIET_HOURS_START', '23:00').split(':')[0])
QUIET_END = int(os.getenv('QUIET_HOURS_END', '07:00').split(':')[0])


def is_quiet_hours() -> bool:
    """Return True if the current time falls within the quiet hours window"""
    hour = datetime.now().hour
    if QUIET_START > QUIET_END:  # Wraps midnight (e.g. 23:00 → 07:00)
        return hour >= QUIET_START or hour < QUIET_END
    return QUIET_START <= hour < QUIET_END


def log_task(task_name: str, status: str):
    """Append a log entry to the scheduled_tasks.md file"""
    log_file = SCHEDULING_DIR / 'scheduled_tasks.md'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f"| {task_name} | {timestamp} | {status} |\n"

    if not log_file.exists():
        log_file.write_text(
            "# Scheduled Tasks Log\n\n"
            "| Task | Timestamp | Status |\n"
            "|------|-----------|--------|\n",
            encoding='utf-8'
        )
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(entry)


def create_daily_briefing_task():
    """Create a daily briefing task file in /Needs_Action/"""
    if is_quiet_hours():
        logger.info("🌙 Quiet hours — daily briefing skipped")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = NEEDS_ACTION / f"SCHEDULED_DailyBriefing_{timestamp}.md"

    content = f"""---
type: scheduled_task
task_name: daily_briefing
scheduled_for: {datetime.now().isoformat()}
status: pending
---

# 📋 Scheduled Task: Daily Briefing

**Triggered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Instructions for Claude Code
1. Read Dashboard.md to understand the current system status
2. Count all files in /Needs_Action/ (pending items)
3. Check /Pending_Approval/ — count and list pending approvals
4. Check /Logs/ for a summary of yesterday's completed actions
5. Update Dashboard.md with:
   - Total pending items today
   - Items requiring urgent attention
   - Any approvals overdue by more than 24 hours → add an ALERT section
   - A one-line overall system health summary
6. Move this task file to /Done/ when complete
"""
    filepath.write_text(content, encoding='utf-8')
    logger.info("📋 Daily briefing task created")
    log_task("Daily Briefing", "✅ Created")


def create_weekly_audit_task():
    """Create the weekly business audit task every Sunday evening"""
    if is_quiet_hours():
        return
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = NEEDS_ACTION / f"SCHEDULED_WeeklyAudit_{timestamp}.md"
    content = f"""---
type: scheduled_task
task_name: weekly_ceo_briefing_audit
scheduled_for: {datetime.now().isoformat()}
status: pending
---

# Scheduled Task: Weekly Business Audit + CEO Briefing

**Triggered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Instructions for Claude Code
Follow the template in /Audit/Weekly_Audit_Template.md exactly.

1. Read Business_Goals.md — monthly targets and KPIs
2. Read all /Done/ files created this week — categorize by type
3. Read /Accounting/Current_Month.md — revenue, expenses, flagged items
4. Read /Social/Social_Summaries/ for this week's social summary
5. Read /Logs/ for this week — count errors and notable events
6. Check /Pending_Approval/ for overdue approvals (>24h)
7. Generate CEO Briefing -> save to:
   /Briefings/{datetime.now().strftime('%Y-%m-%d')}_Monday_Briefing.md
8. Update Dashboard.md Gold section with latest numbers
9. Log the audit action via audit_logger
10. Move this task file to /Done/
"""
    filepath.write_text(content, encoding='utf-8')
    logger.info("Weekly audit task created")
    log_task("Weekly Audit", "Created")


def run_scheduler():
    """Configure and start the scheduler"""
    briefing_time = os.getenv('DAILY_BRIEFING_TIME', '08:00')
    post_days = os.getenv('LINKEDIN_POST_DAYS', 'monday,wednesday,friday').split(',')
    post_time = os.getenv('LINKEDIN_POST_TIME', '10:00')

    # Schedule daily briefing
    schedule.every().day.at(briefing_time).do(create_daily_briefing_task)
    logger.info(f"Daily briefing scheduled at {briefing_time}")

    # Gold Tier — Weekly audit schedule
    audit_day = os.getenv('WEEKLY_AUDIT_DAY', 'sunday')
    audit_time = os.getenv('WEEKLY_AUDIT_TIME', '20:00')
    getattr(schedule.every(), audit_day).at(audit_time).do(create_weekly_audit_task)
    logger.info(f"Weekly audit scheduled: {audit_day} at {audit_time}")

    # Write cron config file to vault
    config_file = SCHEDULING_DIR / 'cron_config.md'
    config_file.write_text(f"""---
last_updated: {datetime.now().isoformat()}
tier: gold
---

# Scheduling Configuration

| Task              | Schedule                      | Time        | Status    |
|-------------------|-------------------------------|-------------|-----------|
| Daily Briefing    | Every day                     | {briefing_time}     | Active |
| LinkedIn Draft    | {', '.join(post_days)}  | {post_time}     | Active |
| WhatsApp Check    | Every 30 seconds              | Ongoing     | Active |
| Gmail Check       | Every 2 minutes               | Ongoing     | Active |
| Weekly Audit      | {audit_day}                   | {audit_time}     | Active |

## Quiet Hours Policy
- No scheduled task files are created between {QUIET_START}:00 and {QUIET_END}:00
- Watchers continue to run during quiet hours (read-only monitoring, no action files)
""", encoding='utf-8')

    logger.info("Scheduler is running...")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    run_scheduler()
