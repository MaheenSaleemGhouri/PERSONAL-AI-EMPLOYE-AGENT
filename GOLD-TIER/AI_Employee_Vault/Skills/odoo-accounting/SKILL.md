---
skill_name: odoo-accounting
version: 1.0
tier: gold
trigger: ODOO_*.md in /Needs_Action/ OR when CEO Briefing needs financial data
---

# Skill: Odoo Accounting Integration

## Purpose
Read financial data from Odoo and update vault accounting files. Draft invoices only — never post.

## Input
- ODOO_*.md action file in /Needs_Action/
- Odoo MCP server (read + draft_invoice tools)

## Steps
1. Call MCP tool: `get_monthly_summary` to get current month totals
2. Update /Accounting/Current_Month.md with latest numbers
3. If action file is for a new invoice:
   - Call `create_draft_invoice` via Odoo MCP (DRAFT state only)
   - Save draft details to /Accounting/Invoices/DRAFT_<timestamp>.md
   - Create approval: /Pending_Approval/ODOO_INVOICE_<timestamp>.md
4. Flag any transaction over $100 in Current_Month.md
5. Log all Odoo actions via audit_logger
6. Update Dashboard.md Odoo section
7. Move original action file to /Done/

## Absolute Rules
- NEVER post invoices (state: posted) without human approval file in /Approved/
- NEVER record payments autonomously
- NEVER expose Odoo credentials in any vault file
- Every Odoo API call must be logged
