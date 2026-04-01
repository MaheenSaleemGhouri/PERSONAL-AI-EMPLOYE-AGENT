# process-whatsapp

Process action files created by the WhatsApp watcher, triage each message, and route appropriately.

## Arguments

```
/process-whatsapp [filename]
```

If a filename is given, process only that file.
If omitted, process all unprocessed WhatsApp action files in `/Needs_Action/` (type: `whatsapp`).

## Instructions

When invoked:

1. **Identify target files** in `/Needs_Action/`:
   - Filter for files with `type: whatsapp` in frontmatter.
   - Filter for `status: pending` (not yet processed).
   - Sort by `priority` (high first), then by `received_at` (oldest first).

2. **Read Company_Handbook.md** for WhatsApp handling rules:
   - What contact types are trusted VIPs?
   - Which message types require immediate escalation?
   - What auto-reply templates are permitted?
   - What actions require human approval?

3. **For each WhatsApp action file**, analyze:
   - **Contact**: Is this a known client, lead, or unknown?
   - **Message content / triggers**: Which keywords matched? What is the underlying intent?
   - **Urgency**: Is this a time-sensitive lead or business inquiry?
   - **Required action**: Reply, escalate as lead, create a plan, or ignore?

4. **Route the message** based on analysis:

   | Scenario | Action |
   |----------|--------|
   | Spam / irrelevant | Set `status: done`, note "ignored — irrelevant", move to `/Done/` |
   | General inquiry | Draft a reply for approval in `/Pending_Approval/` |
   | Active lead (pricing, hire, proposal) | Create a Plan.md via `/create-plan` for follow-up; draft reply for approval |
   | Urgent / financial / contract | Set `status: needs_human`, add triage notes, escalate |
   | Existing client request | Draft reply + create Plan.md if multi-step action needed |

5. **If drafting a reply**:
   - Create `APPROVAL_REQUIRED_WhatsApp_Reply_<contact>_<YYYYMMDD>.md` in `/Pending_Approval/` containing:
     - Original message summary (contact, triggers, key points)
     - Drafted reply text (professional, conversational, on-brand per Company_Handbook.md)
     - Reasoning for the response
     - Instructions: approve with `/approve-item`, or reject to discard
   - Draft format:

```markdown
---
created: <ISO timestamp>
type: whatsapp_reply
contact: "<contact name>"
status: pending_approval
risk: medium
---

## Action Requested
Send the following WhatsApp reply to **<contact>**.

## Original Message
> <message preview>

## Draft Reply

<reply text — keep it concise, professional, 2–4 sentences>

## Reasoning
<Why this response was chosen and what business goal it serves>

## To Approve
Move this file to `/Approved/` or run `/approve-item <filename>`.

## To Reject
Set `status: rejected` and add a note.
```

6. **Update the original action file** with:
   - `status: <done|awaiting_approval|needs_human>`
   - `## Processing Notes` section summarizing the triage decision.

7. **Move processed files** to `/Done/` (except `needs_human` items which stay in `/Needs_Action/`).

8. **Log each message's triage result** in `/Logs/YYYY-MM-DD.md`.

9. **Update Dashboard.md** counts.

## Rules

- Never reply to WhatsApp autonomously — always create an approval file first.
- Never mark a financial request or contract message as `done` without human review.
- Do not log full message content in logs — summaries only, to protect contact privacy.
- If no WhatsApp action files are found, report "No new WhatsApp items to process."
- Lead messages (pricing, hire, proposal) must always create a Plan.md for proper follow-up.

## Example Usage

```
/process-whatsapp
/process-whatsapp WHATSAPP_20260302T083000_John_Smith.md
```
