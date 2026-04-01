# Personal AI Employee — Bronze Tier

**Hackathon 0: Building Autonomous FTEs in 2026**

A local-first, agent-driven AI Employee powered by **Claude Code** and **Obsidian**.

---

## What This Is

A **Bronze Tier** implementation of the Personal AI Employee architecture. It gives you:

- An **Obsidian vault** as the AI's memory and dashboard
- A **File System Watcher** that monitors an Inbox folder and creates action items
- **Agent Skills** for Claude to process, triage, and log vault items
- A structured **folder workflow** (Inbox → Needs_Action → Pending_Approval → Done)

---

## Quick Start

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Open the vault in Obsidian

Open Obsidian and add `AI_Employee_Vault/` as a vault. You'll see:
- `Dashboard.md` — live overview
- `Company_Handbook.md` — AI rules of engagement

### 3. Start the File System Watcher

```bash
python watchers/filesystem_watcher.py
```

The watcher monitors `AI_Employee_Vault/Inbox/`. Drop any file there and it will
automatically create a `.md` action item in `AI_Employee_Vault/Needs_Action/`.

### 4. Run Claude Code from the vault directory

```bash
claude --cwd "AI_Employee_Vault"
```

Use these skills inside Claude Code:

| Command             | Purpose                               |
|---------------------|---------------------------------------|
| `/process-inbox`    | Process all items in /Needs_Action    |
| `/update-dashboard` | Refresh Dashboard.md with live stats  |
| `/triage-item`      | Triage a specific item                |

---

## Project Structure

```
Hackathon 0/
├── AI_Employee_Vault/          ← Obsidian vault (the AI's brain)
│   ├── Inbox/                  ← Drop files here
│   ├── Needs_Action/           ← Auto-generated action items
│   ├── Pending_Approval/       ← Items needing human review
│   ├── Plans/                  ← Claude's task plans
│   ├── Done/                   ← Completed items
│   ├── Logs/                   ← Daily action logs
│   ├── Dashboard.md            ← Live overview
│   └── Company_Handbook.md     ← Rules of engagement
├── watchers/
│   ├── base_watcher.py         ← Abstract base class
│   └── filesystem_watcher.py   ← File drop watcher (Bronze tier)
├── .claude/
│   └── skills/
│       ├── process-inbox.md    ← Agent skill: process vault items
│       ├── update-dashboard.md ← Agent skill: refresh dashboard
│       └── triage-item.md      ← Agent skill: triage a single item
├── CLAUDE.md                   ← Claude Code configuration & instructions
├── requirements.txt
└── README.md
```

---

## Architecture

```
[User drops file]
      │
      ▼
AI_Employee_Vault/Inbox/
      │
      ▼ (filesystem_watcher.py detects it)
AI_Employee_Vault/Needs_Action/FILE_*.md
      │
      ▼ (/process-inbox skill)
[Claude reads Company_Handbook.md]
      │
      ├─ Low risk → Execute → Move to /Done/
      └─ Needs approval → Move to /Pending_Approval/
                              │
                              ▼ (human reviews)
                         /Approved/ or /Rejected/
```

---

## Tier Checklist

### Bronze Tier ✅

- [x] Obsidian vault with `Dashboard.md` and `Company_Handbook.md`
- [x] One working Watcher script (File System Watcher)
- [x] Claude Code reading from and writing to the vault (via CLAUDE.md + skills)
- [x] Basic folder structure: `/Inbox`, `/Needs_Action`, `/Done`
- [x] All AI functionality implemented as Agent Skills

---

## Security

- Never commit `.env` files — add to `.gitignore`.
- Store API keys in environment variables only.
- See `Company_Handbook.md` for the full permission/approval matrix.

---

## Next Steps (Silver Tier)

- Add Gmail Watcher (`watchers/gmail_watcher.py`)
- Add WhatsApp Watcher (`watchers/whatsapp_watcher.py`)
- Implement Human-in-the-Loop approval orchestrator
- Add LinkedIn auto-posting skill
- Set up cron/Task Scheduler for scheduled briefings
