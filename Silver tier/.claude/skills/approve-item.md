# approve-item

Execute the action described in a specific approved item from /Pending_Approval.

## Arguments

```
/approve-item <filename>
```

The filename must exist in `/Pending_Approval/`. This skill executes the action and completes the workflow.

## Instructions

When invoked:

1. **Locate the file** in `/Pending_Approval/` matching the given filename.
   - If not found, report the error and stop.

2. **Read Company_Handbook.md** to verify the action is still within policy.

3. **Re-read the approval file** to understand:
   - What exact action is to be taken.
   - Any parameters (recipient, content, amount, etc.).
   - The `type` and `risk` level.

4. **Confirm the item is approvable**:
   - `status` must be `pending_approval` (not `rejected` or `done`).
   - Risk level must be consistent with what Claude can execute (i.e., not a financial transaction unless explicitly delegated in Company_Handbook.md).

5. **Execute the action** based on `type`:
   - `linkedin_post`: Use the available MCP/browser tool to post the draft content to LinkedIn.
   - `email_send`: Use the email MCP server to send the drafted email.
   - `file_operation`: Perform the specified file move/write operation.
   - `schedule_task`: Create the cron/Task Scheduler entry.
   - Other: Follow the instructions in the file's "Action Requested" section.

6. **Update the approval file**:
   - Set `status: done`
   - Add `executed_at: <ISO timestamp>`
   - Add `executed_by: Claude`
   - Add a brief `## Execution Summary` section describing what was done.

7. **Move the file** from `/Pending_Approval/` to `/Done/`.

8. **If the approval file references a Plan.md**, update the corresponding step checkbox to checked.

9. **Log the execution** in `/Logs/YYYY-MM-DD.md` with: action type, file name, outcome.

10. **Update Dashboard.md** counts.

## Rules

- Never execute financial transactions (bank transfers, payments) autonomously — reject with explanation.
- If execution fails, set `status: failed`, add an error note, leave in `/Pending_Approval/`, and log the failure.
- Always log what was executed, even if it seems minor.

## Example Usage

```
/approve-item APPROVAL_REQUIRED_LinkedIn_Post_20260302.md
/approve-item APPROVAL_REQUIRED_Email_ClientA_Welcome.md
```
