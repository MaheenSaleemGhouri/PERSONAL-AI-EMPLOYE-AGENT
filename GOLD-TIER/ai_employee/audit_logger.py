# audit_logger.py — Centralized JSON audit logging for every AI action
# Every single action the AI takes must pass through this logger

import json
import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
LOGS_DIR = VAULT_PATH / 'Logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

RETENTION_DAYS = int(os.getenv('AUDIT_LOG_RETENTION_DAYS', '90'))

logger = logging.getLogger("AuditLogger")


def log_action(
    action_type: str,
    actor: str,
    target: str,
    parameters: dict,
    approval_status: str,
    result: str,
    error: str = None
) -> dict:
    """
    Log every AI action to a daily JSON file in /Logs/.

    Required for Gold Tier — every single action must be logged.
    Never log credentials, passwords, or sensitive personal data.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action_type": action_type,
        "actor": actor,
        "target": target,
        "parameters": _sanitize(parameters),
        "approval_status": approval_status,
        "result": result,
        "error": error
    }

    # Write to daily log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"{today}.json"

    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            existing = []

    existing.append(log_entry)
    log_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding='utf-8')

    logger.info(f"Logged: {action_type} | {actor} -> {target} | {result}")
    return log_entry


def _sanitize(params: dict) -> dict:
    """Remove sensitive keys from parameters before logging"""
    sensitive_keys = {'password', 'token', 'secret', 'api_key', 'credential', 'auth'}
    return {
        k: '***REDACTED***' if any(s in k.lower() for s in sensitive_keys) else v
        for k, v in params.items()
    }


def cleanup_old_logs():
    """Delete log files older than RETENTION_DAYS"""
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted = 0
    for log_file in LOGS_DIR.glob("*.json"):
        try:
            file_date = datetime.strptime(log_file.stem, '%Y-%m-%d')
            if file_date < cutoff:
                log_file.unlink()
                deleted += 1
        except ValueError:
            continue
    if deleted:
        logger.info(f"Cleaned up {deleted} old log file(s)")


def get_todays_summary() -> dict:
    """Return a summary of today's logged actions"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"{today}.json"

    if not log_file.exists():
        return {"total": 0, "errors": 0, "actions": []}

    entries = json.loads(log_file.read_text(encoding='utf-8'))
    return {
        "total": len(entries),
        "errors": sum(1 for e in entries if e.get("result") == "error"),
        "action_types": list(set(e["action_type"] for e in entries))
    }
