"""
orchestrator.py — Master Watcher Orchestrator for AI Employee (Gold Tier)

Launches and supervises all watcher processes including Facebook and Twitter.
Acts as a watchdog: if a watcher crashes, it restarts automatically.
Writes status to the vault Dashboard.

Usage:
    python watchers/orchestrator.py --vault AI_Employee_Vault
    python watchers/orchestrator.py --vault AI_Employee_Vault --watchers filesystem gmail facebook twitter
    python watchers/orchestrator.py --vault AI_Employee_Vault --dry-run

Environment variables (.env):
    VAULT_PATH=./AI_Employee_Vault
    GMAIL_CREDS=./credentials.json
    WHATSAPP_PROFILE=./whatsapp_profile
    LINKEDIN_PROFILE=./linkedin_profile
    DRY_RUN=false
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("Orchestrator")

WATCHERS_DIR = Path(__file__).parent
RESTART_DELAY = 10
MAX_RESTARTS = 5
RESTART_WINDOW = 300


def build_watcher_commands(
    vault: str,
    gmail_creds: str,
    whatsapp_profile: str,
    linkedin_profile: str,
) -> dict:
    return {
        "filesystem": {
            "cmd": [sys.executable, str(WATCHERS_DIR / "filesystem_watcher.py"), "--vault", vault],
            "description": "File System Drop-Folder Watcher",
        },
        "gmail": {
            "cmd": [
                sys.executable, str(WATCHERS_DIR / "gmail_watcher.py"),
                "--vault", vault, "--creds", gmail_creds, "--interval", "120",
            ],
            "description": "Gmail Watcher (OAuth2)",
        },
        "whatsapp": {
            "cmd": [
                sys.executable, str(WATCHERS_DIR / "whatsapp_watcher.py"),
                "--vault", vault, "--profile", whatsapp_profile, "--interval", "60",
            ],
            "description": "WhatsApp Web Watcher (Playwright)",
        },
        "linkedin": {
            "cmd": [
                sys.executable, str(WATCHERS_DIR / "linkedin_watcher.py"),
                "--vault", vault, "--profile", linkedin_profile, "--interval", "300",
            ],
            "description": "LinkedIn Watcher (Playwright)",
        },
        "facebook": {
            "cmd": [
                sys.executable, str(WATCHERS_DIR / "facebook_watcher.py"),
                "--vault", vault, "--interval", "120",
            ],
            "description": "Facebook & Instagram Watcher (Graph API)",
        },
        "twitter": {
            "cmd": [
                sys.executable, str(WATCHERS_DIR / "twitter_watcher.py"),
                "--vault", vault, "--interval", "120",
            ],
            "description": "Twitter/X Watcher (API v2)",
        },
    }


class WatcherProcess:
    def __init__(self, name: str, cmd: list[str], description: str):
        self.name = name
        self.cmd = cmd
        self.description = description
        self.process: subprocess.Popen | None = None
        self.start_times: list[float] = []
        self.error_count: int = 0

    def start(self) -> None:
        logger.info(f"Starting {self.name}: {self.description}")
        try:
            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self.start_times.append(time.time())
            now = time.time()
            self.start_times = [t for t in self.start_times if now - t < RESTART_WINDOW]
            logger.info(f"{self.name} started (PID {self.process.pid})")
        except Exception as e:
            self.error_count += 1
            logger.error(f"Failed to start {self.name}: {e}")

    def is_alive(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            logger.info(f"Stopping {self.name} (PID {self.process.pid})")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def has_exceeded_restart_limit(self) -> bool:
        now = time.time()
        recent = [t for t in self.start_times if now - t < RESTART_WINDOW]
        return len(recent) >= MAX_RESTARTS

    @property
    def status(self) -> str:
        if self.process is None:
            return "stopped"
        rc = self.process.poll()
        if rc is None:
            return "running"
        return f"exited({rc})"

    @property
    def pid(self) -> int | None:
        return self.process.pid if self.process else None


def write_status_to_vault(vault_path: Path, watchers: dict[str, WatcherProcess]) -> None:
    status_file = vault_path / "watcher_status.json"
    data = {
        "updated_at": datetime.now().isoformat(),
        "tier": "gold",
        "watchers": {
            name: {
                "status": wp.status,
                "pid": wp.pid,
                "description": wp.description,
                "error_count": wp.error_count,
                "recent_starts": len([
                    t for t in wp.start_times if time.time() - t < RESTART_WINDOW
                ]),
            }
            for name, wp in watchers.items()
        },
    }
    status_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_orchestrator(
    vault: str,
    enabled_watchers: list[str],
    gmail_creds: str,
    whatsapp_profile: str,
    linkedin_profile: str,
    dry_run: bool = False,
) -> None:
    vault_path = Path(vault)
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)

    all_commands = build_watcher_commands(vault, gmail_creds, whatsapp_profile, linkedin_profile)
    watchers: dict[str, WatcherProcess] = {}

    for name in enabled_watchers:
        if name not in all_commands:
            logger.warning(f"Unknown watcher '{name}' — skipping.")
            continue
        cfg = all_commands[name]
        watchers[name] = WatcherProcess(name, cfg["cmd"], cfg["description"])

    if not watchers:
        logger.error("No valid watchers configured. Exiting.")
        sys.exit(1)

    shutdown = {"requested": False}

    def handle_signal(sig, frame):
        logger.info("Shutdown signal received — stopping all watchers...")
        shutdown["requested"] = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if dry_run:
        logger.info("[DRY RUN] Would start the following watchers:")
        for name, wp in watchers.items():
            logger.info(f"  {name}: {' '.join(wp.cmd)}")
        return

    for wp in watchers.values():
        wp.start()

    logger.info(f"Gold Tier Orchestrator running — supervising {len(watchers)} watcher(s). Ctrl+C to stop.")

    while not shutdown["requested"]:
        for name, wp in watchers.items():
            if not wp.is_alive():
                if wp.has_exceeded_restart_limit():
                    logger.error(
                        f"{name} crashed {MAX_RESTARTS}+ times in {RESTART_WINDOW}s — giving up."
                    )
                    continue
                rc = wp.process.poll() if wp.process else "N/A"
                logger.warning(f"{name} exited (code {rc}). Restarting in {RESTART_DELAY}s...")
                time.sleep(RESTART_DELAY)
                wp.start()

        write_status_to_vault(vault_path, watchers)
        time.sleep(15)

    for wp in watchers.values():
        wp.stop()

    logger.info("All watchers stopped. Orchestrator exiting.")


def main():
    parser = argparse.ArgumentParser(
        description="Gold Tier Orchestrator — launch and supervise all AI Employee watchers"
    )
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "AI_Employee_Vault"))
    parser.add_argument(
        "--watchers", nargs="+",
        default=["filesystem", "gmail", "linkedin", "facebook", "twitter"],
        choices=["filesystem", "gmail", "whatsapp", "linkedin", "facebook", "twitter"],
    )
    parser.add_argument("--gmail-creds", default=os.getenv("GMAIL_CREDS", "credentials.json"))
    parser.add_argument("--whatsapp-profile", default=os.getenv("WHATSAPP_PROFILE", "./whatsapp_profile"))
    parser.add_argument("--linkedin-profile", default=os.getenv("LINKEDIN_PROFILE", "./linkedin_profile"))
    parser.add_argument("--dry-run", action="store_true", default=os.getenv("DRY_RUN", "false").lower() == "true")
    args = parser.parse_args()

    run_orchestrator(
        vault=args.vault,
        enabled_watchers=args.watchers,
        gmail_creds=args.gmail_creds,
        whatsapp_profile=args.whatsapp_profile,
        linkedin_profile=args.linkedin_profile,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
