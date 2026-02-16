# odoo_watcher.py — Monitor Odoo for new transactions and create accounting action files
# Odoo Community must be running locally at ODOO_URL

import xmlrpc.client
from base_watcher import BaseWatcher
from audit_logger import log_action
from error_handler import with_retry, PermanentError
from pathlib import Path
from datetime import datetime, timedelta
import os


class OdooWatcher(BaseWatcher):
    def __init__(self, vault_path: str = None):
        super().__init__(vault_path, check_interval=3600)  # Check every hour
        self.odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.odoo_db = os.getenv('ODOO_DB', '')
        self.odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        self.odoo_password = os.getenv('ODOO_PASSWORD', '')
        self.accounting_dir = self.vault_path / 'Accounting'
        self.accounting_dir.mkdir(parents=True, exist_ok=True)
        self.uid = None
        self._authenticate()
        self.logger.info("Odoo Watcher initialized")

    @with_retry(max_attempts=3, base_delay=2)
    def _authenticate(self):
        """Authenticate with Odoo via XML-RPC"""
        if not self.odoo_db or not self.odoo_password:
            self.logger.warning("Odoo credentials not configured — watcher in standby mode")
            return
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.odoo_db, self.odoo_username, self.odoo_password, {})
            if self.uid:
                self.logger.info(f"Odoo authenticated | UID: {self.uid}")
            else:
                raise PermanentError("Odoo authentication failed — check credentials in .env")
        except Exception as e:
            self.logger.error(f"Odoo connection error: {e}")
            self.uid = None

    def check_for_updates(self) -> list:
        """Fetch new transactions from Odoo from the last 24 hours"""
        if not self.uid:
            return []
        try:
            models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            invoices = models.execute_kw(
                self.odoo_db, self.uid, self.odoo_password,
                'account.move', 'search_read',
                [[['write_date', '>=', yesterday], ['move_type', 'in', ['out_invoice', 'in_invoice']]]],
                {'fields': ['name', 'partner_id', 'amount_total', 'state', 'move_type', 'invoice_date']}
            )
            return invoices
        except Exception as e:
            self.logger.error(f"Odoo fetch error: {e}")
            return []

    def create_action_file(self, invoice: dict) -> Path:
        """Create an accounting action file for a new Odoo transaction"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        inv_name = invoice.get('name', 'Unknown').replace('/', '_')
        filename = f"ODOO_{timestamp}_{inv_name}.md"
        filepath = self.needs_action / filename

        amount = invoice.get('amount_total', 0)
        flagged = amount > 100
        move_type = invoice.get('move_type', '')
        type_label = "Customer Invoice" if move_type == 'out_invoice' else "Vendor Bill"
        partner = invoice.get('partner_id', ['', 'Unknown'])[1] if invoice.get('partner_id') else 'Unknown'

        content = f"""---
type: odoo_transaction
invoice_name: {invoice.get('name', 'Unknown')}
partner: "{partner}"
amount: {amount}
transaction_type: {type_label}
state: {invoice.get('state', 'unknown')}
flagged_for_review: {flagged}
received: {datetime.now().isoformat()}
status: pending
dry_run: {self.dry_run}
---

# Odoo Transaction: {invoice.get('name', 'Unknown')}

**Type:** {type_label}
**Partner:** {partner}
**Amount:** ${amount:,.2f}
**Status:** {invoice.get('state', 'unknown').title()}
{'**FLAGGED:** Amount exceeds $100 — requires human review' if flagged else ''}

## Instructions for Claude Code
1. Read Company_Handbook.md Odoo Accounting Rules
2. Update /Accounting/Current_Month.md with this transaction
3. If flagged -> add to CEO Briefing flagged transactions section
4. If it is a draft invoice -> create approval request in /Pending_Approval/
5. Log this action via audit_logger
6. Update Dashboard.md Odoo section
7. Move this file to /Done/

## Rule Reminder
- NEVER post invoices or record payments without human approval
- ONLY create draft invoices via Odoo MCP
"""
        filepath.write_text(content, encoding='utf-8')
        log_action(
            action_type="odoo_transaction_detected",
            actor="odoo_watcher",
            target=invoice.get('name', 'Unknown'),
            parameters={"amount": amount, "type": move_type, "partner": partner},
            approval_status="auto_detected",
            result="action_file_created"
        )
        self.logger.info(f"Odoo action file: {filename} | Amount: ${amount:,.2f}")
        return filepath


if __name__ == "__main__":
    watcher = OdooWatcher()
    watcher.run()
