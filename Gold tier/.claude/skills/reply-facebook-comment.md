# reply-facebook-comment

Reply to a Facebook or Instagram comment after human approval.

> **Important:** Only call this after human approval. Never reply without approval.

## Arguments

```
/reply-facebook-comment <approval-filename>
```

The file must exist in `/Approved/` with `type: facebook_comment_reply` or `type: instagram_comment_reply`.

## Instructions

When invoked:

1. **Locate the approval file** in `/Approved/`.
   - If not found, check `/Pending_Approval/` — if there but not approved, report and stop.

2. **Validate**:
   - `type` must be `facebook_comment_reply` or `instagram_comment_reply`.
   - `status` must be `approved`.
   - Extract the **Reply Text** and **comment_id** from frontmatter.

3. **Execute the reply** using the appropriate method:

   For Facebook comments:
   ```python
   from facebook_watcher import FacebookWatcher
   watcher = FacebookWatcher(vault_path="AI_Employee_Vault")
   result = watcher.reply_to_comment(comment_id=comment_id, message=reply_text)
   ```

   For Instagram comments:
   ```python
   result = watcher.reply_to_instagram_comment(comment_id=comment_id, message=reply_text)
   ```

4. **Update the approval file**:
   - Set `status: done`
   - Add `replied_at: <ISO timestamp>`
   - Add `executed_by: Claude`

5. **Move the file** to `/Done/`.

6. **Log** to `/Logs/YYYY-MM-DD.md`:
   ```
   [TIMESTAMP] [SOCIAL_REPLY] Replied to <platform> comment <comment_id>. Status: success.
   ```

7. **Update Dashboard.md**.

## Error Handling

- If the Graph API returns an error: set `status: failed`, log the error.
- If comment not found (deleted): set `status: failed`, log "Comment no longer exists."
- Never retry — require fresh approval.

## Rules

- Never modify the reply text — send exactly what was approved.
- One reply per invocation.
- Requires FACEBOOK_PAGE_ACCESS_TOKEN in `.env`.
