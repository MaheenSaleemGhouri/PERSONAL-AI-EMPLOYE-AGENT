# schedule-task

Create a scheduled recurring task that automatically runs a Claude Code skill at a specified time.
Supports Windows Task Scheduler and Unix cron.

## Arguments

```
/schedule-task <skill-name> <schedule> [--label "custom label"]
```

- `<skill-name>`: The Claude Code skill to schedule (e.g., `ceo-briefing`, `update-dashboard`, `process-inbox`)
- `<schedule>`: When to run — use natural language or cron syntax:
  - `"daily 08:00"` — every day at 8 AM
  - `"monday 08:00"` — every Monday at 8 AM
  - `"hourly"` — every hour
  - `"0 8 * * 1"` — raw cron expression (Monday 8 AM)
- `--label`: Optional human-readable name for the task

## Instructions

When invoked:

1. **Parse the arguments**:
   - Identify the skill to run and the schedule.
   - Convert natural-language schedules to cron expressions:
     | Input | Cron |
     |-------|------|
     | `daily 08:00` | `0 8 * * *` |
     | `monday 08:00` | `0 8 * * 1` |
     | `hourly` | `0 * * * *` |
     | `weekly` | `0 8 * * 1` |

2. **Detect the operating system**:
   - Check if running on Windows → use Task Scheduler.
   - Check if running on Mac/Linux → use cron.

3. **Generate the command**:
   - The command to schedule is: `claude "/<skill-name>"`
   - Run from the project directory (where CLAUDE.md lives).

4. **Create an approval file** in `/Pending_Approval/` named `APPROVAL_REQUIRED_Schedule_<skill>_<YYYYMMDD>.md` with the exact setup commands for the human to run:

```markdown
---
created: <ISO timestamp>
type: schedule_task
skill: <skill-name>
schedule: <cron expression>
status: pending_approval
risk: low
---

## Action Requested
Create a scheduled task to run `/<skill-name>` on schedule: **<human-readable schedule>**.

## Setup Commands

### Windows (Task Scheduler) — run in PowerShell as Administrator:

```powershell
$action = New-ScheduledTaskAction -Execute "claude" -Argument '"/<skill-name>"' -WorkingDirectory "<project-path>"
$trigger = New-ScheduledTaskTrigger <trigger-flags>
Register-ScheduledTask -TaskName "AIEmployee_<skill-name>" -Action $action -Trigger $trigger -RunLevel Highest
```

### Mac/Linux (cron) — run `crontab -e` and add:

```
<cron-expression> cd <project-path> && claude "/<skill-name>"
```

## Verification
After creating the task, verify it appears in Task Scheduler (Windows) or `crontab -l` (Mac/Linux).

## To Approve
Move this file to `/Approved/` or run `/approve-item <filename>` and follow the setup commands above.

## To Reject
Set `status: rejected`.
```

5. **Do NOT create the scheduled task autonomously** — output the commands and create the approval file. The human must run the commands.

   > Exception: If the user explicitly says "just do it" or the Company_Handbook grants auto-approval for scheduling, you may attempt to create the task via shell commands.

6. **If auto-executing** (explicit approval granted):
   - On Windows: run the PowerShell `Register-ScheduledTask` commands via shell.
   - On Mac/Linux: append the cron entry via `crontab -l | { cat; echo "<entry>"; } | crontab -`.
   - Log the result.

7. **Log the schedule request** in `/Logs/YYYY-MM-DD.md`.

8. **Update Dashboard.md** with the new scheduled task info.

## Common Schedules for This Project

| Use Case | Skill | Recommended Schedule |
|----------|-------|---------------------|
| Monday CEO Briefing | `ceo-briefing` | `monday 08:00` |
| Daily dashboard refresh | `update-dashboard` | `daily 07:00` |
| Hourly inbox check | `process-inbox` | `hourly` |
| Weekly LinkedIn post | `draft-linkedin-post` | `monday 09:00` |

## Rules

- Never schedule financial actions — those always require on-demand human approval.
- Use descriptive task names prefixed with `AIEmployee_` to make them easy to find.
- Always log scheduled tasks in `/Logs/`.

## Example Usage

```
/schedule-task ceo-briefing "monday 08:00"
/schedule-task update-dashboard "daily 07:00" --label "Morning Dashboard Refresh"
/schedule-task process-inbox "hourly"
```
