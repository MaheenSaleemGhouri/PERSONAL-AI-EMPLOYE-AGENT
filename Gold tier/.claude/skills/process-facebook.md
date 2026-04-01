# process-facebook

Triage Facebook and Instagram action files created by the Facebook Watcher.

## Arguments

```
/process-facebook
```

## Instructions

When invoked:

1. **Read Company_Handbook.md** for tone, rules, and escalation policies.

2. **Scan `/Needs_Action/`** for files matching `FB_*.md` patterns:
   - `FB_FACEBOOK_COMMENT_*.md` — Facebook post comments
   - `FB_FACEBOOK_MESSAGE_*.md` — Facebook Messenger messages
   - `FB_INSTAGRAM_COMMENT_*.md` — Instagram comments

3. **For each file**, read the frontmatter and content, then triage:

   **Facebook Comments:**
   - If positive/neutral → archive to `/Done/` with a note.
   - If a question → draft a reply in `/Pending_Approval/` for human review.
   - If negative/complaint → flag as high priority, create approval for response.

   **Facebook Messages (Messenger):**
   - Always high priority — these are direct customer conversations.
   - Draft a reply in `/Pending_Approval/`.
   - If contains keywords (invoice, payment, urgent, help) → escalate.

   **Instagram Comments:**
   - Same logic as Facebook comments.
   - If mentions pricing → flag for manual reply.

4. **Update each file's `status`** to `triaged`, `escalated`, or `done`.

5. **Move processed files** to `/Done/` (for archived) or `/Pending_Approval/` (for replies needing approval).

6. **Log** all actions to `/Logs/YYYY-MM-DD.md`.

7. **Update Dashboard.md** with processing stats.

## Rules

- Never reply to customers directly — always create approval files.
- Never delete incoming messages.
- Treat Messenger messages as higher priority than comments.
