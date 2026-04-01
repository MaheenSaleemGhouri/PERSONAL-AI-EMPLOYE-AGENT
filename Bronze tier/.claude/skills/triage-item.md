# triage-item

Triage a specific item from /Inbox or /Needs_Action based on Company_Handbook.md rules.

## Arguments

Accepts an optional filename argument:
```
/triage-item [filename]
```

If no filename is provided, triage the oldest un-triaged item in /Needs_Action.

## Instructions

When invoked:

1. **Identify the target file**:
   - If a filename argument is given, find it in `/Inbox/` or `/Needs_Action/`.
   - If no argument, find the oldest file in `/Needs_Action/` with `status: pending`.

2. **Read Company_Handbook.md** to understand the rules of engagement.

3. **Analyze the item**:
   - What type is it? (email, file_drop, whatsapp, etc.)
   - What action is being requested?
   - What is the risk level? (financial, communication, file operation)

4. **Decide and act**:
   - **Low risk / auto-approvable**: Execute the action, update status to `done`, move to `/Done/`.
   - **Requires approval**: Create an approval request in `/Pending_Approval/`, update status to `awaiting_approval`.
   - **Uncertain / complex**: Update status to `needs_human`, add a `## Triage Notes` section explaining why.

5. **Log the triage decision** in `/Logs/YYYY-MM-DD.md`.

6. **Update Dashboard.md** counts.

## Output

After triaging, briefly summarize:
- What the item was
- What decision was made
- What action was taken (or what approval is needed)

## Example Usage

```
/triage-item
/triage-item FILE_20260207T093000_report.md.md
```
