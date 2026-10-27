import xmlrpc.client
import os
from dotenv import load_dotenv

load_dotenv()

def get_outstanding_invoices():

    url = os.getenv("ODOO_URL")
    db = os.getenv("ODOO_DB")
    username = os.getenv("ODOO_USER")
    password = os.getenv("ODOO_PASSWORD")

    if not all([url, db, username, password]):
        raise ValueError("Missing one or more ODOO_* environment variables.")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if not uid:
        raise ValueError("Failed to authenticate with Odoo.")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    invoices = models.execute_kw(
        db,
        uid,
        password,
        "account.move",
        "search_read",
        [[
            ("move_type", "=", "out_invoice"),
            ("state", "=", "posted"),
            ("amount_residual", ">", 0)
        ]],
        {
            "fields": [
                "name",
                "partner_id",
                "invoice_date_due",
                "amount_residual"
            ]
        }
    )

    return invoices
