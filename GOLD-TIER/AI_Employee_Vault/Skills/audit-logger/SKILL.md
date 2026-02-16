---
skill_name: audit-logger
version: 1.0
tier: gold
trigger: After every action Claude Code takes — mandatory
---

# Skill: Audit Logger

## Purpose
Log every single AI action to a daily JSON file for a complete audit trail.

## When to Use
After EVERY action — no exceptions. This is mandatory at Gold Tier.

## Log File Location
/Logs/YYYY-MM-DD.json

## Required Log Entry Fields
```json
{
  "timestamp": "ISO 8601 UTC",
  "action_type": "email_send | linkedin_post | odoo_create | facebook_post | ...",
  "actor": "claude_code | gmail_watcher | odoo_watcher | scheduler | ...",
  "target": "who or what was acted upon",
  "parameters": { "key": "value — NO credentials or passwords" },
  "approval_status": "approved | auto_approved | pending | rejected",
  "result": "success | error | dry_run",
  "error": "error message if result is error, else null"
}
```

## Rules
- NEVER log passwords, API keys, tokens, or personal credentials
- Use audit_logger.py's `log_action()` function — do not write logs manually
- If logging itself fails: write a plain text error to /Logs/logging_errors.txt
- Retain logs for 90 days minimum — cleanup_old_logs() runs weekly
