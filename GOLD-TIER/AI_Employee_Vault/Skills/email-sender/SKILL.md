---
skill_name: email-sender
version: 1.0
tier: silver
trigger: EMAIL_SEND_*.md file appears in /Approved/ folder
---

# Skill: Email Sender (MCP-Powered)

## Purpose
Send approved emails using the Gmail MCP server.

## Input
A file named `EMAIL_SEND_*.md` in the `/Approved/` folder

## Pre-Flight Checks (MANDATORY — stop if any check fails)
- [ ] File is located in /Approved/ (not /Pending_Approval/)
- [ ] Recipient is a known contact per Company_Handbook.md
- [ ] DRY_RUN status confirmed before proceeding
- [ ] Current email count is under the hourly rate limit

## Steps
1. Read the approved file: extract `to`, `subject`, and `body` fields
2. Call MCP tool: `send_email` — pass the approval file name as `approval_file`
3. On SUCCESS:
   - Update the file's `status` field to `sent`
   - Move the file to /Done/
   - Append a log entry to /Logs/YYYY-MM-DD.json
   - Update Dashboard.md (emails sent today + 1)
4. On FAILURE:
   - Log the error with full details to /Logs/
   - Move the file back to /Pending_Approval/ with an error note appended
   - Add an ALERT to Dashboard.md so the human is aware

## Hard Rules
- NEVER send to unknown or new contacts
- NEVER send bulk emails under any circumstances
- Every single send must be logged with timestamp, recipient, and subject
- If in doubt, create an approval request instead of sending
