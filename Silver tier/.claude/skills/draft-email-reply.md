# draft-email-reply

Draft a professional email reply to a specific email action file and queue it for human approval before sending.

## Arguments

```
/draft-email-reply <filename> [--tone <professional|friendly|formal>]
```

- `<filename>`: The email action file in `/Needs_Action/` or `/Done/` to reply to.
- `--tone`: Optional tone override. Default is `professional`. Choices: `professional`, `friendly`, `formal`.

If no filename is provided, draft a reply for the most recent unprocessed email in `/Needs_Action/`.

## Instructions

When invoked:

1. **Locate the target email file**:
   - Check `/Needs_Action/` for a file with `type: email`.
   - If no filename given, use the oldest pending email (`status: pending`).
   - If still not found, report "No email found to reply to."

2. **Read the email action file** fully:
   - Extract: sender, subject, received_at, message snippet/summary.
   - Understand the core ask or context of the email.

3. **Read Company_Handbook.md**:
   - Check email communication rules (Section 4).
   - Verify the sender is a known contact or determine if extra caution is needed.
   - Apply tone and content guidelines.

4. **Reason through the appropriate reply**:
   - What is the sender asking or communicating?
   - What is the ideal response that serves the business relationship?
   - Does the reply require any information you don't have? If so, note it as a placeholder `[FILL IN: ...]`.
   - Keep the reply concise (3–5 sentences for simple replies; structured paragraphs for complex ones).

5. **Draft the reply**:

   Structure:
   - **Greeting**: Address the sender by first name.
   - **Acknowledgement**: Briefly acknowledge what they said/asked.
   - **Response**: Answer clearly and helpfully.
   - **Next step / CTA**: What happens next (e.g., "I'll follow up by Friday", "Please find the attached…").
   - **Sign-off**: Professional closing with the owner's name.

   Tone guidelines:
   - `professional`: Polished, clear, no slang. Suitable for most business contacts.
   - `friendly`: Warm and conversational. Suitable for regular clients.
   - `formal`: Conservative and precise. Suitable for legal, financial, or official contexts.

6. **Create an approval file** in `/Pending_Approval/` named `APPROVAL_REQUIRED_Email_Reply_<sender-safe>_<YYYYMMDD>.md`:

```markdown
---
created: <ISO timestamp>
type: email_reply
original_email: "<original filename>"
to: "<sender email>"
subject: "Re: <original subject>"
status: pending_approval
risk: medium
tone: <tone>
---

## Action Requested
Send the following email reply to **<sender name>** at `<sender email>`.

## Original Email Summary
- **From:** <sender>
- **Subject:** <subject>
- **Key points:** <2–3 bullet summary of what they said>

## Draft Reply

**To:** <sender email>
**Subject:** Re: <original subject>

---

<greeting>,

<reply body — 3–5 sentences or structured paragraphs>

<sign-off>,
[Your Name]

---

## Reasoning
<Why this reply was written this way — what goal it serves>

## Placeholders to Fill
<List any [FILL IN: ...] items that need human input before sending>

## To Approve
Move this file to `/Approved/` or run `/approve-item <filename>`.

## To Reject
Set `status: rejected` and add a note explaining what to change.
```

7. **Update the original email action file**:
   - Set `status: awaiting_approval`
   - Add `## Processing Notes` referencing the approval file name.

8. **Log the draft** in `/Logs/YYYY-MM-DD.md`:
   ```
   [TIMESTAMP] [EMAIL_DRAFT] Drafted reply for <subject> from <sender>. Approval file: <filename>.
   ```

9. **Update Dashboard.md** counts.

## Rules

- Never send an email autonomously — always create an approval file.
- If the email appears to be spam or requires no reply, report this and do NOT draft.
- Do not include confidential business data (pricing tiers, client names) unless it was in the original email.
- If the original email is a financial request (invoice, payment), escalate instead of drafting (`status: needs_human`).
- Keep placeholders `[FILL IN: ...]` visible — do not guess at missing information.

## Example Usage

```
/draft-email-reply EMAIL_20260302T083000_invoice_request.md
/draft-email-reply EMAIL_20260302T083000_intro_email.md --tone friendly
/draft-email-reply
```
