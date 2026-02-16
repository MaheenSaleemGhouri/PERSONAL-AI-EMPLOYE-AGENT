# AI Employee — Silver Tier (Hackathon 0)

Personal AI Employee: a local-first, autonomous agent system that monitors personal and business affairs, posts to LinkedIn, sends emails (after approval), and takes action on your behalf.

> Built on top of Bronze Tier — all Bronze functionality remains intact.

## Architecture

```
                              +-------------------+
                              |   Obsidian Vault  |
                              |  (Dashboard.md)   |
                              +--------+----------+
                                       |
  +----------+    +----------------+   |   +-------------+    +---------+
  |  /Inbox  | -> | File Watcher   | --+-> | /Needs_     | -> | Claude  |
  | (files)  |    | (Bronze)       |       |  Action/    |    | Code    |
  +----------+    +----------------+       +-------------+    +----+----+
                                                                   |
  +----------+    +----------------+          +--------------------+
  |  Gmail   | -> | Gmail Watcher  | -------> |
  | (API)    |    | (Bronze)       |          |
  +----------+    +----------------+          |
                                              |
  +----------+    +----------------+   +------+-------+------+--------+
  | WhatsApp | -> | WhatsApp       |   |      |       |      |        |
  | (Web)    |    | Watcher (NEW)  |   |  /Plans/ /Pending/ /Done/ /Logs/
  +----------+    +----------------+   |         /Approval/            |
                                       |              |                |
  +----------+    +----------------+   |    +---------+--------+       |
  | LinkedIn | <- | LinkedIn       |   |    |  /Approved/      |       |
  | (API)    |    | Watcher (NEW)  |   |    |  (Human moves    |       |
  +----------+    +----------------+   |    |   files here)    |       |
                                       |    +------------------+       |
  +----------+    +----------------+   |                               |
  | Schedule | -> | Scheduler      | --+    +------------------+       |
  | (Cron)   |    | (NEW)          |        | Gmail MCP Server | <-----+
  +----------+    +----------------+        | (Email Sending)  |
                                            +------------------+
  +-------------------+
  | Orchestrator v2.0 | --- Monitors /Needs_Action/ + /Approved/ + expired approvals
  +-------------------+
```

## What's New in Silver Tier

| Feature | Description |
|---------|-------------|
| **WhatsApp Watcher** | Monitors WhatsApp Web for urgent keyword messages (invoice, payment, urgent, help) |
| **LinkedIn Watcher** | Auto-drafts LinkedIn posts on schedule, publishes approved posts |
| **Scheduler** | Cron-based daily briefings (8 AM), LinkedIn drafts (Mon/Wed/Fri), quiet hours enforced |
| **Gmail MCP Server** | Node.js MCP server with `send_email` and `draft_email` tools, rate-limited |
| **Approval Workflow** | Full HITL flow: `/Pending_Approval/` → human moves to `/Approved/` → orchestrator acts |
| **Plan Creator** | Structured `Plan.md` reasoning loop before any complex task execution |
| **4 New Agent Skills** | whatsapp-monitor, linkedin-poster, email-sender, plan-creator |

## Prerequisites

- Python 3.13+
- Node.js v24+ (for MCP server)
- [Obsidian](https://obsidian.md/) v1.10.6+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (latest)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [PM2](https://pm2.keymetrics.io/) (process manager — `npm install -g pm2`)

## Folder Structure

```
AI_Employee_Vault/                    ← Obsidian Vault (GUI + Memory)
├── Dashboard.md                      ← Live status dashboard (Bronze + Silver sections)
├── Company_Handbook.md               ← Rules of engagement (Bronze + Silver rules)
├── Inbox/                            ← [Bronze] Drop files here
├── Needs_Action/                     ← [Bronze] Action files for Claude
├── Plans/                            ← [Bronze] Claude's reasoning plans
├── Done/                             ← [Bronze] Archived processed items
├── Logs/                             ← [Bronze] System logs
├── Pending_Approval/                 ← [Silver] Approval requests land here
├── Approved/                         ← [Silver] Human moves files here to approve
├── Rejected/                         ← [Silver] Human moves files here to reject
├── Social/                           ← [Silver] Social media content
│   ├── LinkedIn_Drafts/              ← Drafts waiting for approval
│   └── Posted/                       ← Archive of published posts
├── Scheduling/                       ← [Silver] Cron config & task logs
│   ├── cron_config.md
│   └── scheduled_tasks.md
└── Skills/                           ← Agent skill definitions
    ├── email-triage/SKILL.md         ← [Bronze]
    ├── file-processor/SKILL.md       ← [Bronze]
    ├── whatsapp-monitor/SKILL.md     ← [Silver]
    ├── linkedin-poster/SKILL.md      ← [Silver]
    ├── email-sender/SKILL.md         ← [Silver]
    └── plan-creator/SKILL.md         ← [Silver]

ai_employee/                          ← Python project
├── base_watcher.py                   ← [Bronze] Abstract base class
├── filesystem_watcher.py             ← [Bronze] File drop monitor
├── gmail_watcher.py                  ← [Bronze] Gmail inbox monitor
├── whatsapp_watcher.py               ← [Silver] WhatsApp Web monitor
├── linkedin_watcher.py               ← [Silver] LinkedIn post watcher
├── scheduler.py                      ← [Silver] Cron-based scheduling
├── orchestrator.py                   ← [Updated] Now checks /Approved/ + expired approvals
├── pyproject.toml                    ← [Updated] Silver dependencies added
├── .env / .env.example               ← [Updated] Silver variables added
└── mcp/                              ← [Silver] MCP servers
    ├── mcp_config.json
    └── email_mcp/
        ├── package.json
        └── index.js                  ← Gmail MCP server (send_email, draft_email)
```

## Setup

```bash
# 1. Enter the project
cd ai_employee

# 2. Install Python dependencies
uv sync

# 3. Setup environment
cp .env.example .env
# Edit .env — set VAULT_PATH, credentials, DRY_RUN=true

# 4. Install MCP server dependencies
cd mcp/email_mcp && npm install && cd ../..

# 5. Install PM2 globally
npm install -g pm2

# 6. Open AI_Employee_Vault/ in Obsidian
```

## Running (PM2 — Recommended)

```bash
cd ai_employee

# Start all processes
pm2 start filesystem_watcher.py  --interpreter .venv/Scripts/python.exe --name file-watcher
pm2 start gmail_watcher.py       --interpreter .venv/Scripts/python.exe --name gmail-watcher
pm2 start whatsapp_watcher.py    --interpreter .venv/Scripts/python.exe --name whatsapp-watcher
pm2 start linkedin_watcher.py    --interpreter .venv/Scripts/python.exe --name linkedin-watcher
pm2 start scheduler.py           --interpreter .venv/Scripts/python.exe --name scheduler
pm2 start orchestrator.py        --interpreter .venv/Scripts/python.exe --name orchestrator
pm2 start mcp/email_mcp/index.js                                       --name email-mcp

# Manage processes
pm2 list          # View status of all processes
pm2 logs          # Stream live logs
pm2 save          # Save process list
pm2 startup       # Auto-start on reboot
pm2 stop all      # Stop everything
```

## How to Use

### File Processing (Bronze)
1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. File Watcher creates an action file in `/Needs_Action/`
3. Orchestrator detects it → triggers Claude Code
4. Claude reads handbook rules, creates a Plan, updates Dashboard

### WhatsApp Monitoring (Silver)
1. WhatsApp Watcher scans for unread messages with urgent keywords
2. Creates `WHATSAPP_*.md` in `/Needs_Action/`
3. Claude drafts a reply in `/Plans/` and creates an approval file in `/Pending_Approval/`
4. **You** move the approval file to `/Approved/` to allow sending

### LinkedIn Posting (Silver)
1. Scheduler triggers a draft request on Mon/Wed/Fri at 10 AM
2. Claude writes a post draft → saves to `/Social/LinkedIn_Drafts/`
3. Approval file goes to `/Pending_Approval/`
4. **You** review and move to `/Approved/` → LinkedIn Watcher publishes it
5. Published posts are archived in `/Social/Posted/`

### Email Sending via MCP (Silver)
1. Claude drafts an email reply and creates an approval file
2. **You** move the approval file to `/Approved/`
3. Orchestrator detects it → Claude calls `send_email` via MCP
4. In DRY_RUN mode: logs intent only. With DRY_RUN=false: sends via Gmail API

### Approval Flow (Silver)
```
/Pending_Approval/  →  Human reviews  →  /Approved/   → Orchestrator acts
                                      →  /Rejected/   → No action taken
```

## Scheduling

| Task               | Schedule        | Time     |
|--------------------|-----------------|----------|
| Daily Briefing     | Every day       | 8:00 AM  |
| LinkedIn Draft     | Mon, Wed, Fri   | 10:00 AM |
| WhatsApp Check     | Every 30 sec    | Ongoing  |
| Gmail Check        | Every 2 min     | Ongoing  |
| File Watch         | Real-time       | Ongoing  |

**Quiet Hours:** No scheduled tasks between 11 PM – 7 AM.

## Security

- `.env` is gitignored — credentials never touch GitHub
- `DRY_RUN=true` by default — no real actions until explicitly enabled
- All sensitive actions require human-in-the-loop approval (file-based gate)
- WhatsApp session stays local — never inside the vault or synced to cloud
- LinkedIn credentials stored in `.env` only — never in any `.md` file
- Email rate limit: max 10/hour (enforced at MCP server level)
- LinkedIn rate limit: max 3 posts/day
- No script ever writes directly to `/Approved/` — only humans do

## Dependencies

| Package | Purpose | Tier |
|---------|---------|------|
| watchdog | File system monitoring | Bronze |
| python-dotenv | .env loading | Bronze |
| google-auth / google-api-python-client | Gmail API | Bronze |
| schedule | Job scheduling | Bronze |
| linkedin-api | LinkedIn automation | Silver |
| requests / httpx | HTTP clients | Silver |
| python-crontab / apscheduler | Cron management | Silver |
| beautifulsoup4 | HTML parsing | Silver |
| @modelcontextprotocol/sdk | MCP server (Node.js) | Silver |
| googleapis / nodemailer | Gmail via Node.js | Silver |

## Tier Declaration

**Silver Tier** — Functional AI Assistant with Social Media, Email MCP, Scheduling & Approval Workflows

Built on top of Bronze Tier — all Bronze folders, files, and functionality remain fully intact.

---
*Silver Tier — Personal AI Employee Hackathon 0 | Panaversity 2026*
