# process-linkedin

Process LinkedIn notification action files created by the LinkedIn watcher. Triage each notification and route to the appropriate action.

## Arguments

```
/process-linkedin [filename]
```

If a filename is given, process only that file.
If omitted, process all unprocessed LinkedIn action files in `/Needs_Action/` (type: `linkedin`).

## Instructions

When invoked:

1. **Identify target files** in `/Needs_Action/`:
   - Filter for files with `type: linkedin` in frontmatter.
   - Filter for `status: pending`.
   - Sort by `priority` (high first), then by `received_at`.

2. **Read Company_Handbook.md** for LinkedIn communication rules:
   - What tone is appropriate for LinkedIn?
   - Which notification types require a response?
   - What actions require human approval?

3. **For each LinkedIn action file**, analyze:
   - **notification_type**: message, connection, comment, mention, reaction, job, other
   - **Content**: What exactly happened? Who is it from?
   - **Business relevance**: Is this a potential lead, client, or partner?
   - **Required action**: Reply, accept, acknowledge, or ignore?

4. **Route based on notification type**:

   | Type | Action |
   |------|--------|
   | `message` | Draft a LinkedIn reply → create approval file in `/Pending_Approval/` |
   | `connection` | If relevant contact → create approval to accept; else → Done (ignored) |
   | `comment` | If on a business post → draft reply for approval; else → Done (acknowledged) |
   | `mention` | High priority — always draft a response for approval |
   | `reaction` | Log and move to Done (no response needed) |
   | `job` | If relevant → create Plan.md for evaluation; else → Done (ignored) |
   | `other` | Triage case-by-case based on content |

5. **If drafting a reply**:
   - Create `APPROVAL_REQUIRED_LinkedIn_Reply_<type>_<YYYYMMDD>.md` in `/Pending_Approval/`:

```markdown
---
created: <ISO timestamp>
type: linkedin_reply
notification_type: <type>
status: pending_approval
risk: medium
---

## Action Requested
Reply to this LinkedIn <type>.

## Original Notification
> <notification text>

## Draft Reply

<2–4 sentence professional reply>

## Reasoning
<Why this reply was drafted and what business goal it serves>

## To Approve
Move to `/Approved/` — the LinkedIn watcher will post the reply automatically.

## To Reject
Set `status: rejected`.
```

6. **Update the original action file**:
   - Set `status: <done|awaiting_approval|needs_human>`
   - Add `## Processing Notes` with the triage decision.

7. **Move processed files** to `/Done/` (except `needs_human` items).

8. **Log each notification's result** in `/Logs/YYYY-MM-DD.md`.

9. **Update Dashboard.md** counts.

## Rules

- Never reply to LinkedIn messages autonomously — always create an approval file.
- Connection requests to unknown people → always create an approval file (don't auto-accept).
- Reactions and low-priority notifications → move directly to Done with a log note.
- Do not log full message content — summaries only.

## Example Usage

```
/process-linkedin
/process-linkedin LINKEDIN_20260302T083000_MESSAGE_John_Smith.md
```
