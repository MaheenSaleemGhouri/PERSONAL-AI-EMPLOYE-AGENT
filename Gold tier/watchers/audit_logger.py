"""
audit_logger.py — Comprehensive Audit Logging for AI Employee (Gold Tier)

Provides structured, append-only audit logging for all AI Employee actions.
Every skill, watcher, and automated action should log through this module
to maintain a complete audit trail.

Usage:
    from audit_logger import AuditLogger

    logger = AuditLogger("AI_Employee_Vault")
    logger.log_action("FACEBOOK_POST", "Published post to Facebook", status="success", metadata={"post_id": "123"})
    logger.log_error("ODOO", "Connection refused", severity="warning")
    logger.log_approval("invoice_001.md", "approved", approved_by="human")
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("AuditLogger")


class AuditLogger:
    """Structured audit logger that writes to the vault's /Logs/ directory."""

    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.logs_dir = self.vault / "Logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.audit_json = self.logs_dir / "audit_trail.jsonl"

    def _daily_log_path(self) -> Path:
        return self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"

    def _append_markdown(self, entry: str):
        """Append a line to today's markdown log."""
        log_file = self._daily_log_path()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def _append_jsonl(self, record: dict):
        """Append a structured JSON record to the audit trail."""
        record["timestamp"] = datetime.now().isoformat()
        with open(self.audit_json, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    # ── Public API ───────────────────────────────────────────────

    def log_action(
        self,
        category: str,
        description: str,
        status: str = "success",
        metadata: dict | None = None,
    ):
        """Log a completed action (skill execution, post, email, etc.)."""
        now = datetime.now().strftime("%H:%M:%S")
        md_entry = f"[{now}] [{category}] {description} — Status: {status}"
        self._append_markdown(md_entry)
        self._append_jsonl({
            "type": "action",
            "category": category,
            "description": description,
            "status": status,
            "metadata": metadata or {},
        })
        logger.info(f"AUDIT: {md_entry}")

    def log_error(
        self,
        category: str,
        error_message: str,
        severity: str = "error",
        metadata: dict | None = None,
    ):
        """Log an error or warning."""
        now = datetime.now().strftime("%H:%M:%S")
        md_entry = f"[{now}] [{category}] [{severity.upper()}] {error_message}"
        self._append_markdown(md_entry)
        self._append_jsonl({
            "type": "error",
            "category": category,
            "severity": severity,
            "error": error_message,
            "metadata": metadata or {},
        })
        logger.warning(f"AUDIT ERROR: {md_entry}")

    def log_approval(
        self,
        filename: str,
        decision: str,
        approved_by: str = "human",
        metadata: dict | None = None,
    ):
        """Log an approval/rejection decision."""
        now = datetime.now().strftime("%H:%M:%S")
        md_entry = f"[{now}] [APPROVAL] {filename} — {decision} by {approved_by}"
        self._append_markdown(md_entry)
        self._append_jsonl({
            "type": "approval",
            "filename": filename,
            "decision": decision,
            "approved_by": approved_by,
            "metadata": metadata or {},
        })

    def log_watcher_event(
        self,
        watcher_name: str,
        event: str,
        items_found: int = 0,
    ):
        """Log a watcher check cycle."""
        self._append_jsonl({
            "type": "watcher_event",
            "watcher": watcher_name,
            "event": event,
            "items_found": items_found,
        })

    def log_ralph_iteration(
        self,
        iteration: int,
        max_iterations: int,
        status: str,
        reason: str,
    ):
        """Log a Ralph Wiggum loop iteration."""
        now = datetime.now().strftime("%H:%M:%S")
        md_entry = f"[{now}] [RALPH] Iteration {iteration}/{max_iterations} — {status}: {reason}"
        self._append_markdown(md_entry)
        self._append_jsonl({
            "type": "ralph_wiggum",
            "iteration": iteration,
            "max_iterations": max_iterations,
            "status": status,
            "reason": reason,
        })

    # ── Reporting ────────────────────────────────────────────────

    def get_recent_entries(self, hours: int = 24, entry_type: str | None = None) -> list[dict]:
        """Read recent audit trail entries from the JSONL file."""
        if not self.audit_json.exists():
            return []

        entries = []
        cutoff = datetime.now().timestamp() - (hours * 3600)

        for line in self.audit_json.read_text(encoding="utf-8").strip().split("\n"):
            if not line:
                continue
            try:
                record = json.loads(line)
                ts = datetime.fromisoformat(record["timestamp"]).timestamp()
                if ts >= cutoff:
                    if entry_type is None or record.get("type") == entry_type:
                        entries.append(record)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
        return entries

    def get_error_summary(self, hours: int = 24) -> dict:
        """Get a summary of recent errors for health reporting."""
        errors = self.get_recent_entries(hours=hours, entry_type="error")
        by_category: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for e in errors:
            cat = e.get("category", "unknown")
            sev = e.get("severity", "error")
            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {
            "total_errors": len(errors),
            "by_category": by_category,
            "by_severity": by_severity,
        }
