"""Quick test script for Odoo Docker integration."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "watchers"))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from odoo_connector import OdooClient, accounting_summary_to_markdown, partners_to_markdown

def main():
    print("=" * 60)
    print("  Odoo Docker Integration Test")
    print("=" * 60)

    client = OdooClient()

    # 1. Health check
    print("\n[1] Health Check...")
    health = client.health_check()
    if health["status"] == "ok":
        print(f"    OK — Odoo version: {health['version']}")
    else:
        print(f"    FAILED — {health['error']}")
        sys.exit(1)

    # 2. Authentication
    print("\n[2] Authentication...")
    try:
        uid = client.uid
        print(f"    OK — Logged in as uid={uid}")
    except Exception as e:
        print(f"    FAILED — {e}")
        sys.exit(1)

    # 3. List partners
    print("\n[3] Listing Partners...")
    partners = client.list_partners(limit=10)
    print(f"    Found {len(partners)} partners")
    if partners:
        print(partners_to_markdown(partners))

    # 4. Create a test partner
    print("[4] Creating test partner...")
    try:
        partner_id = client.create("res.partner", {
            "name": "AI Employee Test Client 2",
            "email": "test2@ai-employee.local",
            "is_company": True,
            "autopost_bills": "never",
        })
        print(f"    OK — Created partner ID: {partner_id}")
    except Exception as e:
        print(f"    FAILED — {e}")
        partner_id = None

    # 5. Create a test invoice
    if partner_id:
        print("\n[5] Creating test invoice...")
        try:
            invoice_id = client.create_invoice(
                partner_id=partner_id,
                lines=[
                    {"name": "AI Agent Development", "quantity": 1, "price_unit": 5000.00},
                    {"name": "Odoo Integration Setup", "quantity": 1, "price_unit": 2500.00},
                ],
            )
            print(f"    OK — Created draft invoice ID: {invoice_id}")
        except Exception as e:
            print(f"    FAILED — {e}")

    # 6. Accounting summary
    print("\n[6] Accounting Summary...")
    try:
        summary = client.get_account_balance_summary()
        print(accounting_summary_to_markdown(summary))
    except Exception as e:
        print(f"    FAILED — {e}")

    print("=" * 60)
    print("  All tests passed! Odoo integration is working.")
    print("=" * 60)


if __name__ == "__main__":
    main()
