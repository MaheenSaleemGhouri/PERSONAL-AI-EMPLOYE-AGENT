# Personal AI Employee — Silver Tier

**Hackathon 0: Building Autonomous FTEs in 2026**

A local-first, agent-driven AI Employee powered by **Claude Code** and **Obsidian**.

---

## What This Is

A **Silver Tier** implementation of the Personal AI Employee architecture. It gives you:

- An **Obsidian vault** as the AI's memory and dashboard
- **Three Watcher scripts** (Filesystem, Gmail, WhatsApp) running via an Orchestrator
- **14 Agent Skills** for Claude to process, triage, draft, publish, and schedule
- A structured **folder workflow** (Inbox → Needs_Action → Pending_Approval → Approved → Done)
- **Human-in-the-loop** approval workflow for all sensitive actions
- **LinkedIn auto-posting** (draft → approve → publish via Playwright)
- **Scheduling** support via Windows Task Scheduler / cron

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Open the vault in Obsidian

Open Obsidian and add `AI_Employee_Vault/` as a vault. You'll see:
- `Dashboard.md` — live overview
- `Company_Handbook.md` — AI rules of engagement

### 3. Set up Gmail (first time only)

1. Go to [Google Cloud Console](https://console.cloud.google.com) → Create Project → Enable Gmail API
2. Create OAuth 2.0 Desktop credentials → download as `credentials.json` into this folder
3. On first run the browser opens — sign in and grant access → token saved automatically

### 4. Set up WhatsApp (first time only)

```bash
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault --setup
```
Scan the QR code in the browser. Session is saved for future headless runs.

### 5. Start all watchers via the Orchestrator

```bash
python watchers/orchestrator.py --vault AI_Employee_Vault
```

Or start individual watchers:
```bash
python watchers/filesystem_watcher.py --vault AI_Employee_Vault
python watchers/gmail_watcher.py --vault AI_Employee_Vault
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault
```

### 6. Run Claude Code from the project directory

```bash
claude
```

---

## Silver Tier Skills

### Bronze Skills (inherited)

| Command             | Purpose                               |
|---------------------|---------------------------------------|
| `/process-inbox`    | Process all items in /Needs_Action    |
| `/update-dashboard` | Refresh Dashboard.md with live stats  |
| `/triage-item`      | Triage a specific item                |
| `/create-plan`      | Create a Plan.md for complex tasks    |
| `/draft-linkedin-post` | Draft LinkedIn post for approval   |
| `/review-approvals` | Summarise all /Pending_Approval items |
| `/approve-item`     | Execute a specific approved action    |
| `/ceo-briefing`     | Monday Morning CEO Briefing           |
| `/process-gmail`    | Triage Gmail watcher action files     |

### Silver Skills (new)

| Command                   | Purpose                                              |
|---------------------------|------------------------------------------------------|
| `/process-whatsapp`       | Triage WhatsApp keyword-triggered messages           |
| `/publish-linkedin-post`  | Execute approved LinkedIn post via Playwright        |
| `/schedule-task`          | Create cron/Task Scheduler entries for recurring jobs |
| `/draft-email-reply`      | Draft email reply and queue for approval             |
| `/watcher-status`         | Check health of all running watcher scripts          |

---

## Project Structure

```
Silver tier/
├── AI_Employee_Vault/             ← Obsidian vault (the AI's brain)
│   ├── Inbox/                     ← Drop files here
│   ├── Needs_Action/              ← Auto-generated action items
│   ├── Pending_Approval/          ← Items needing human review
│   ├── Plans/                     ← Claude's task plans
│   ├── Done/                      ← Completed items
│   ├── Logs/                      ← Daily action logs (YYYY-MM-DD.md)
│   ├── Dashboard.md               ← Live overview
│   ├── Company_Handbook.md        ← Rules of engagement
│   └── watcher_status.json        ← Live watcher health (written by orchestrator)
├── watchers/
│   ├── base_watcher.py            ← Abstract base class
│   ├── filesystem_watcher.py      ← File drop watcher (Bronze)
│   ├── gmail_watcher.py           ← Gmail watcher (Silver)
│   ├── whatsapp_watcher.py        ← WhatsApp Web watcher (Silver)
│   └── orchestrator.py            ← Master supervisor (Silver)
├── .claude/
│   └── skills/
│       ├── process-inbox.md
│       ├── update-dashboard.md
│       ├── triage-item.md
│       ├── create-plan.md
│       ├── draft-linkedin-post.md
│       ├── review-approvals.md
│       ├── approve-item.md
│       ├── ceo-briefing.md
│       ├── process-gmail.md
│       ├── process-whatsapp.md       ← NEW (Silver)
│       ├── publish-linkedin-post.md  ← NEW (Silver)
│       ├── schedule-task.md          ← NEW (Silver)
│       ├── draft-email-reply.md      ← NEW (Silver)
│       └── watcher-status.md         ← NEW (Silver)
├── CLAUDE.md                      ← Claude Code configuration
├── requirements.txt               ← Python dependencies (Silver tier enabled)
└── README.md
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      WATCHERS LAYER                      │
│  filesystem_watcher  │  gmail_watcher  │ whatsapp_watcher│
│         ↓            │       ↓         │       ↓         │
│                 orchestrator.py (supervisor)             │
└───────────────────────────┬─────────────────────────────┘
                            │ writes .md action files
                            ▼
              AI_Employee_Vault/Needs_Action/
                            │
                            ▼  (Claude skills: process-inbox / process-gmail / process-whatsapp)
              [Claude reads Company_Handbook.md]
                            │
              ┌─────────────┼────────────────┐
              ▼             ▼                ▼
          Low risk     Needs approval    Complex task
          Execute       Pending_         create-plan →
          → Done/       Approval/        Plan.md
                            │
                            ▼ (human reviews via review-approvals)
                       /Approved/
                            │
                            ▼ (approve-item / publish-linkedin-post)
                        Execute → /Done/
```

---

## Tier Checklist

### Bronze Tier ✅

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System Watcher)
- [x] Claude Code reading from and writing to the vault (via CLAUDE.md + skills)
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] All AI functionality implemented as Agent Skills

### Silver Tier ✅

- [x] All Bronze requirements
- [x] Three Watcher scripts: Filesystem + Gmail + WhatsApp
- [x] Orchestrator to supervise and auto-restart watchers
- [x] LinkedIn auto-posting workflow (draft → approve → publish via Playwright)
- [x] Email reply drafting skill with approval workflow
- [x] WhatsApp message processing skill
- [x] Human-in-the-loop approval workflow (Pending_Approval → approve-item)
- [x] Scheduling support via `/schedule-task` (cron / Windows Task Scheduler)
- [x] Watcher health monitoring via `/watcher-status`
- [x] All AI functionality implemented as Agent Skills (14 total)

---

## Scheduling Recommended Tasks

Set up recurring automations with `/schedule-task`:

```
/schedule-task ceo-briefing "monday 08:00"
/schedule-task update-dashboard "daily 07:00"
/schedule-task process-inbox "hourly"
```

---

## Security

- Never commit `.env` or `credentials.json` — add to `.gitignore`.
- Never commit `token.json` or `whatsapp_profile/` — these contain live session credentials.
- Store API keys in environment variables only.
- See `Company_Handbook.md` for the full permission/approval matrix.

### Recommended .gitignore additions

```
.env
credentials.json
token.json
whatsapp_profile/
*.pid
AI_Employee_Vault/.gmail_processed_ids.json
AI_Employee_Vault/.whatsapp_processed.json
```

---

## Next Steps (Gold Tier)

- Integrate Odoo Community for accounting via MCP
- Add Facebook/Instagram posting
- Add Twitter/X posting
- Ralph Wiggum loop for autonomous multi-step task completion
- Weekly business audit with full accounting summary
