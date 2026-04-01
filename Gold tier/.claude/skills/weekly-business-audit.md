# weekly-business-audit

Generate a comprehensive Weekly Business and Accounting Audit — the Gold tier CEO Briefing
that combines vault activity, Odoo accounting data, and social media metrics.

## Arguments

```
/weekly-business-audit [period]
```

Optional period: `week` (default), `month`, `quarter`.

## Instructions

When invoked:

1. **Read Company_Handbook.md** for KPIs, targets, and reporting preferences.

2. **Collect Vault Data** (same as `/ceo-briefing`):
   - Count items in `/Needs_Action/`, `/Pending_Approval/`, `/Done/`.
   - Read logs in `/Logs/` within the period.
   - Scan `/Plans/` for stalled plans.

3. **Pull Accounting Data from Odoo**:
   - Use `watchers/odoo_connector.py`:
     ```python
     from odoo_connector import OdooClient, accounting_summary_to_markdown, invoices_to_markdown
     client = OdooClient()
     summary = client.get_account_balance_summary()
     invoices = client.list_invoices()
     bills = client.list_invoices(move_type="in_invoice")
     ```
   - If Odoo is unreachable, note "Odoo offline" and skip accounting section.

4. **Pull Social Media Metrics** (if configured):
   - Facebook/Instagram via `watchers/facebook_watcher.py` → `generate_summary()`.
   - Twitter/X via `watchers/twitter_watcher.py` → `generate_summary()`.
   - LinkedIn from vault `/Done/` files.

5. **Generate the audit report** and save to `/Logs/Weekly_Audit_YYYYMMDD.md`:

```markdown
---
created: <ISO timestamp>
type: weekly_business_audit
period: <period>
---

# Weekly Business & Accounting Audit — <Date Range>

## Executive Summary
<3-5 sentence high-level business snapshot including financial position>

## Task Pipeline
| Status | Count |
|--------|-------|
| Needs Action | X |
| Pending Approval | X |
| Completed (period) | X |
| Stalled Plans | X |

## Financial Overview (Odoo)
<accounting_summary_to_markdown output>

### Outstanding Invoices
<invoices_to_markdown output for unpaid out_invoices>

### Outstanding Bills
<invoices_to_markdown output for unpaid in_invoices>

### Financial Health Indicators
- Cash flow status: <positive/negative/neutral>
- Overdue receivables: <count and total>
- Revenue trend: <increasing/decreasing/stable>

## Social Media Performance
| Platform | Posts | Engagement | Trend |
|----------|-------|------------|-------|
| Facebook | X | X likes/comments | ↑/↓/→ |
| Instagram | X | X likes/comments | ↑/↓/→ |
| Twitter/X | X | X likes/RTs | ↑/↓/→ |
| LinkedIn | X | — | — |

## Pending Approvals (Action Required)
<List each item needing human decision, with age and type>

## Bottlenecks & Risks
<Blockers, overdue items, stalled plans, financial risks>

## Recent Wins
<Top 5 completed items from the period>

## Recommended Actions
1. <Immediate: what to do today>
2. <This week: what to prioritize>
3. <Strategic: longer-term suggestion>

## Audit Metadata
- Report generated: <timestamp>
- Data sources: Vault, Odoo, Facebook, Twitter, LinkedIn
- Errors: <any data source failures>
```

6. **Update Dashboard.md** with latest audit summary and link.
7. **Log** to `/Logs/YYYY-MM-DD.md`.

## Error Recovery

- If Odoo is unreachable: skip financial section, note in report.
- If a social API fails: skip that platform, note in report.
- If vault data is incomplete: report what is available.
- Never fail the entire report because one data source is down.

## Rules

- Read-only — never modify external systems.
- Do not fabricate any numbers.
- Flag overdue invoices (>30 days) prominently.
- Flag receivables over $10,000.
- This report replaces `/ceo-briefing` for Gold tier.
