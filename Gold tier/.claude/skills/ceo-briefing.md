# ceo-briefing

Generate a Monday Morning CEO Briefing: a proactive summary of business status, outstanding tasks, recent activity, and recommended actions.

## Arguments

```
/ceo-briefing [date-range]
```

Optional date-range: `today`, `week` (default), `month`.

## Instructions

When invoked:

1. **Read Company_Handbook.md** for business context, KPIs, and reporting preferences.

2. **Audit the vault** — collect data across all relevant folders:

   **Tasks & Actions:**
   - Count items in `/Needs_Action/` by priority (high / medium / low).
   - Count items in `/Pending_Approval/` — list each with its type and age.
   - Count items completed in `/Done/` within the date range.

   **Logs:**
   - Read all log files in `/Logs/` within the date range.
   - Count total actions taken.
   - Identify recurring issues or patterns (e.g., repeated `needs_human` escalations).

   **Plans:**
   - Scan `/Plans/` for in-progress Plan.md files.
   - Report which plans are stalled (not updated in 48+ hours).

   **Communications (if watcher data exists):**
   - Check `/Needs_Action/` for unprocessed Gmail or WhatsApp items.
   - Note any urgent or high-priority messages waiting.

3. **Identify bottlenecks**:
   - Items stuck in `needs_human` status.
   - Plans with blocked steps.
   - Approvals pending more than 2 days.

4. **Generate the briefing** and save it to `/Logs/CEO_BRIEFING_YYYYMMDD.md`:

```markdown
---
created: <ISO timestamp>
type: ceo_briefing
period: <date range>
---

# Monday Morning CEO Briefing — <Date>

## Executive Summary
<2–3 sentence high-level snapshot of business status>

## Task Pipeline
| Status           | Count |
|------------------|-------|
| Needs Action     | X     |
| Pending Approval | X     |
| Completed        | X     |
| Stalled Plans    | X     |

## Pending Approvals (Action Required)
<List each item needing human decision>

## Bottlenecks & Escalations
<List any blockers, stalled items, or recurring issues>

## Recent Wins
<Top 3–5 completed items from the period>

## Recommended Actions
1. <Specific action to take today>
2. <Specific action to take this week>
3. <Optional: schedule or delegate>

## Comms Summary
<Unread Gmail/WhatsApp items waiting, if any>
```

5. **Update Dashboard.md** with a link to the briefing and a "Last Briefing" timestamp.

6. **Append a log entry** to `/Logs/YYYY-MM-DD.md` noting the briefing was generated.

## Rules

- Do not include financial figures unless they are sourced from verified vault data.
- Do not fabricate metrics — only report what is actually in the vault.
- Keep the briefing actionable: every section should lead to a decision or next step.
- This skill is read-only (generates a report) — it does not execute actions.

## Scheduling (Recommended)

Run this automatically every Monday at 08:00 via Task Scheduler (Windows) or cron (Mac/Linux):

**Windows Task Scheduler:**
```
Action: claude "/ceo-briefing week"
Trigger: Weekly, Monday, 08:00
```

**cron (Mac/Linux):**
```
0 8 * * 1 claude "/ceo-briefing week"
```

## Example Usage

```
/ceo-briefing
/ceo-briefing week
/ceo-briefing month
```
