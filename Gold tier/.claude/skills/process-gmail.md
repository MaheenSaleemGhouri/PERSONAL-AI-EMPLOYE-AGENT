# process-gmail

Process action files created by the Gmail watcher, triage each email, and route appropriately.

## Arguments

```
/process-gmail [filename]
```

If a filename is given, process only that file.
If omitted, process all unprocessed Gmail action files in `/Needs_Action/` (type: `email`).

## Instructions

When invoked:

1. **Identify target files** in `/Needs_Action/`:
   - Filter for files with `type: email` in frontmatter.
   - Filter for `status: pending` (not yet processed).
   - Sort by `priority` (high first), then by `received_at` (oldest first).

2. **Read Company_Handbook.md** for email handling rules:
   - Which senders are trusted / VIP?
   - Which email types require immediate escalation?
   - What auto-replies are permitted?
   - What email actions require approval?

3. **For each email action file**, analyze:
   - **Sender**: Is this a known client, vendor, spam, or unknown?
   - **Subject & body summary**: What is being asked or communicated?
   - **Urgency**: Does the subject/body contain urgent keywords (invoice, payment, urgent, ASAP, deadline)?
   - **Required action**: Reply, forward, file, ignore, escalate?

4. **Route the email** based on analysis:

   | Scenario | Action |
   |----------|--------|
   | Spam / irrelevant | Set `status: done`, note "ignored — spam", move to `/Done/` |
   | FYI / no reply needed | Set `status: done`, note "acknowledged", move to `/Done/` |
   | Requires a reply (low-risk, templated) | Create approval file in `/Pending_Approval/` with drafted reply |
   | Client request / important task | Create a Plan.md via `/create-plan` and link it |
   | Urgent / financial / contract | Set `status: needs_human`, add triage notes, escalate |

5. **If drafting a reply**:
   - Create `APPROVAL_REQUIRED_Email_Reply_<sender>_<YYYYMMDD>.md` in `/Pending_Approval/` containing:
     - Original email summary (from, subject, key points)
     - Drafted reply text
     - Reasoning for the response
     - Instructions: approve with `/approve-item`, or reject to discard

6. **Update the original action file** with:
   - `status: <done|awaiting_approval|needs_human>`
   - `## Processing Notes` section summarizing the triage decision.

7. **Move processed files** to `/Done/` (except `needs_human` items which stay in `/Needs_Action/`).

8. **Log each email's triage result** in `/Logs/YYYY-MM-DD.md`.

9. **Update Dashboard.md** counts.

## Rules

- Never send an email autonomously — always create an approval file first.
- Never mark a financial or contract email as `done` without human review.
- If the Gmail watcher has not run recently (no new email files), report "No new Gmail items to process."
- Preserve email confidentiality — do not log full email body content, only summaries.

## Example Usage

```
/process-gmail
/process-gmail EMAIL_20260302T083000_invoice_request.md
```
