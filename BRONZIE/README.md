# AI Employee — Bronze Tier (Hackathon 0)

Personal AI Employee: a local-first, autonomous agent system that monitors personal and business affairs and takes action on your behalf.

## Architecture

```
                         +------------------+
                         |   Obsidian Vault |
                         |  (Dashboard.md)  |
                         +--------+---------+
                                  |
  +----------+    +-----------+   |   +-----------+    +--------+
  |  /Inbox  | -> | Watcher   | --+-> | /Needs_   | -> | Claude |
  | (files)  |    | (Python)  |       |  Action   |    | Code   |
  +----------+    +-----------+       +-----------+    +---+----+
                                                           |
                                  +------------------------+
                                  |
                    +-------------+-------------+
                    |             |              |
              +-----+----+ +-----+-----+ +-----+-----+
              | /Plans/  | | /Pending_ | |  /Done/   |
              |          | | Approval/ | |           |
              +----------+ +-----------+ +-----------+
```

## Prerequisites

- Python 3.13+
- Node.js v24+ (for future MCP servers)
- [Obsidian](https://obsidian.md/) v1.10.6+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (latest)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Setup

```bash
# 1. Clone and enter the project
cd bronzie

# 2. Install uv (if not installed)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies
cd ai_employee
uv sync

# 4. Setup environment
cp .env.example .env
# Edit .env — set VAULT_PATH to the absolute path of AI_Employee_Vault/
# DRY_RUN=true by default (safe mode)

# 5. Open AI_Employee_Vault/ in Obsidian

# 6. Run the File System Watcher
uv run python filesystem_watcher.py

# 7. In another terminal, run the Orchestrator
uv run python orchestrator.py
```

## How to Use

1. **Drop a file** into `AI_Employee_Vault/Inbox/`
2. The **File Watcher** detects it and creates a metadata `.md` file in `/Needs_Action/`
3. The **Orchestrator** detects pending items and prepares a prompt for Claude Code
4. **Claude Code** reads the action file, checks `Company_Handbook.md`, and creates a plan in `/Plans/`
5. Actions requiring approval go to `/Pending_Approval/` — move to `/Approved/` to execute
6. Processed items are archived in `/Done/`

## Security

- `.env` is gitignored — credentials never touch GitHub
- `DRY_RUN=true` by default — no real actions until explicitly enabled
- All sensitive actions (send email, payments) require human-in-the-loop approval
- File-based approval gate: move files from `/Pending_Approval/` to `/Approved/`

## Tier Declaration

**Bronze Tier** — Minimum Viable AI Employee

## Known Limitations

- No auto-send emails or payments (by design at Bronze)
- No MCP servers (planned for Silver tier)
- Claude Code must be triggered manually or via orchestrator prompt
- Gmail watcher requires Google Cloud Console OAuth setup
- No web UI — Obsidian is the dashboard

---
*Bronze Tier — Personal AI Employee Hackathon 0 | Panaversity 2026*
