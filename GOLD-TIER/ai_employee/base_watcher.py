"""base_watcher.py — Abstract base class for all Watchers"""

import time
import logging
import os
from pathlib import Path
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("watcher.log"),
    ],
)


class BaseWatcher(ABC):
    def __init__(self, vault_path: str = None, check_interval: int = 60):
        self.vault_path = Path(
            vault_path or os.getenv("VAULT_PATH", "../AI_Employee_Vault")
        )
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.inbox = self.vault_path / "Inbox"
        self.check_interval = check_interval
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure required folders exist
        for folder in [self.needs_action, self.done, self.inbox]:
            folder.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            self.logger.warning("DRY RUN MODE — No real actions will be taken")

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        self.logger.info(
            f"Starting {self.__class__.__name__} (interval: {self.check_interval}s)"
        )
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f"Action file created: {filepath.name}")
            except KeyboardInterrupt:
                self.logger.info("Watcher stopped by user.")
                break
            except Exception as e:
                self.logger.error(f"Error in watcher loop: {e}", exc_info=True)
            time.sleep(self.check_interval)
