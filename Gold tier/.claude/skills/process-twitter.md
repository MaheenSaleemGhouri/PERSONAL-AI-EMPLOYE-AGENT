# process-twitter

Triage Twitter/X mention action files created by the Twitter Watcher.

## Arguments

```
/process-twitter
```

## Instructions

When invoked:

1. **Read Company_Handbook.md** for tone and escalation rules.

2. **Scan `/Needs_Action/`** for `TWITTER_MENTION_*.md` files.

3. **For each file**, triage:
   - Positive mention → archive to `/Done/` with note.
   - Question or inquiry → draft reply in `/Pending_Approval/`.
   - Complaint or negative → flag high priority, draft careful response in `/Pending_Approval/`.
   - Spam/irrelevant → archive to `/Done/`.

4. **Update status** in each file.
5. **Move** processed files appropriately.
6. **Log** to `/Logs/YYYY-MM-DD.md`.
7. **Update Dashboard.md**.

## Rules

- Never reply to tweets directly — always create approval files.
- Never delete or hide mentions.
- Keep reply drafts under 280 characters.
