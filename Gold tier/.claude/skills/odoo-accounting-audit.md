# odoo-accounting-audit

Pull accounting data from Odoo and generate a summary report in the vault.

## Arguments

```
/odoo-accounting-audit [period]
```

Optional period: `month` (default), `week`, `quarter`.

## Instructions

When invoked:

1. **Connect to Odoo** using `watchers/odoo_connector.py`:
   - Import `OdooClient` and `accounting_summary_to_markdown`, `invoices_to_markdown`.
   - Credentials come from `.env` (`ODOO_URL`, `ODOO_DB`, `ODOO_USER`, `ODOO_PASSWORD`).

2. **Run a health check** — if Odoo is unreachable, log the error and stop.

3. **Pull accounting data**:
   - Call `client.get_account_balance_summary()` for the financial overview.
   - Call `client.list_invoices(state="posted")` for recent invoices.
   - Call `client.list_invoices(state="posted", move_type="in_invoice")` for vendor bills.
   - Call `client.list_partners(company_only=True)` for the customer list.

4. **Generate the audit report** and save to `/Accounting/Audit_YYYYMMDD.md`:

```markdown
---
created: <ISO timestamp>
type: accounting_audit
period: <period>
source: odoo
---

# Accounting Audit — <Date>

## Financial Summary
<output of accounting_summary_to_markdown>

## Recent Customer Invoices
<output of invoices_to_markdown for out_invoices>

## Recent Vendor Bills
<output of invoices_to_markdown for in_invoices>

## Active Customers/Partners
<output of partners_to_markdown>

## Observations
<AI-generated observations: overdue invoices, revenue trends, anomalies>

## Recommended Actions
1. <specific action>
2. <specific action>
```

5. **Update Dashboard.md** with the latest accounting snapshot.

6. **Log the action** to `/Logs/YYYY-MM-DD.md`.

## Rules

- This skill is read-only against Odoo — never create, modify, or delete records.
- Do not fabricate numbers — only report what the API returns.
- Flag any invoice overdue by more than 30 days.
- Flag if total receivables exceed $10,000.
