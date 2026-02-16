"""orchestrator.py — Master process that ties everything together"""

import logging
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | ORCHESTRATOR | %(levelname)s | %(message)s",
)
logger = logging.getLogger("Orchestrator")

VAULT_PATH = Path(os.getenv("VAULT_PATH", "../AI_Employee_Vault"))
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE = VAULT_PATH / "Done"


def update_dashboard(message: str):
    """Append a log entry to Dashboard.md"""
    dashboard = VAULT_PATH / "Dashboard.md"
    if dashboard.exists():
        content = dashboard.read_text(encoding="utf-8")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        log_entry = f"\n- [{timestamp}] {message}"
        content = content.replace(
            "<!-- Auto-updated by Claude Code -->",
            f"<!-- Auto-updated by Claude Code -->{log_entry}",
            1,
        )
        dashboard.write_text(content, encoding="utf-8")


def get_pending_files() -> list[Path]:
    """Return list of pending .md files in Needs_Action"""
    return [f for f in NEEDS_ACTION.glob("*.md") if f.name != ".gitkeep"]


def trigger_claude(task_description: str):
    """Trigger Claude Code to process pending tasks"""
    pending = get_pending_files()
    if not pending:
        logger.info("No pending items — Claude not triggered.")
        return

    logger.info(f"Triggering Claude Code — {len(pending)} item(s) pending")

    prompt = f"""
You are a Personal AI Employee. Your vault is at: {VAULT_PATH}

CURRENT TASK: {task_description}

FILES TO PROCESS: {[f.name for f in pending]}

INSTRUCTIONS:
1. Read Company_Handbook.md to understand the rules
2. Read each file in /Needs_Action/
3. For each file, determine the correct action based on handbook rules
4. Create a Plan.md in /Plans/ with checkboxes for next steps
5. Update Dashboard.md with what you found and what you're doing
6. If any action requires approval, create a file in /Pending_Approval/
7. Move processed files to /Done/
8. NEVER send emails or make payments — only draft and request approval

Output <TASK_COMPLETE> when finished.
"""
    logger.info("Prompt prepared for Claude Code")
    logger.info(
        f"To run manually: claude --cwd {VAULT_PATH.resolve()} '<prompt>'"
    )
    # In production: subprocess.run(['claude', '--cwd', str(VAULT_PATH), prompt])


def run_scheduled_check():
    """Main orchestration loop"""
    logger.info("AI Employee Orchestrator started (Bronze Tier)")
    logger.info(f"Vault: {VAULT_PATH}")
    update_dashboard("Orchestrator started")

    while True:
        pending = get_pending_files()
        if pending:
            logger.info(f"{len(pending)} item(s) in Needs_Action")
            trigger_claude("Process all pending items in /Needs_Action/")
        else:
            logger.debug("All clear — no pending items")

        time.sleep(60)


if __name__ == "__main__":
    run_scheduled_check()
