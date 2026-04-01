# Personal AI Employee — Gold Tier

**Hackathon 0: Building Autonomous FTEs in 2026**

A local-first, agent-driven AI Employee powered by **Claude Code**, **Obsidian**, **Odoo**, and cross-platform social media integration.

---

## What This Is

A **Gold Tier** implementation of the Personal AI Employee architecture. It builds on Silver and adds:

- **Odoo 19 Community** (self-hosted via Docker) for accounting — invoices, partners, financial audits
- **Facebook & Instagram** monitoring and posting via Meta Graph API
- **Twitter/X** monitoring and posting via Twitter API v2
- **Ralph Wiggum loop** for autonomous multi-step task completion
- **Comprehensive audit logging** (structured JSONL + daily markdown)
- **Error recovery & graceful degradation** across all services
- **Weekly Business & Accounting Audit** combining vault + Odoo + social metrics
- **28 Agent Skills** covering all Bronze + Silver + Gold capabilities

---

## Quick Start

### 1. Start Odoo (Docker)

```bash
cd "Gold tier/odoo"
cp .env.example .env
docker compose up -d
# Open http://localhost:8069 — create database "ai_employee"
# See odoo/ODOO_SETUP.md for detailed instructions
cd ..
```

### 2. Install Python dependencies

```bash
cd "Gold tier"
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials:
#   - Gmail OAuth (credentials.json)
#   - Facebook Page Access Token + Page ID
#   - Twitter API keys
#   - Odoo connection details
```

### 4. Open the vault in Obsidian

Open `AI_Employee_Vault/` as an Obsidian vault. You'll see:
- `Dashboard.md` — live overview of all systems
- `Company_Handbook.md` — AI rules of engagement

### 5. First-time platform setup

```bash
# Facebook — test API connection
python watchers/facebook_watcher.py --setup

# Twitter — test API connection
python watchers/twitter_watcher.py --setup

# LinkedIn — browser login (one-time)
python watchers/linkedin_watcher.py --setup

# WhatsApp — QR code scan (one-time)
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault --setup
```

### 6. Start all watchers

```bash
python watchers/orchestrator.py --vault AI_Employee_Vault
```

### 7. Run Claude Code

```bash
claude
```

---

## Gold Tier Skills (27 total)

### Bronze Skills (inherited)

| Command | Purpose |
|---------|---------|
| `/process-inbox` | Process all items in /Needs_Action |
| `/update-dashboard` | Refresh Dashboard.md |
| `/triage-item` | Triage a specific item |
| `/create-plan` | Create Plan.md for complex tasks |
| `/draft-linkedin-post` | Draft LinkedIn post for approval |
| `/review-approvals` | Summarise all pending approvals |
| `/approve-item` | Execute an approved action |
| `/ceo-briefing` | Monday Morning CEO Briefing |
| `/process-gmail` | Triage Gmail action files |

### Silver Skills (inherited)

| Command | Purpose |
|---------|---------|
| `/process-whatsapp` | Triage WhatsApp messages |
| `/process-linkedin` | Triage LinkedIn notifications |
| `/publish-linkedin-post` | Publish approved LinkedIn post |
| `/schedule-task` | Create scheduled recurring jobs |
| `/draft-email-reply` | Draft email reply for approval |
| `/watcher-status` | Check watcher health |

### Gold Skills (new)

| Command | Purpose |
|---------|---------|
| `/draft-facebook-post` | Draft Facebook Page post for approval |
| `/publish-facebook-post` | Publish approved FB post via Graph API |
| `/process-facebook` | Triage FB/IG comments and messages |
| `/draft-twitter-post` | Draft tweet (≤280 chars) for approval |
| `/publish-twitter-post` | Publish approved tweet via API v2 |
| `/process-twitter` | Triage Twitter/X mentions |
| `/social-media-summary` | Cross-platform social metrics report |
| `/odoo-accounting-audit` | Pull Odoo financials into vault report |
| `/odoo-create-invoice` | Create draft invoice (approval required) |
| `/odoo-list-partners` | List Odoo customers/partners |
| `/odoo-health` | Check if Odoo Docker is running |
| `/weekly-business-audit` | Full audit: vault + Odoo + social media |
| `/ralph-loop` | Autonomous multi-step task loop |

---

## Project Structure

```
Gold tier/
├── AI_Employee_Vault/             ← Obsidian vault (the AI's brain)
│   ├── Inbox/                     ← Drop files here
│   ├── Needs_Action/              ← Auto-generated action items
│   ├── Pending_Approval/          ← Items needing human review
│   ├── Approved/                  ← Human-approved items
│   ├── Plans/                     ← Claude's task plans
│   ├── Done/                      ← Completed items
│   ├── Logs/                      ← Daily logs + audit_trail.jsonl
│   ├── Accounting/                ← Odoo financial reports
│   ├── Dashboard.md               ← Live overview
│   └── Company_Handbook.md        ← Rules of engagement
├── watchers/
│   ├── base_watcher.py            ← Abstract base class
│   ├── filesystem_watcher.py      ← File drop watcher
│   ├── gmail_watcher.py           ← Gmail watcher (OAuth2)
│   ├── whatsapp_watcher.py        ← WhatsApp Web watcher
│   ├── linkedin_watcher.py        ← LinkedIn watcher (Playwright)     [Silver]
│   ├── facebook_watcher.py        ← Facebook + Instagram (Graph API)  [Gold]
│   ├── twitter_watcher.py         ← Twitter/X watcher (API v2)        [Gold]
│   ├── odoo_connector.py          ← Odoo JSON-RPC client              [Gold]
│   ├── audit_logger.py            ← Structured audit logging          [Gold]
│   └── orchestrator.py            ← Master supervisor (6 watchers)
├── odoo/
│   ├── docker-compose.yml         ← Odoo 19 + PostgreSQL
│   ├── odoo.conf                  ← Odoo server configuration
│   ├── .env.example               ← Docker env vars
│   └── ODOO_SETUP.md              ← Step-by-step Odoo setup guide
├── .claude/
│   ├── skills/                    ← 27 Agent Skills (Bronze+Silver+Gold)
│   └── hooks/
│       └── ralph_wiggum.py        ← Ralph Wiggum stop hook
├── CLAUDE.md                      ← Claude Code configuration
├── requirements.txt               ← Python dependencies
├── .env.example                   ← Environment template
└── README.md                      ← This file
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          WATCHERS LAYER (6 watchers)                     │
│  filesystem │ gmail │ whatsapp │ linkedin │ facebook │ twitter           │
│      ↓          ↓        ↓          ↓          ↓          ↓             │
│                    orchestrator.py (supervisor)                          │
└─────────────────────────────┬────────────────────────────────────────────┘
                              │ writes .md action files
                              ▼
                AI_Employee_Vault/Needs_Action/
                              │
                              ▼  (Claude skills: process-inbox/gmail/facebook/twitter)
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
                              ▼ (approve-item / publish-facebook-post / publish-twitter-post)
                          Execute → /Done/
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                             │
│  Gmail (OAuth2) │ Facebook (Graph API) │ Twitter (API v2)       │
│  LinkedIn (Playwright) │ Odoo 19 (JSON-RPC via Docker)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    audit_logger.py → Logs/audit_trail.jsonl
```

### Ralph Wiggum Loop (Autonomous Processing)

```
Start: /ralph-loop "Process all items"
  ↓
  Claude processes items in /Needs_Action/
  ↓
  Stop hook checks: Is task complete?
  ├── YES → Allow exit, log completion
  └── NO  → Re-inject prompt, continue (up to max-iterations)
```

---

## Tier Checklist

### Bronze Tier ✅
- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System Watcher)
- [x] Claude Code reading/writing to the vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] All AI functionality as Agent Skills

### Silver Tier ✅
- [x] All Bronze requirements
- [x] Three+ Watcher scripts (Filesystem + Gmail + WhatsApp + LinkedIn)
- [x] Orchestrator supervisor with auto-restart
- [x] LinkedIn auto-posting (draft → approve → publish)
- [x] Email reply drafting with approval workflow
- [x] Human-in-the-loop approval workflow
- [x] Scheduling support via `/schedule-task`
- [x] All AI functionality as Agent Skills (14 total)

### Gold Tier ✅
- [x] All Silver requirements
- [x] Full cross-domain integration (Personal + Business)
- [x] Odoo 19 Community (Docker Compose) with JSON-RPC integration
- [x] Facebook & Instagram integration (post + monitor + summary)
- [x] Twitter/X integration (post + monitor + summary)
- [x] Multiple MCP servers / API integrations (6 platforms)
- [x] Weekly Business and Accounting Audit with CEO Briefing
- [x] Error recovery and graceful degradation
- [x] Comprehensive audit logging (JSONL + markdown)
- [x] Ralph Wiggum loop for autonomous multi-step task completion
- [x] Documentation of architecture and lessons learned
- [x] All AI functionality as Agent Skills (27 total)

---

## Scheduling Recommended Tasks

```
/schedule-task weekly-business-audit "monday 08:00"
/schedule-task social-media-summary "friday 17:00"
/schedule-task update-dashboard "daily 07:00"
/schedule-task process-inbox "hourly"
/schedule-task odoo-accounting-audit "weekly monday 09:00"
```

---

## Security

- Never commit `.env`, `credentials.json`, `token.json` — add to `.gitignore`.
- Never commit browser profiles (`whatsapp_profile/`, `linkedin_profile/`).
- Odoo runs locally via Docker — no external exposure.
- All social media tokens stored in `.env` only.
- See `Company_Handbook.md` for the full permission/approval matrix.

### Recommended .gitignore

```
.env
credentials.json
token.json
whatsapp_profile/
linkedin_profile/
*.pid
AI_Employee_Vault/.gmail_processed_ids.json
AI_Employee_Vault/.whatsapp_processed.json
AI_Employee_Vault/.facebook_processed.json
AI_Employee_Vault/.twitter_processed.json
AI_Employee_Vault/.ralph_wiggum_state.json
odoo/odoo_db_data/
odoo/odoo_data/
```

---

## Lessons Learned

1. **Graceful degradation is essential** — any external service can go down; the system must continue operating with reduced capability rather than failing entirely.
2. **Human-in-the-loop for all public actions** — drafting is safe to automate, but publishing requires explicit approval.
3. **Structured audit logging** (JSONL) enables querying and analysis; markdown logs provide human readability.
4. **Docker Compose for Odoo** simplifies deployment — single command to spin up a full accounting system.
5. **The Ralph Wiggum pattern** transforms Claude from reactive to proactive — it keeps working until the job is done.
6. **Watcher + Skill separation** keeps concerns clean: watchers detect, skills decide and act.
