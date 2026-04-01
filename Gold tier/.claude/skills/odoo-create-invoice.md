# odoo-create-invoice

Create a draft invoice in Odoo and queue for human approval before posting.

## Arguments

```
/odoo-create-invoice <customer-name> <line-items>
```

- `customer-name`: Name or partial match of an Odoo partner.
- `line-items`: Comma-separated items in format `"description:quantity:price"`.

Example: `/odoo-create-invoice "Acme Corp" "Consulting:10:150, Setup Fee:1:500"`

## Instructions

When invoked:

1. **Connect to Odoo** using `watchers/odoo_connector.py`.

2. **Find the partner**:
   - Search `res.partner` for a name matching the customer-name argument.
   - If no match, list the closest 5 partners and ask the user to pick.
   - If multiple exact matches, list them and ask.

3. **Parse line items** from the argument into a list of dicts:
   ```python
   [{"name": "Consulting", "quantity": 10, "price_unit": 150.0}, ...]
   ```

4. **Calculate the total** and display a summary to the user.

5. **Create an approval file** in `/Pending_Approval/`:

```markdown
---
created: <ISO timestamp>
type: odoo_invoice
status: pending_approval
risk: high
partner_name: <name>
partner_id: <odoo id>
total_amount: <calculated total>
---

## Action Requested
Create the following draft invoice in Odoo.

## Invoice Details

| Line | Qty | Unit Price | Subtotal |
|------|-----|------------|----------|
| <line> | <qty> | $<price> | $<subtotal> |

**Total: $<total>**
**Customer: <name>**

## To Approve
Move this file to `/Approved/` to create the draft invoice in Odoo.

## To Reject
Set `status: rejected`.
```

6. **Do NOT create the invoice in Odoo yet** — wait for approval via `/approve-item`.

7. **When approved** (via approve-item skill):
   - Call `client.create_invoice(partner_id, lines)` to create a DRAFT invoice.
   - The invoice is created in draft state — it still needs to be manually confirmed/posted in Odoo.
   - Update the approval file with the new invoice ID and status.
   - Move to `/Done/`.

8. **Log the action** to `/Logs/YYYY-MM-DD.md`.

## Rules

- NEVER post/confirm an invoice automatically — only create drafts.
- Always require human approval before calling the Odoo API.
- Validate that line quantities and prices are positive numbers.
- This is a high-risk action — always create a Pending_Approval file.
