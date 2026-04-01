# update-dashboard

Regenerate and update the AI Employee Dashboard.md with current vault statistics.

## Instructions

When invoked:

1. **Count items** in each folder:
   - `/Inbox/` — files not yet triaged
   - `/Needs_Action/` — items pending processing
   - `/Done/` — items completed today (filter by today's date)
   - `/Pending_Approval/` — items awaiting human approval

2. **Read the Logs** directory:
   - Find today's log file (`/Logs/YYYY-MM-DD.md`).
   - Count total actions taken today.

3. **Check system status**:
   - Verify the vault folders exist and are accessible.
   - Note any items with `status: needs_human` as escalations.

4. **Rewrite Dashboard.md** with:
   - Updated "System Status" table (all components accessible = OK).
   - Updated "Inbox Summary" counts.
   - Updated "Recent Activity" (last 5 log entries, most recent first).
   - Updated "Quick Stats" for the current week.

5. Update the `last_updated` field in the frontmatter to the current ISO timestamp.

## Output Format

Preserve the existing Dashboard.md structure. Only update the data values, not the layout.

## Example Usage

```
/update-dashboard
```
