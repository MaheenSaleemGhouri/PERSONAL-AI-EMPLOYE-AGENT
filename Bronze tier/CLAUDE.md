# AI Employee — Claude Code Configuration

## Project Overview

This is a **Personal AI Employee** built for the Hackathon 0 (Bronze Tier).
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

| Skill              | Command             | Purpose                              |
|--------------------|---------------------|--------------------------------------|
| Process Inbox      | `/process-inbox`    | Process all items in /Needs_Action   |
| Update Dashboard   | `/update-dashboard` | Refresh Dashboard.md with live stats |
| Triage Item        | `/triage-item`      | Triage a specific item               |

## Watcher Scripts

Located in `/watchers/`:

| Script                    | Monitors        | Trigger          |
|---------------------------|-----------------|------------------|
| `filesystem_watcher.py`   | /Inbox folder   | New file dropped |

### Starting the File System Watcher

```bash
# Install dependencies first
pip install -r requirements.txt

# Start the watcher (monitors AI_Employee_Vault/Inbox)
python watchers/filesystem_watcher.py

# Or specify a custom vault path
python watchers/filesystem_watcher.py --vault /path/to/AI_Employee_Vault
```

## Typical Workflow

1. File Watcher detects new file in `/Inbox/`
2. Watcher creates `.md` action file in `/Needs_Action/`
3. Run `/process-inbox` to have Claude triage and act
4. Review `/Pending_Approval/` items and approve/reject manually
5. Run `/update-dashboard` to refresh the overview

## Security Notes

- Never put API keys or passwords inside the vault.
- Use `.env` file for credentials (it is gitignored).
- See Company_Handbook.md Section 7 for full privacy rules.
