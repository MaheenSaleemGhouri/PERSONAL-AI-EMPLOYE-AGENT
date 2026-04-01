# odoo-list-partners

List customers and partners from Odoo.

## Arguments

```
/odoo-list-partners [--companies-only] [--limit N]
```

## Instructions

When invoked:

1. **Connect to Odoo** using `watchers/odoo_connector.py`.
2. **Fetch partners** using `client.list_partners()`.
3. **Display** the results in a markdown table using `partners_to_markdown()`.
4. **Save** to `/Accounting/Partners_YYYYMMDD.md` if requested.
5. **Log** to `/Logs/YYYY-MM-DD.md`.

## Rules

- Read-only operation — no data is modified.
