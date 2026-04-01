# publish-facebook-post

Execute an approved Facebook Page post via the Meta Graph API.

> **Important:** Only call this after human approval. Never invoke for unapproved drafts.

## Arguments

```
/publish-facebook-post <approval-filename>
```

The file must exist in `/Pending_Approval/` or `/Approved/` with `type: facebook_post`.

## Instructions

When invoked:

1. **Locate the approval file** in `/Pending_Approval/` or `/Approved/`.
   - If not found, report error and stop.

2. **Validate**:
   - `type` must be `facebook_post`.
   - `status` must be `pending_approval` or `approved`.
   - Extract the **Draft Post** section.

3. **Read Company_Handbook.md** to confirm posting is allowed.

4. **Publish via the Graph API** using `watchers/facebook_watcher.py`:
   ```python
   from facebook_watcher import FacebookWatcher
   watcher = FacebookWatcher(vault_path="AI_Employee_Vault")
   result = watcher.publish_post(message=post_text)
   ```

5. **Update the approval file**:
   - Set `status: done`
   - Add `published_at: <ISO timestamp>`
   - Add `post_id: <returned post ID>`
   - Add `executed_by: Claude`

6. **Move the file** to `/Done/`.

7. **Log** to `/Logs/YYYY-MM-DD.md`:
   ```
   [TIMESTAMP] [FACEBOOK_POST] Published post to Facebook Page. Post ID: <id>. Status: success.
   ```

8. **Update Dashboard.md**.

## Error Handling

- If the Graph API returns an error: set `status: failed`, log the error, leave in `/Pending_Approval/`.
- If the token is expired: set `status: failed`, log "Facebook token expired — re-authenticate."
- Never retry automatically — require fresh approval.

## Rules

- Never modify the post content — publish exactly what was approved.
- One post per invocation.
- Requires FACEBOOK_PAGE_ACCESS_TOKEN and FACEBOOK_PAGE_ID in `.env`.
