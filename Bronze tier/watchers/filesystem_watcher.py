"""
filesystem_watcher.py — File System Drop-Folder Watcher for AI Employee.

Monitors the /Inbox folder for newly dropped files.
When a file appears, it creates a structured .md action file in /Needs_Action
so Claude Code can process it.

Usage:
    python filesystem_watcher.py --vault /path/to/AI_Employee_Vault

Requires:
    pip install watchdog
"""

import argparse
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Ensure base_watcher is importable from the same directory
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


# ---------------------------------------------------------------------------
# Event handler (used by watchdog Observer)
# ---------------------------------------------------------------------------

class DropFolderHandler(FileSystemEventHandler):
    """Handles new file events in the Inbox folder."""

    def __init__(self, watcher: "FileSystemWatcher"):
        super().__init__()
        self.watcher = watcher
        # Track files already processed to avoid duplicate events
        self._processed: set[str] = set()

    def on_created(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        # Skip hidden/temp files (e.g. .DS_Store, ~$tmp)
        if src.name.startswith(".") or src.name.startswith("~"):
            return
        if str(src) in self._processed:
            return
        self._processed.add(str(src))
        self.watcher.handle_new_file(src)


# ---------------------------------------------------------------------------
# Main watcher class
# ---------------------------------------------------------------------------

class FileSystemWatcher(BaseWatcher):
    """
    Watches the /Inbox folder for new files.
    Creates .md action files in /Needs_Action for each new drop.
    """

    def __init__(self, vault_path: str, check_interval: int = 5):
        super().__init__(vault_path, check_interval)
        self.handler = DropFolderHandler(self)
        self.observer = Observer()

    def check_for_updates(self) -> list:
        # Not used in event-driven mode; kept for interface compliance.
        return []

    def create_action_file(self, item: dict) -> Path:
        """
        Create a structured Markdown action file in /Needs_Action.

        item keys:
            source_path: Path  — original file path in /Inbox
            filename: str
            size: int
            detected_at: str (ISO timestamp)
        """
        source_path: Path = item["source_path"]
        filename: str = item["filename"]
        safe_name = filename.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        action_filename = f"FILE_{timestamp}_{safe_name}.md"
        dest_path = self.needs_action / action_filename

        content = f"""---
type: file_drop
original_name: {filename}
source_path: {source_path}
size_bytes: {item.get('size', 'unknown')}
detected_at: {item['detected_at']}
priority: normal
status: pending
---

## New File Dropped

A new file has been placed in the Inbox and requires processing.

- **File:** `{filename}`
- **Size:** {item.get('size', 'unknown')} bytes
- **Detected:** {item['detected_at']}

## Suggested Actions

- [ ] Review the file contents
- [ ] Determine action required (archive / process / escalate)
- [ ] Move original file to appropriate folder
- [ ] Update Dashboard.md
- [ ] Move this action file to /Done when complete
"""

        dest_path.write_text(content, encoding="utf-8")
        return dest_path

    def handle_new_file(self, source: Path):
        """Called by DropFolderHandler when a new file appears in /Inbox."""
        self.logger.info(f"New file detected in Inbox: {source.name}")
        item = {
            "source_path": source,
            "filename": source.name,
            "size": source.stat().st_size if source.exists() else "unknown",
            "detected_at": datetime.now().isoformat(),
        }
        try:
            action_file = self.create_action_file(item)
            self.logger.info(f"Action file created: {action_file.name}")
            self.log_action(
                action_type="file_drop_detected",
                description=f"Inbox file '{source.name}' → action file '{action_file.name}'",
            )
        except Exception as e:
            self.logger.error(f"Failed to create action file for {source.name}: {e}")
            self.log_action(
                action_type="file_drop_error",
                description=f"Failed for '{source.name}': {e}",
                status="error",
            )

    def run(self):
        """Start the watchdog observer on the /Inbox folder."""
        self.logger.info(f"Watching Inbox: {self.inbox}")
        self.observer.schedule(self.handler, str(self.inbox), recursive=False)
        self.observer.start()
        self.logger.info("File System Watcher is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Stopping watcher...")
        finally:
            self.observer.stop()
            self.observer.join()
            self.logger.info("File System Watcher stopped.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AI Employee — File System Drop-Folder Watcher"
    )
    parser.add_argument(
        "--vault",
        default=str(Path(__file__).parent.parent / "AI_Employee_Vault"),
        help="Absolute path to the Obsidian vault (default: ../AI_Employee_Vault)",
    )
    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()
    if not vault_path.exists():
        print(f"ERROR: Vault path does not exist: {vault_path}")
        sys.exit(1)

    watcher = FileSystemWatcher(vault_path=str(vault_path))
    watcher.run()


if __name__ == "__main__":
    main()
