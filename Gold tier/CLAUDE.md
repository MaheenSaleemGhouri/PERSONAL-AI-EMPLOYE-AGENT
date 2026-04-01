# AI Employee — Claude Code Configuration (Gold Tier)

## Project Overview

This is a **Personal AI Employee** built for Hackathon 0 (**Gold Tier**).
Claude Code acts as the reasoning engine, using the Obsidian vault as memory and GUI.
Gold tier adds Odoo accounting, Facebook/Instagram, Twitter/X, Ralph Wiggum loop, and comprehensive audit logging.

## Vault Location

```
AI_Employee_Vault/
```

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              ← Files dropped here by the user or watcher scripts
├── Needs_Action/       ← Items requiring Claude's attention (auto-generated .md files)
├── Pending_Approval/   ← Items that need human review before action
├── Approved/           ← Human-approved items ready for Claude to execute
├── Plans/              ← Claude's reasoning plans for multi-step tasks
├── Done/               ← Completed items (archived)
├── Logs/               ← Daily action logs + audit trail (YYYY-MM-DD.md, audit_trail.jsonl)
├── Accounting/         ← Odoo accounting reports and audit snapshots
├── Dashboard.md        ← Live system overview — READ THIS FIRST
└── Company_Handbook.md ← Rules of engagement — ALWAYS consult before acting
```

## Core Rules

1. **Always read Company_Handbook.md** before making any approval decisions.
2. **Always read Dashboard.md** at the start of a session.
3. **Never delete files** — only move them between folders.
4. **Never take financial actions autonomously** — always create a Pending_Approval file.
5. **Always log actions** to `/Logs/YYYY-MM-DD.md` and the audit trail.
6. **Update Dashboard.md** after processing any items.
7. **Graceful degradation** — if a service is down, skip it and note in the report.

## Available Skills

### Bronze Tier Skills (inherited)

| Skill | Command | Purpose |
|-------|---------|---------|
| Process Inbox | `/process-inbox` | Process all items in /Needs_Action |
| Update Dashboard | `/update-dashboard` | Refresh Dashboard.md with live stats |
| Triage Item | `/triage-item` | Triage a specific item |
| Create Plan | `/create-plan` | Reasoning loop — creates Plan.md |
| Draft LinkedIn Post | `/draft-linkedin-post` | Draft LinkedIn post for approval |
| Review Approvals | `/review-approvals` | Summarise all /Pending_Approval items |
| Approve Item | `/approve-item` | Execute a specific approved action |
| CEO Briefing | `/ceo-briefing` | Generate Monday Morning CEO Briefing |
| Process Gmail | `/process-gmail` | Triage Gmail watcher action files |

### Silver Tier Skills (inherited)

| Skill | Command | Purpose |
|-------|---------|---------|
| Process WhatsApp | `/process-whatsapp` | Triage WhatsApp messages |
| Process LinkedIn | `/process-linkedin` | Triage LinkedIn notifications |
| Publish LinkedIn Post | `/publish-linkedin-post` | Publish approved LinkedIn post |
| Schedule Task | `/schedule-task` | Create scheduled recurring jobs |
| Draft Email Reply | `/draft-email-reply` | Draft email reply for approval |
| Watcher Status | `/watcher-status` | Check watcher health |

### Gold Tier Skills (new)

| Skill | Command | Purpose |
|-------|---------|---------|
| Draft Facebook Post | `/draft-facebook-post` | Draft FB post for approval |
| Publish Facebook Post | `/publish-facebook-post` | Publish approved FB post via Graph API |
| Process Facebook | `/process-facebook` | Triage FB/IG comments and messages |
| Draft Twitter Post | `/draft-twitter-post` | Draft tweet for approval |
| Publish Twitter Post | `/publish-twitter-post` | Publish approved tweet via API v2 |
| Process Twitter | `/process-twitter` | Triage Twitter mentions |
| Social Media Summary | `/social-media-summary` | Cross-platform social metrics report |
| Odoo Accounting Audit | `/odoo-accounting-audit` | Pull Odoo financials into vault |
| Odoo Create Invoice | `/odoo-create-invoice` | Create draft invoice (approval required) |
| Odoo List Partners | `/odoo-list-partners` | List Odoo customers/partners |
| Odoo Health Check | `/odoo-health` | Check if Odoo Docker is running |
| Weekly Business Audit | `/weekly-business-audit` | Full audit: vault + Odoo + social |
| Ralph Wiggum Loop | `/ralph-loop` | Autonomous multi-step task loop |

**Total: 28 Agent Skills** (9 Bronze + 6 Silver + 13 Gold)

## Watcher Scripts

Located in `/watchers/`:

| Script | Monitors | Trigger |
|--------|----------|---------|
| `filesystem_watcher.py` | /Inbox folder | New file dropped |
| `gmail_watcher.py` | Gmail (unread) | New email arrives |
| `whatsapp_watcher.py` | WhatsApp Web | Keyword trigger |
| `linkedin_watcher.py` | LinkedIn notifications | New notification |
| `facebook_watcher.py` | Facebook Page + Instagram | New comment/message |
| `twitter_watcher.py` | Twitter/X mentions | New mention |
| `orchestrator.py` | All of the above | Supervisor |

### Supporting Modules

| Module | Purpose |
|--------|---------|
| `odoo_connector.py` | Odoo JSON-RPC client for accounting |
| `audit_logger.py` | Structured audit logging (JSONL + markdown) |

## Odoo Integration

Odoo 19 Community runs via Docker Compose in the `odoo/` directory.

```bash
cd odoo && docker compose up -d
# Open http://localhost:8069 — see odoo/ODOO_SETUP.md
```

## Starting Everything

```bash
# 1. Start Odoo
cd odoo && docker compose up -d && cd ..

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Fill in .env
cp .env.example .env
# Edit .env with your credentials

# 4. Start all watchers
python watchers/orchestrator.py
```

## Security Notes

- Never put API keys or passwords inside the vault.
- Use `.env` file for all credentials (gitignored).
- Odoo credentials in `.env` — never in vault files.
- See Company_Handbook.md Section 7 for full privacy rules.
