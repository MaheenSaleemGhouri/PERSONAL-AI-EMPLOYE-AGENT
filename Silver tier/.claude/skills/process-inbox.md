# process-inbox

Process all pending items in the AI Employee vault's /Needs_Action folder.

## Instructions

When invoked, you must:

1. **Read** all `.md` files currently in `/Needs_Action/` of the vault.
2. For each file:
   - Parse the YAML frontmatter to understand `type`, `priority`, and `status`.
   - Read the full content and determine what action is needed.
   - If the action is **safe and auto-approvable** (per Company_Handbook.md rules):
     - Execute the action (e.g., move a file, write a log entry).
     - Update the file's frontmatter: set `status: done`.
     - Move the file to `/Done/`.
   - If the action **requires human approval**:
     - Copy the file to `/Pending_Approval/` with `status: pending_approval`.
     - Leave original in `/Needs_Action/` with `status: awaiting_approval`.
   - If you are **uncertain**:
     - Set `status: needs_human` in the frontmatter.
     - Leave the file in `/Needs_Action/`.
3. After processing all items, **update `Dashboard.md`**:
   - Update "Inbox Summary" counts.
   - Add entries to "Recent Activity" with timestamp and summary.
4. **Append a log entry** to `/Logs/YYYY-MM-DD.md` for each item processed.

## Rules

- Read `Company_Handbook.md` before making any approval decisions.
- Never delete files — only move them between folders.
- Never take financial or email-sending actions autonomously.
- Always log what you did.

## Example Usage

```
/process-inbox
```
