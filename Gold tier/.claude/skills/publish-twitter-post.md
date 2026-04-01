# publish-twitter-post

Execute an approved tweet via the Twitter API v2.

> Only call after human approval.

## Arguments

```
/publish-twitter-post <approval-filename>
```

## Instructions

When invoked:

1. **Locate** the approval file in `/Pending_Approval/` or `/Approved/`.
2. **Validate**: `type` = `twitter_post`, `status` = `pending_approval` or `approved`.
3. **Extract** the Draft Tweet text. Verify it is ≤280 characters.
4. **Publish** via `watchers/twitter_watcher.py`:
   ```python
   from twitter_watcher import TwitterWatcher
   watcher = TwitterWatcher(vault_path="AI_Employee_Vault")
   result = watcher.post_tweet(text=tweet_text)
   ```
5. **Update** the approval file: `status: done`, `tweet_id`, `published_at`.
6. **Move** to `/Done/`.
7. **Log** to `/Logs/YYYY-MM-DD.md`.
8. **Update Dashboard.md**.

## Error Handling

- API error → `status: failed`, log error, leave in `/Pending_Approval/`.
- Rate limited → `status: failed`, log "Rate limited — retry later."
- Never retry automatically.

## Rules

- Publish exactly what was approved — no modifications.
- One tweet per invocation.
- Requires all TWITTER_* env vars set in `.env`.
