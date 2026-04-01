# AI Employee — Claude Code Configuration

## Project Overview

This is a **Personal AI Employee** built for the Hackathon 0 (Silver Tier).
Claude Code acts as the reasoning engine, using the Obsidian vault as memory and GUI.

## Vault Location

```
C:\Hackathon 0\AI_Employee_Vault\
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
├── Logs/               ← Daily action logs (YYYY-MM-DD.md)
├── Dashboard.md        ← Live system overview — READ THIS FIRST
└── Company_Handbook.md ← Rules of engagement — ALWAYS consult before acting
```

## Core Rules

1. **Always read Company_Handbook.md** before making any approval decisions.
2. **Always read Dashboard.md** at the start of a session to understand current state.
3. **Never delete files** — only move them between folders.
4. **Never take financial actions autonomously** — always create a Pending_Approval file.
5. **Always log actions** to `/Logs/YYYY-MM-DD.md`.
6. **Update Dashboard.md** after processing any items.

## Available Skills

### Bronze Tier Skills

| Skill               | Command                 | Purpose                                          |
|---------------------|-------------------------|--------------------------------------------------|
| Process Inbox       | `/process-inbox`        | Process all items in /Needs_Action               |
| Update Dashboard    | `/update-dashboard`     | Refresh Dashboard.md with live stats             |
| Triage Item         | `/triage-item`          | Triage a specific item                           |
| Create Plan         | `/create-plan`          | Reasoning loop — creates Plan.md for complex tasks |
| Draft LinkedIn Post | `/draft-linkedin-post`  | Draft LinkedIn post and queue for approval       |
| Review Approvals    | `/review-approvals`     | Summarise all items in /Pending_Approval         |
| Approve Item        | `/approve-item`         | Execute a specific approved action               |
| CEO Briefing        | `/ceo-briefing`         | Generate Monday Morning CEO Briefing             |
| Process Gmail       | `/process-gmail`        | Triage Gmail watcher action files                |

### Silver Tier Skills

| Skill                  | Command                    | Purpose                                              |
|------------------------|----------------------------|------------------------------------------------------|
| Process WhatsApp       | `/process-whatsapp`        | Triage WhatsApp keyword-triggered messages           |
| Process LinkedIn       | `/process-linkedin`        | Triage LinkedIn notification action files            |
| Publish LinkedIn Post  | `/publish-linkedin-post`   | Execute approved LinkedIn post via Playwright        |
| Schedule Task          | `/schedule-task`           | Create cron/Task Scheduler entries for recurring jobs |
| Draft Email Reply      | `/draft-email-reply`       | Draft email reply and queue for approval             |
| Watcher Status         | `/watcher-status`          | Check health of all running watcher scripts          |

## Watcher Scripts

Located in `/watchers/`:

| Script                    | Monitors                        | Trigger                              |
|---------------------------|---------------------------------|--------------------------------------|
| `filesystem_watcher.py`   | /Inbox folder                   | New file dropped                     |
| `gmail_watcher.py`        | Gmail (unread)                  | New email arrives                    |
| `linkedin_watcher.py`     | LinkedIn notifications + /Approved/ | New notification OR approved post |
| `whatsapp_watcher.py`     | WhatsApp Web                    | Keyword trigger in message           |
| `orchestrator.py`         | All of the above                | Supervisor — auto-restarts on crash  |

### First-Time Setup

```bash
# 1. Install all dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Fill in credentials.json (Gmail) — see GMAIL_SETUP.md for instructions
# 3. Copy env template
cp .env.example .env

# 4. First-time LinkedIn session setup (opens browser → sign in)
python watchers/linkedin_watcher.py --setup

# 5. First-time WhatsApp session setup (opens browser → scan QR)
python watchers/whatsapp_watcher.py --setup
```

### Starting the Watchers

```bash
# Run all watchers via orchestrator (recommended)
python watchers/orchestrator.py

# Or run individually:
python watchers/filesystem_watcher.py
python watchers/gmail_watcher.py          # Gmail OAuth — credentials.json required
python watchers/linkedin_watcher.py       # LinkedIn Playwright — setup first
python watchers/whatsapp_watcher.py       # WhatsApp Playwright — setup first
```

## Typical Workflow

1. Complete one-time setup (see above)
2. Start all watchers: `python watchers/orchestrator.py`
3. Watchers detect new items → create `.md` files in `/Needs_Action/`
4. Triage items:
   - `/process-gmail` — for email action files
   - `/process-linkedin` — for LinkedIn notification files
   - `/process-whatsapp` — for WhatsApp message files
   - `/process-inbox` — for filesystem-dropped files
5. Complex tasks → Claude runs `/create-plan` → produces Plan.md
6. Sensitive actions → Claude creates files in `/Pending_Approval/`
7. Review: `/review-approvals` — see what needs your decision
8. Approve: `/approve-item <filename>` — execute approved actions
9. LinkedIn posts: `/draft-linkedin-post` → move to /Approved/ → LinkedIn watcher publishes
10. Email replies: `/draft-email-reply <file>` → approve → `/approve-item` sends
11. Check watcher health: `/watcher-status`
12. Schedule recurring jobs: `/schedule-task <skill> <schedule>`
13. Every Monday: `/ceo-briefing` for a business status report
14. Refresh dashboard: `/update-dashboard`

## Security Notes

- Never put API keys or passwords inside the vault.
- Use `.env` file for credentials (it is gitignored).
- See Company_Handbook.md Section 7 for full privacy rules.
