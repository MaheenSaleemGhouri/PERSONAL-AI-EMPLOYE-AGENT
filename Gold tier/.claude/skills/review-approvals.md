# review-approvals

Review all items in /Pending_Approval and present a clear human-readable summary for decision-making.

## Arguments

```
/review-approvals [filter]
```

Optional filter: `financial`, `email`, `linkedin`, `all` (default: `all`).

## Instructions

When invoked:

1. **Scan `/Pending_Approval/`** for all `.md` files with `status: pending_approval`.

2. **For each item**, extract:
   - File name
   - `type` (from frontmatter)
   - `risk` level (from frontmatter)
   - What action is being requested (from the file body)
   - Date created
   - Any linked Plan.md (if referenced)

3. **Group items by risk level** for the summary:
   - 🔴 High risk (financial transactions, contract actions)
   - 🟡 Medium risk (external communications, public posts)
   - 🟢 Low risk (internal file operations, scheduling)

4. **Present a structured summary** to the user:

```
## Pending Approvals — <date>

Total items: X

### 🔴 High Risk (X items)
1. [FILENAME] — <one-line description> | Created: <date>

### 🟡 Medium Risk (X items)
1. [FILENAME] — <one-line description> | Created: <date>

### 🟢 Low Risk (X items)
1. [FILENAME] — <one-line description> | Created: <date>

---
To approve an item: /approve-item [filename]
To reject an item: update the file's status to `rejected` manually.
```

5. **Do not auto-approve any items** — this skill is read-only and informational.

6. **Log the review** in `/Logs/YYYY-MM-DD.md`.

## Rules

- This skill only reads and summarizes — it never executes actions.
- If `/Pending_Approval/` is empty, report "No pending approvals."
- If an item has been in `/Pending_Approval/` for more than 3 days, flag it as stale.

## Example Usage

```
/review-approvals
/review-approvals financial
/review-approvals linkedin
```
