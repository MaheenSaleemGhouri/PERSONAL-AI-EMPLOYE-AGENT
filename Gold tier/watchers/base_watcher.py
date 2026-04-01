"""
base_watcher.py — Abstract base class for all AI Employee Watcher scripts.

All watchers follow the same pattern:
1. Poll/watch a source for new items.
2. Create a .md action file in /Needs_Action for each new item.
3. Sleep and repeat.
"""

import time
import logging
import os
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class BaseWatcher(ABC):
    """Abstract base class for all watcher scripts."""

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / "Inbox"
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.logs_dir = self.vault_path / "Logs"
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure required directories exist
        for folder in [self.inbox, self.needs_action, self.done, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return a list of new items to process."""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create a .md file in Needs_Action for the given item."""
        pass

    def log_action(self, action_type: str, description: str, status: str = "success"):
        """Append an action entry to today's log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.md"
        timestamp = datetime.now().isoformat()
        entry = f"- [{timestamp}] [{action_type}] {description} — {status}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)

    def run(self):
        """Main loop: poll for updates on a fixed interval."""
        self.logger.info(f"Starting {self.__class__.__name__} (interval={self.check_interval}s)")
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    path = self.create_action_file(item)
                    self.logger.info(f"Created action file: {path.name}")
                    self.log_action(
                        action_type="file_created",
                        description=f"Action file created: {path.name}",
                    )
            except KeyboardInterrupt:
                self.logger.info("Watcher stopped by user.")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}", exc_info=True)
                self.log_action(
                    action_type="error",
                    description=str(e),
                    status="error",
                )
            time.sleep(self.check_interval)
