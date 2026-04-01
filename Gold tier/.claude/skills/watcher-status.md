# watcher-status

Check the operational status of all AI Employee watcher scripts and report a live health summary.

## Arguments

```
/watcher-status [watcher-name]
```

Optional: specify a single watcher (`filesystem`, `gmail`, `whatsapp`) to check just that one.
If omitted, report status of all watchers.

## Instructions

When invoked:

1. **Read the orchestrator status file** at `<vault-root>/watcher_status.json` (written every 15s by `orchestrator.py`):
   - If the file exists and was updated within the last 2 minutes, use it as the primary source of truth.
   - If the file does not exist or is stale (>2 minutes old), the orchestrator is likely not running.

2. **Check for recent activity** as a secondary health signal:
   - Scan `/Needs_Action/` for files created in the last 30 minutes — indicates watchers are producing output.
   - Check `/Logs/YYYY-MM-DD.md` for recent watcher-related log entries.

3. **Check processed-IDs files**:
   - `/AI_Employee_Vault/.gmail_processed_ids.json` — last-modified time shows when Gmail watcher last ran.
   - `/AI_Employee_Vault/.whatsapp_processed.json` — same for WhatsApp.

4. **Determine status for each watcher**:

   | Signal | Status Interpretation |
   |--------|-----------------------|
   | `watcher_status.json` is fresh + watcher shows `running` | ✅ Running |
   | `watcher_status.json` is fresh + watcher shows `exited(...)` | ⚠️ Crashed — may be auto-restarting |
   | `watcher_status.json` is stale or missing | ❌ Orchestrator not running |
   | Recent `/Needs_Action/` files from that watcher | ✅ Active (even if status unknown) |
   | No activity in 60+ minutes | ⚠️ Possibly stalled |

5. **Present a formatted status report**:

```
## Watcher Status — <date/time>

| Watcher    | Status   | PID   | Last Activity         | Notes |
|------------|----------|-------|-----------------------|-------|
| filesystem | ✅ Running | 12345 | 2026-03-02 10:15      | —     |
| gmail      | ✅ Running | 12346 | 2026-03-02 09:58      | —     |
| whatsapp   | ⚠️ Crashed | —     | 2026-03-02 08:30      | Restarting |

**Orchestrator:** ✅ Active (watcher_status.json updated 45s ago)

### Recent Items Produced
- 3 email action files (last 2h)
- 1 WhatsApp action file (last 1h)
- 0 filesystem drop items (last 2h)

### Recommendations
- ✅ All watchers healthy.
  OR
- ⚠️ Gmail watcher appears stalled. Try: `python watchers/gmail_watcher.py --vault AI_Employee_Vault`
- ❌ Orchestrator not running. Start with: `python watchers/orchestrator.py --vault AI_Employee_Vault`
```

6. **If any watcher is down**, provide the exact restart command:
   - Orchestrator (recommended — restarts all): `python watchers/orchestrator.py --vault AI_Employee_Vault`
   - Individual watchers:
     - `python watchers/filesystem_watcher.py --vault AI_Employee_Vault`
     - `python watchers/gmail_watcher.py --vault AI_Employee_Vault`
     - `python watchers/whatsapp_watcher.py --vault AI_Employee_Vault`
     - WhatsApp first-time setup: `python watchers/whatsapp_watcher.py --vault AI_Employee_Vault --setup`

7. **Log the status check** in `/Logs/YYYY-MM-DD.md` (brief one-liner only).

8. **Update Dashboard.md** System Status table with current watcher states.

## Rules

- This skill is read-only — it only reports status and does not restart processes.
- Do not attempt to start or stop watcher processes — that requires shell access the user must perform.
- If `watcher_status.json` is missing, do not assume watchers are running — always say "status unknown."
- Keep the report concise — one table row per watcher, plus actionable recommendations.

## Example Usage

```
/watcher-status
/watcher-status gmail
/watcher-status filesystem
```
