# publish-linkedin-post

Execute an approved LinkedIn post by navigating to LinkedIn via Playwright and publishing the content.

> **Important:** This skill executes the actual post. It should only be called after human approval
> (either via `/approve-item` or directly). Never invoke this for unapproved drafts.

## Arguments

```
/publish-linkedin-post <approval-filename>
```

The filename must exist in `/Pending_Approval/` or `/Approved/` with `type: linkedin_post`.

## Instructions

When invoked:

1. **Locate the approval file**:
   - Check `/Pending_Approval/` then `/Approved/` for the given filename.
   - If not found, report the error and stop.

2. **Validate the file**:
   - `type` must be `linkedin_post`.
   - `status` must be `pending_approval` or `approved` — never `rejected` or `done`.
   - Extract the **Draft Post** section (the full post text to publish).

3. **Read Company_Handbook.md** to confirm posting is allowed right now (check working hours / content rules).

4. **Use the Playwright browsing skill** to publish:

   a. Navigate to `https://www.linkedin.com`
   b. Verify you are logged in (look for the home feed or profile nav item).
      - If not logged in, stop and set `status: failed` with note "LinkedIn session not active."
   c. Click the **"Start a post"** button (or equivalent compose area).
   d. Type the draft post content into the compose area.
   e. Review: confirm the visible text matches the draft exactly (no truncation).
   f. Click the **"Post"** button to publish.
   g. Wait for the confirmation message (e.g., "Your post has been shared").
   h. Take a screenshot and save it to `/Logs/linkedin_post_<YYYYMMDD_HHMMSS>.png`.

5. **Update the approval file**:
   - Set `status: done`
   - Add `published_at: <ISO timestamp>`
   - Add `executed_by: Claude`
   - Add a `## Execution Summary` section: "Post published successfully. Screenshot saved to /Logs/."

6. **Move the file** from `/Pending_Approval/` (or `/Approved/`) to `/Done/`.

7. **Log the action** in `/Logs/YYYY-MM-DD.md`:
   ```
   [TIMESTAMP] [LINKEDIN_POST] Published post to LinkedIn. File: <filename>. Status: success.
   ```

8. **Update Dashboard.md** — decrement pending approvals count, add to recent activity.

## Error Handling

- If LinkedIn navigation fails or the page does not load: set `status: failed`, log the error, leave in `/Pending_Approval/`.
- If the post text field is not found: set `status: failed`, log "Could not locate LinkedIn compose area."
- If the Post button is not found after typing: do NOT retry — leave `status: failed`, log the issue.
- Never retry a failed post automatically — always require fresh human approval.

## Rules

- This skill requires an active LinkedIn browser session (already logged in via Playwright profile).
- Never modify the post content — publish exactly what was approved.
- If the post is over LinkedIn's character limit (3,000 chars), truncate at the last full sentence before the limit and add "…" — then log the truncation.
- Do not click "Anyone" visibility controls — use whatever default is set.
- One post per invocation — never batch-post.

## Example Usage

```
/publish-linkedin-post APPROVAL_REQUIRED_LinkedIn_Post_20260302.md
```

## Notes for Setup

The LinkedIn session must be pre-authenticated. First time:
1. Run the `browsing-with-playwright` skill to open a browser.
2. Navigate to `https://www.linkedin.com` and log in manually.
3. Save the session/profile so subsequent headless runs reuse it.
