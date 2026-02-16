---
skill_name: email-triage
version: 1.0
tier: bronze
trigger: When an EMAIL_*.md file appears in /Needs_Action/
---

# Skill: Email Triage

## Purpose
Process incoming email action files and determine the correct response.

## Input
A file named `EMAIL_*.md` in the `/Needs_Action/` folder.

## Steps
1. Read the email metadata (from, subject, priority, snippet)
2. Check `Company_Handbook.md` for matching rules
3. If priority is HIGH:
   - Draft a polite reply in a new file: `/Plans/DRAFT_REPLY_<id>.md`
   - Create an approval request: `/Pending_Approval/EMAIL_SEND_<id>.md`
4. If priority is NORMAL:
   - Log to Dashboard.md
   - Move original to /Done/
5. Always update Dashboard.md

## Output Files
- `/Plans/DRAFT_REPLY_<id>.md` — Draft reply for human review
- `/Pending_Approval/EMAIL_SEND_<id>.md` — Approval gate before sending
- `/Done/EMAIL_<id>.md` — Archived original after processing

## Rules (from Company_Handbook.md)
- NEVER send email without file in /Approved/
- Always be polite and professional
- Unknown senders -> priority: low, no reply drafted

## Example Approval File Format

```
---
type: approval_request
action: send_email
to: sender@example.com
subject: "Re: <original subject>"
status: pending
---
Draft reply is in /Plans/DRAFT_REPLY_<id>.md
Move THIS file to /Approved to send, or /Rejected to cancel.
```
