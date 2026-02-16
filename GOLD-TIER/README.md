# AI Employee — Gold Tier (Hackathon 0)

Personal AI Employee: a local-first, fully autonomous agent system that monitors personal and business affairs, manages social media across 4 platforms, integrates with Odoo ERP for accounting, generates weekly CEO briefings, and takes action on your behalf — with comprehensive audit logging and error recovery.

> Built on top of Bronze + Silver Tier — all previous functionality remains intact.

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
  | (Web)    |    | Watcher (Slvr) |   |  /Plans/ /Pending/ /Done/ /Logs/
  +----------+    +----------------+   |         /Approval/            |
                                       |              |                |
  +----------+    +----------------+   |    +---------+--------+       |
  | LinkedIn | <- | LinkedIn       |   |    |  /Approved/      |       |
  | (API)    |    | Watcher (Slvr) |   |    |  (Human moves    |       |
  +----------+    +----------------+   |    |   files here)    |       |
                                       |    +------------------+       |
  +----------+    +----------------+   |                               |
  | Schedule | -> | Scheduler      | --+  +------- MCP Servers -------+
  | (Cron)   |    | (Gold: +Audit) |      |                           |
  +----------+    +----------------+      |  +------------------+     |
                                          |  | Gmail MCP (Slvr) |     |
  +----------+    +----------------+      |  +------------------+     |
  | Facebook | <- | Social Watcher | --+  |  +------------------+     |
  | Insta    |    | (Gold NEW)     |   |  |  | Odoo MCP (Gold)  |     |
  +----------+    +----------------+   |  |  +------------------+     |
                                       |  |  +------------------+     |
  +----------+    +----------------+   |  |  | Social MCP (Gold)|     |
  | Twitter  | <- | (via Social    |   |  |  +------------------+     |
  | /X       |    |  Watcher)      |   |  |  +------------------+     |
  +----------+    +----------------+   |  |  | Twitter MCP(Gold)|     |
                                       |  |  +------------------+     |
  +----------+    +----------------+   |  |                           |
  | Odoo ERP | <- | Odoo Watcher   | --+  +---------------------------+
  | (local)  |    | (Gold NEW)     |
  +----------+    +----------------+

  +-------------------+     +------------------+     +------------------+
  | Orchestrator v2.0 |     | Audit Logger     |     | Error Handler    |
  | (monitors all     | <-> | (JSON logs every | <-> | (retry + backoff |
  |  action folders)  |     |  AI action)      |     |  + degradation)  |
  +-------------------+     +------------------+     +------------------+

  +---------------------------+
  | Ralph Wiggum Loop (Gold)  |
  | Stop hook keeps Claude    |
  | working until task is     |
  | truly complete            |
  +---------------------------+
```

## Tier Evolution

| Tier | Focus | Components |
|------|-------|------------|
| **Bronze** | Core automation | File Watcher, Gmail Watcher, Orchestrator, basic skills |
| **Silver** | Communication | WhatsApp, LinkedIn, Email MCP, Scheduler, Approval Workflow |
| **Gold** | Full autonomy | Odoo ERP, Facebook/Instagram, Twitter, CEO Briefings, Audit Logging, Error Recovery, Ralph Wiggum Loop |

## What's New in Gold Tier

| Feature | Description |
|---------|-------------|
| **Odoo Watcher** | Monitors self-hosted Odoo ERP for new transactions, creates accounting action files, flags amounts >$100 |
| **Social Watcher** | Monitors `/Approved/` for Facebook, Instagram, Twitter posts; creates weekly social summaries |
| **Odoo MCP Server** | `get_invoices`, `create_draft_invoice`, `get_monthly_summary` — read + draft only, never posts |
| **Social MCP Server** | `post_facebook`, `post_instagram` via Facebook Graph API |
| **Twitter MCP Server** | `post_tweet` with 280-char validation, max 1/day enforced |
| **Audit Logger** | Every AI action logged to `/Logs/YYYY-MM-DD.json` with sanitized parameters (no credentials) |
| **Error Handler** | `@with_retry` decorator with exponential backoff, dashboard alerts, graceful degradation |
| **Weekly CEO Briefing** | Sunday 8 PM audit -> Monday Morning briefing in `/Briefings/` with revenue, tasks, social, suggestions |
| **Business Goals** | `Business_Goals.md` with KPIs, revenue targets, alert thresholds, subscription audit rules |
| **Ralph Wiggum Loop** | Stop hook pattern — Claude keeps working until `TASK_COMPLETE` signal, with max iteration safety |
| **5 New Agent Skills** | facebook-instagram-poster, twitter-poster, odoo-accounting, ceo-briefing, audit-logger |

## Prerequisites

- Python 3.13+
- Node.js v24+ (for MCP servers)
- [Obsidian](https://obsidian.md/) v1.10.6+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (latest)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [PM2](https://pm2.keymetrics.io/) (process manager — `npm install -g pm2`)
- Odoo Community Edition (self-hosted locally, optional until configured)

## Folder Structure

```
AI_Employee_Vault/                    <- Obsidian Vault (GUI + Memory)
|-- Dashboard.md                      <- Live status dashboard (Bronze + Silver + Gold sections)
|-- Company_Handbook.md               <- Rules of engagement (Bronze + Silver + Gold rules)
|-- Business_Goals.md                 <- [Gold] KPIs, revenue targets, audit rules
|-- Inbox/                            <- [Bronze] Drop files here
|-- Needs_Action/                     <- [Bronze] Action files for Claude
|-- Plans/                            <- [Bronze] Claude's reasoning plans
|-- Done/                             <- [Bronze] Archived processed items
|-- Logs/                             <- [Bronze + Gold] System logs + JSON audit logs
|-- Pending_Approval/                 <- [Silver] Approval requests land here
|-- Approved/                         <- [Silver] Human moves files here to approve
|-- Rejected/                         <- [Silver] Human moves files here to reject
|-- Social/                           <- [Silver + Gold] Social media content
|   |-- LinkedIn_Drafts/              <- [Silver] LinkedIn drafts
|   |-- Facebook_Drafts/              <- [Gold] Facebook drafts
|   |-- Instagram_Drafts/             <- [Gold] Instagram drafts
|   |-- Twitter_Drafts/               <- [Gold] Twitter/X drafts
|   |-- Social_Summaries/             <- [Gold] Weekly engagement summaries
|   +-- Posted/                       <- [Silver] Archive of published posts
|-- Scheduling/                       <- [Silver] Cron config & task logs
|-- Accounting/                       <- [Gold] Financial data from Odoo
|   |-- Current_Month.md              <- Running transaction log
|   +-- Invoices/                     <- Draft invoices awaiting approval
|-- Briefings/                        <- [Gold] CEO briefing reports
|-- Audit/                            <- [Gold] Weekly audit working files
|   |-- Weekly_Audit_Template.md      <- Template Claude follows for audit
|   +-- Archive/                      <- Past audit files
+-- Skills/                           <- Agent skill definitions
    |-- email-triage/SKILL.md         <- [Bronze]
    |-- file-processor/SKILL.md       <- [Bronze]
    |-- whatsapp-monitor/SKILL.md     <- [Silver]
    |-- linkedin-poster/SKILL.md      <- [Silver]
    |-- email-sender/SKILL.md         <- [Silver]
    |-- plan-creator/SKILL.md         <- [Silver]
    |-- facebook-instagram-poster/    <- [Gold]
    |-- twitter-poster/               <- [Gold]
    |-- odoo-accounting/              <- [Gold]
    |-- ceo-briefing/                 <- [Gold]
    +-- audit-logger/                 <- [Gold]

ai_employee/                          <- Python project
|-- base_watcher.py                   <- [Bronze] Abstract base class
|-- filesystem_watcher.py             <- [Bronze] File drop monitor
|-- gmail_watcher.py                  <- [Bronze] Gmail inbox monitor
|-- whatsapp_watcher.py               <- [Silver] WhatsApp Web monitor
|-- linkedin_watcher.py               <- [Silver] LinkedIn post watcher
|-- scheduler.py                      <- [Silver + Gold] Cron scheduling + Sunday audit
|-- orchestrator.py                   <- [Silver] Monitors action folders
|-- social_watcher.py                 <- [Gold] Facebook/Instagram/Twitter monitor
|-- odoo_watcher.py                   <- [Gold] Odoo transaction watcher
|-- audit_logger.py                   <- [Gold] Centralized JSON audit logging
|-- error_handler.py                  <- [Gold] Retry logic + graceful degradation
|-- pyproject.toml                    <- [Gold] v3.0.0 with all dependencies
|-- .env / .env.example               <- [Gold] All tier variables
+-- mcp/                              <- MCP servers
    |-- mcp_config.json               <- [Gold] 4 server entries
    |-- email_mcp/                    <- [Silver] Gmail MCP
    |-- odoo_mcp/                     <- [Gold] Odoo JSON-RPC MCP
    |-- social_mcp/                   <- [Gold] Facebook + Instagram MCP
    +-- twitter_mcp/                  <- [Gold] Twitter/X MCP
```

## Setup

```bash
# 1. Enter the project
cd ai_employee

# 2. Install Python dependencies
uv sync

# 3. Setup environment
cp .env.example .env
# Edit .env — set VAULT_PATH, all credentials, DRY_RUN=true

# 4. Install MCP server dependencies
cd mcp/email_mcp && npm install && cd ../..
cd mcp/odoo_mcp && npm install && cd ../..
cd mcp/social_mcp && npm install && cd ../..
cd mcp/twitter_mcp && npm install && cd ../..

# 5. Install PM2 globally
npm install -g pm2

# 6. Open AI_Employee_Vault/ in Obsidian

# 7. (Optional) Install Odoo Community locally
# See: https://www.odoo.com/page/download
# Run at http://localhost:8069
```

## Running (PM2 — Recommended)

```bash
cd ai_employee

# Bronze watchers
pm2 start filesystem_watcher.py  --interpreter .venv/Scripts/python.exe --name file-watcher
pm2 start gmail_watcher.py       --interpreter .venv/Scripts/python.exe --name gmail-watcher

# Silver watchers
pm2 start whatsapp_watcher.py    --interpreter .venv/Scripts/python.exe --name whatsapp-watcher
pm2 start linkedin_watcher.py    --interpreter .venv/Scripts/python.exe --name linkedin-watcher

# Gold watchers
pm2 start social_watcher.py      --interpreter .venv/Scripts/python.exe --name social-watcher
pm2 start odoo_watcher.py        --interpreter .venv/Scripts/python.exe --name odoo-watcher

# Scheduler + Orchestrator
pm2 start scheduler.py           --interpreter .venv/Scripts/python.exe --name scheduler
pm2 start orchestrator.py        --interpreter .venv/Scripts/python.exe --name orchestrator

# MCP Servers (all 4)
pm2 start mcp/email_mcp/index.js                                       --name email-mcp
pm2 start mcp/odoo_mcp/index.js                                        --name odoo-mcp
pm2 start mcp/social_mcp/index.js                                      --name social-mcp
pm2 start mcp/twitter_mcp/index.js                                     --name twitter-mcp

# Manage
pm2 save          # Save process list
pm2 startup       # Auto-start on reboot
pm2 list          # View all 12 processes
pm2 logs          # Stream live logs
pm2 stop all      # Stop everything
```

## How to Use

### File Processing (Bronze)
1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. File Watcher creates an action file in `/Needs_Action/`
3. Orchestrator detects it -> triggers Claude Code
4. Claude reads handbook rules, creates a Plan, updates Dashboard

### WhatsApp Monitoring (Silver)
1. WhatsApp Watcher scans for unread messages with urgent keywords
2. Creates `WHATSAPP_*.md` in `/Needs_Action/`
3. Claude drafts a reply in `/Plans/` and creates an approval file in `/Pending_Approval/`
4. **You** move the approval file to `/Approved/` to allow sending

### LinkedIn Posting (Silver)
1. Scheduler triggers a draft request on Mon/Wed/Fri at 10 AM
2. Claude writes a post draft -> saves to `/Social/LinkedIn_Drafts/`
3. Approval file goes to `/Pending_Approval/`
4. **You** review and move to `/Approved/` -> LinkedIn Watcher publishes it
5. Published posts are archived in `/Social/Posted/`

### Email Sending via MCP (Silver)
1. Claude drafts an email reply and creates an approval file
2. **You** move the approval file to `/Approved/`
3. Orchestrator detects it -> Claude calls `send_email` via MCP
4. In DRY_RUN mode: logs intent only. With DRY_RUN=false: sends via Gmail API

### Facebook / Instagram Posting (Gold)
1. Scheduler or manual trigger creates a social post task in `/Needs_Action/`
2. Claude drafts platform-appropriate content -> saves to `/Social/Facebook_Drafts/` or `/Social/Instagram_Drafts/`
3. Approval file goes to `/Pending_Approval/`
4. **You** move to `/Approved/` -> Social Watcher creates action file -> Social MCP posts it
5. Published posts archived in `/Social/Posted/`, logged via audit_logger

### Twitter/X Posting (Gold)
1. Same approval flow as Facebook/Instagram
2. Tweets enforced at max 280 characters, max 1 per day
3. No auto-replies or DMs — explicit human approval required

### Odoo Accounting (Gold)
1. Odoo Watcher polls for new invoices/transactions every hour
2. Creates `ODOO_*.md` action files in `/Needs_Action/`
3. Transactions >$100 are flagged for human review
4. Claude updates `/Accounting/Current_Month.md` and Dashboard
5. Draft invoices only — **never posts or records payments without approval**

### Weekly CEO Briefing (Gold)
1. Scheduler triggers audit task every Sunday at 8 PM
2. Claude reads Business_Goals.md, Done/, Accounting, Social, Logs
3. Generates comprehensive briefing -> `/Briefings/YYYY-MM-DD_Monday_Briefing.md`
4. Includes: revenue vs target, completed tasks, bottlenecks, social performance, proactive suggestions

### Ralph Wiggum Loop (Gold)
```bash
# Set environment variables
export RALPH_PROMISE="TASK_COMPLETE"
export RALPH_MAX_ITERATIONS=10
export VAULT_PATH=/path/to/AI_Employee_Vault

# Claude keeps working until TASK_COMPLETE signal
claude --cwd /path/to/AI_Employee_Vault \
  "Process all files in /Needs_Action/ completely.
   For each file: read it, take action per Company_Handbook.md,
   log everything, update Dashboard.md, move to /Done/.
   When ALL files are processed, output: TASK_COMPLETE"
```

### Approval Flow
```
/Pending_Approval/  ->  Human reviews  ->  /Approved/   -> Orchestrator acts
                                        ->  /Rejected/   -> No action taken
```

## Scheduling

| Task               | Schedule        | Time     | Tier   |
|--------------------|-----------------|----------|--------|
| Daily Briefing     | Every day       | 8:00 AM  | Silver |
| LinkedIn Draft     | Mon, Wed, Fri   | 10:00 AM | Silver |
| WhatsApp Check     | Every 30 sec    | Ongoing  | Silver |
| Gmail Check        | Every 2 min     | Ongoing  | Bronze |
| File Watch         | Real-time       | Ongoing  | Bronze |
| Weekly Audit       | Sunday          | 8:00 PM  | Gold   |
| Social Summary     | Sunday          | 7:00 PM  | Gold   |
| Odoo Sync          | Every hour      | Ongoing  | Gold   |

**Quiet Hours:** No scheduled tasks between 11 PM - 7 AM.

## Error Recovery (Gold)

| Scenario | Behavior |
|----------|----------|
| API timeout | Exponential backoff: 1s -> 2s -> 4s, max 3 retries |
| Auth failure | Permanent error — no retry, alert on Dashboard |
| Odoo offline | Standby mode, queue locally, never retry payments |
| MCP server crash | PM2 auto-restarts, alert logged |
| Orchestrator crash | PM2 watchdog restarts within 60 seconds |
| Component failure | Graceful degradation — other components continue |

## Audit Logging (Gold)

Every AI action is logged to `/Logs/YYYY-MM-DD.json`:

```json
{
  "timestamp": "2026-02-16T12:00:00Z",
  "action_type": "email_send",
  "actor": "claude_code",
  "target": "client@example.com",
  "parameters": { "subject": "Invoice Follow-up" },
  "approval_status": "approved",
  "result": "success",
  "error": null
}
```

- Credentials are **never** logged (auto-sanitized)
- Logs retained for 90 days minimum
- `cleanup_old_logs()` runs weekly

## Security

- `.env` is gitignored — credentials never touch GitHub
- `DRY_RUN=true` by default — no real actions until explicitly enabled
- All sensitive actions require human-in-the-loop approval (file-based gate)
- WhatsApp session stays local — never inside the vault or synced to cloud
- Social media tokens stored in `.env` only — never in any `.md` file
- Odoo self-hosted locally — never exposed to public internet
- Audit logs sanitize all credentials automatically
- Email rate limit: max 10/hour (MCP enforced)
- LinkedIn rate limit: max 3 posts/day
- Twitter rate limit: max 1 tweet/day, max 280 chars
- Facebook/Instagram: max 1 post/day per platform
- No script ever writes directly to `/Approved/` — only humans do
- Ralph Wiggum Loop has `MAX_ITERATIONS` safety limit (default 10)

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
| tweepy | Twitter/X API v2 | Gold |
| facebook-sdk | Facebook Graph API | Gold |
| instagrapi | Instagram API | Gold |
| xmlrpc-client | Odoo JSON-RPC calls | Gold |
| tenacity | Retry with exponential backoff | Gold |
| rich | Terminal logging | Gold |
| orjson | Fast JSON for audit logs | Gold |
| @modelcontextprotocol/sdk | MCP server (Node.js) | Silver |
| googleapis / nodemailer | Gmail via Node.js | Silver |
| node-fetch | Facebook API calls (Node.js) | Gold |
| twitter-api-v2 | Twitter API (Node.js) | Gold |

## Lessons Learned

1. **File-based communication is robust.** Using markdown files as the interface between watchers, Claude, and humans creates a natural audit trail and makes debugging straightforward. Every action is a file you can read.

2. **Human-in-the-loop via folder gates works well.** The `/Pending_Approval/` -> `/Approved/` pattern is simple, Obsidian-friendly, and impossible to accidentally bypass — no script writes to `/Approved/`.

3. **DRY_RUN as the default is essential.** Every MCP server and watcher defaults to DRY_RUN=true. This prevented real API calls during development and testing. Always build with the safety on.

4. **Layered tiers prevent regression.** Building Gold on top of Silver on top of Bronze, with explicit "do not modify" rules, meant each tier's functionality stayed stable as new features were added.

5. **Centralized audit logging pays for itself.** The `audit_logger.py` pattern (one function call per action) made it trivial to add logging everywhere. The sanitization step prevents credential leaks automatically.

6. **Error recovery must be built in from the start.** The `@with_retry` decorator pattern is cleaner than try/except blocks scattered through every function. Graceful degradation keeps the system running even when one component fails.

7. **MCP servers should be minimal.** Each MCP server does one domain well (email, Odoo, social, Twitter). Keeping them small and focused makes them easier to test and debug independently.

8. **The Ralph Wiggum Loop needs a safety valve.** Autonomous loops are powerful but dangerous. The `MAX_ITERATIONS` limit prevents runaway execution, and the state file tracks progress across invocations.

## Tier Declaration

**Gold Tier** — Fully Autonomous AI Employee with Cross-Domain Business Operations, ERP Integration, Multi-Platform Social Media, Weekly CEO Briefings, Comprehensive Audit Logging, and Error Recovery

Built on top of Bronze + Silver Tier — all previous folders, files, and functionality remain fully intact.

---
*Gold Tier — Personal AI Employee Hackathon 0 | Panaversity 2026*
