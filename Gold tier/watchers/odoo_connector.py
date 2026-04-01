"""
odoo_connector.py — Odoo JSON-RPC Client for AI Employee (Gold Tier)

Provides a Python client for Odoo 19 Community Edition via JSON-RPC.
Used by skills and watchers to read/write accounting data.

Usage:
    from odoo_connector import OdooClient

    client = OdooClient(
        url="http://localhost:8069",
        db="ai_employee",
        username="admin@example.com",
        password="admin",
    )
    partners = client.search_read("res.partner", [("is_company", "=", True)], ["name", "email"])
"""

import json
import logging
import os
import requests
from datetime import datetime, date
from typing import Any

logger = logging.getLogger("OdooConnector")

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class OdooClient:
    """Lightweight Odoo JSON-RPC client for Odoo 19+."""

    def __init__(
        self,
        url: str | None = None,
        db: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        self.url = (url or os.getenv("ODOO_URL", "http://localhost:8069")).rstrip("/")
        self.db = db or os.getenv("ODOO_DB", "ai_employee")
        self.username = username or os.getenv("ODOO_USER", "admin")
        self.password = password or os.getenv("ODOO_PASSWORD", "admin")
        self._uid: int | None = None
        self._request_id = 0

    # ── Low-level JSON-RPC ───────────────────────────────────────

    def _jsonrpc(self, service: str, method: str, args: list) -> Any:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args,
            },
            "id": self._request_id,
        }
        resp = requests.post(
            f"{self.url}/jsonrpc",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        if "error" in result:
            err = result["error"]
            msg = err.get("data", {}).get("message", err.get("message", str(err)))
            raise RuntimeError(f"Odoo RPC error: {msg}")
        return result.get("result")

    # ── Authentication ───────────────────────────────────────────

    @property
    def uid(self) -> int:
        if self._uid is None:
            self._uid = self._jsonrpc(
                "common", "login", [self.db, self.username, self.password]
            )
            if not self._uid:
                raise RuntimeError(
                    f"Odoo authentication failed for {self.username}@{self.db}"
                )
            logger.info(f"Authenticated as uid={self._uid}")
        return self._uid

    def version(self) -> dict:
        return self._jsonrpc("common", "version", [])

    # ── ORM wrappers ─────────────────────────────────────────────

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        return self._jsonrpc(
            "object",
            "execute_kw",
            [self.db, self.uid, self.password, model, method, list(args), kwargs],
        )

    def search(self, model: str, domain: list, **kw) -> list[int]:
        return self._execute(model, "search", domain, **kw)

    def read(self, model: str, ids: list[int], fields: list[str]) -> list[dict]:
        return self._execute(model, "read", ids, {"fields": fields})

    def search_read(
        self, model: str, domain: list, fields: list[str], limit: int = 100, order: str = ""
    ) -> list[dict]:
        kw: dict[str, Any] = {"fields": fields, "limit": limit}
        if order:
            kw["order"] = order
        return self._execute(model, "search_read", domain, **kw)

    def create(self, model: str, values: dict) -> int:
        return self._execute(model, "create", values)

    def write(self, model: str, ids: list[int], values: dict) -> bool:
        return self._execute(model, "write", ids, values)

    def unlink(self, model: str, ids: list[int]) -> bool:
        return self._execute(model, "unlink", ids)

    def fields_get(self, model: str, attributes: list[str] | None = None) -> dict:
        attrs = attributes or ["string", "type", "required"]
        return self._execute(model, "fields_get", attributes=attrs)

    # ── Accounting Helpers ───────────────────────────────────────

    def list_partners(self, company_only: bool = False, limit: int = 50) -> list[dict]:
        domain = [("is_company", "=", True)] if company_only else []
        return self.search_read(
            "res.partner", domain, ["name", "email", "phone", "is_company"], limit=limit
        )

    def list_invoices(
        self,
        state: str = "posted",
        move_type: str = "out_invoice",
        limit: int = 50,
    ) -> list[dict]:
        domain = [("move_type", "=", move_type), ("state", "=", state)]
        return self.search_read(
            "account.move",
            domain,
            ["name", "partner_id", "amount_total", "amount_residual", "state", "invoice_date", "invoice_date_due"],
            limit=limit,
            order="invoice_date desc",
        )

    def create_invoice(
        self,
        partner_id: int,
        lines: list[dict],
        move_type: str = "out_invoice",
    ) -> int:
        """Create a draft invoice.

        Args:
            partner_id: Odoo partner (customer) ID.
            lines: List of dicts with keys: name, quantity, price_unit.

        Returns:
            The new account.move ID.
        """
        invoice_lines = []
        for line in lines:
            invoice_lines.append((0, 0, {
                "name": line["name"],
                "quantity": line.get("quantity", 1),
                "price_unit": line["price_unit"],
            }))

        return self.create("account.move", {
            "move_type": move_type,
            "partner_id": partner_id,
            "invoice_date": date.today().isoformat(),
            "invoice_line_ids": invoice_lines,
        })

    def get_account_balance_summary(self) -> dict:
        """Get a high-level accounting summary: total receivable, payable, revenue."""
        # Total outstanding receivables (unpaid customer invoices)
        receivables = self.search_read(
            "account.move",
            [("move_type", "=", "out_invoice"), ("state", "=", "posted"), ("payment_state", "!=", "paid")],
            ["amount_residual"],
            limit=0,
        )
        total_receivable = sum(r["amount_residual"] for r in receivables)

        # Total outstanding payables (unpaid vendor bills)
        payables = self.search_read(
            "account.move",
            [("move_type", "=", "in_invoice"), ("state", "=", "posted"), ("payment_state", "!=", "paid")],
            ["amount_residual"],
            limit=0,
        )
        total_payable = sum(p["amount_residual"] for p in payables)

        # Revenue this month
        month_start = date.today().replace(day=1).isoformat()
        month_invoices = self.search_read(
            "account.move",
            [
                ("move_type", "=", "out_invoice"),
                ("state", "=", "posted"),
                ("invoice_date", ">=", month_start),
            ],
            ["amount_total"],
            limit=0,
        )
        month_revenue = sum(inv["amount_total"] for inv in month_invoices)

        return {
            "total_receivable": total_receivable,
            "total_payable": total_payable,
            "month_revenue": month_revenue,
            "outstanding_invoices": len(receivables),
            "outstanding_bills": len(payables),
            "as_of": datetime.now().isoformat(),
        }

    def health_check(self) -> dict:
        """Check if Odoo is reachable and return version info."""
        try:
            ver = self.version()
            return {"status": "ok", "version": ver.get("server_version", "unknown")}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ── Convenience: vault-friendly markdown export ──────────────────

def accounting_summary_to_markdown(summary: dict) -> str:
    return f"""## Accounting Summary (as of {summary['as_of'][:10]})

| Metric | Value |
|--------|-------|
| Month Revenue | ${summary['month_revenue']:,.2f} |
| Outstanding Receivables | ${summary['total_receivable']:,.2f} ({summary['outstanding_invoices']} invoices) |
| Outstanding Payables | ${summary['total_payable']:,.2f} ({summary['outstanding_bills']} bills) |
"""


def invoices_to_markdown(invoices: list[dict]) -> str:
    if not invoices:
        return "_No invoices found._\n"
    lines = ["| Invoice | Customer | Total | Due Date | Status |",
             "|---------|----------|-------|----------|--------|"]
    for inv in invoices:
        partner = inv["partner_id"][1] if isinstance(inv["partner_id"], (list, tuple)) else inv["partner_id"]
        lines.append(
            f"| {inv['name']} | {partner} | ${inv['amount_total']:,.2f} | {inv.get('invoice_date_due', 'N/A')} | {inv['state']} |"
        )
    return "\n".join(lines) + "\n"


def partners_to_markdown(partners: list[dict]) -> str:
    if not partners:
        return "_No partners found._\n"
    lines = ["| Name | Email | Phone |",
             "|------|-------|-------|"]
    for p in partners:
        lines.append(f"| {p['name']} | {p.get('email') or '—'} | {p.get('phone') or '—'} |")
    return "\n".join(lines) + "\n"
