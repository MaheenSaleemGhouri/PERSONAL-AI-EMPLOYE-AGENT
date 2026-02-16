# error_handler.py — Retry logic and graceful degradation for all Gold Tier scripts

import time
import logging
import functools
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ErrorHandler")

MAX_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', '3'))
BASE_DELAY = int(os.getenv('RETRY_BASE_DELAY_SECONDS', '1'))
VAULT_PATH = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))


class TransientError(Exception):
    """Errors that are safe to retry (network timeouts, API rate limits)"""
    pass


class PermanentError(Exception):
    """Errors that should NOT be retried (auth failure, invalid data)"""
    pass


def with_retry(max_attempts: int = MAX_ATTEMPTS, base_delay: int = BASE_DELAY, max_delay: int = 60):
    """
    Decorator for automatic retry with exponential backoff.
    Use on any function that makes external API calls.

    Usage:
        @with_retry(max_attempts=3, base_delay=1)
        def call_odoo_api():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except PermanentError as e:
                    logger.error(f"Permanent error in {func.__name__}: {e} — not retrying")
                    alert_dashboard(f"PERMANENT ERROR in {func.__name__}: {e}")
                    raise
                except Exception as e:
                    last_error = e
                    if attempt == max_attempts - 1:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
                        alert_dashboard(f"FAILED after {max_attempts} retries: {func.__name__} — {e}")
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e} — retrying in {delay}s")
                    time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


def alert_dashboard(message: str):
    """Write an ALERT to Dashboard.md so the human sees it"""
    dashboard = VAULT_PATH / 'Dashboard.md'
    if not dashboard.exists():
        return
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    alert_line = f"\n- [{timestamp}] ALERT: {message}"
    content = dashboard.read_text(encoding='utf-8')
    if '## Alerts' in content:
        content = content.replace(
            '## Alerts\n<!-- Auto-updated on critical events -->\n- None',
            f'## Alerts\n<!-- Auto-updated on critical events -->{alert_line}'
        )
    else:
        content += f"\n\n## Alerts{alert_line}"
    dashboard.write_text(content, encoding='utf-8')


def graceful_degradation(component: str, fallback_message: str):
    """
    Log a degradation event when a component fails.
    System continues running — just without that component.
    """
    logger.warning(f"{component} degraded — {fallback_message}")
    alert_dashboard(f"{component} is unavailable: {fallback_message}. Other components continue.")
