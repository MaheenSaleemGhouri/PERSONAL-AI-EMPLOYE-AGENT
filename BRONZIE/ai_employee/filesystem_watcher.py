"""filesystem_watcher.py — Monitors /Inbox for dropped files"""

import shutil
import time
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, watcher_instance):
        self.watcher = watcher_instance

    def _should_ignore(self, path: Path) -> bool:
        return path.name.startswith(".") or path.suffix == ".md" or ".tmp." in path.name

    def on_created(self, event):
        if event.is_directory:
            return
        source = Path(event.src_path)
        if self._should_ignore(source):
            return
        time.sleep(1)
        if not source.exists():
            return
        self.watcher.logger.info(f"New file detected: {source.name}")
        self.watcher.process_dropped_file(source)

    def on_moved(self, event):
        if event.is_directory:
            return
        dest = Path(event.dest_path)
        if self._should_ignore(dest):
            return
        # Handle temp file rename to final file
        self.watcher.logger.info(f"New file detected (moved): {dest.name}")
        self.watcher.process_dropped_file(dest)


class FileSystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str = None):
        super().__init__(vault_path, check_interval=10)
        self.observer = Observer()

    def check_for_updates(self) -> list:
        # Handled by watchdog event handler
        return []

    def create_action_file(self, item) -> Path:
        pass  # Handled in process_dropped_file

    def process_dropped_file(self, source: Path) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_name = f"FILE_{timestamp}_{source.name}"
        dest = self.needs_action / dest_name

        if not self.dry_run:
            shutil.copy2(source, dest)
        else:
            self.logger.info(f"[DRY RUN] Would copy {source.name} -> Needs_Action/")

        # Always create the metadata .md file
        meta_path = self.needs_action / f"FILE_{timestamp}_{source.stem}.md"
        file_size = source.stat().st_size if source.exists() else "unknown"
        now_iso = datetime.now().isoformat()
        now_fmt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        meta_content = f"""---
type: file_drop
original_name: "{source.name}"
file_path: "{dest_name}"
size_bytes: {file_size}
received: {now_iso}
status: pending
priority: normal
dry_run: {self.dry_run}
---

# New File Received: `{source.name}`

## Details
- **Original Path**: `{source}`
- **Received At**: {now_fmt}
- **File Size**: {file_size} bytes

## Suggested Actions
- [ ] Review file contents
- [ ] Categorize and tag
- [ ] Move to appropriate folder
- [ ] Update Dashboard.md

## Claude Code Instructions
Read this file, determine what action to take based on Company_Handbook.md rules,
create a Plan.md in /Plans/, and update Dashboard.md.
"""
        meta_path.write_text(meta_content, encoding="utf-8")
        self.logger.info(f"Metadata file created: {meta_path.name}")
        return meta_path

    def run(self):
        handler = DropFolderHandler(self)
        self.observer.schedule(handler, str(self.inbox), recursive=False)
        self.observer.start()
        self.logger.info(f"Watching folder: {self.inbox}")
        self.logger.info("Drop files into the /Inbox folder to trigger processing.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            self.logger.info("File watcher stopped.")
        self.observer.join()


if __name__ == "__main__":
    watcher = FileSystemWatcher()
    watcher.run()
