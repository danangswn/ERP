# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from id_compliance.id_compliance.efaktur import generate_efaktur_csv


def execute(filters=None):
    filters = frappe._dict(filters or {})
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    columns = [
        {"label": _("Faktur Pajak No"), "fieldname": "faktur_pajak_no", "fieldtype": "Data", "width": 180},
        {"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("NPWP"), "fieldname": "customer_npwp", "fieldtype": "Data", "width": 140},
        {"label": _("DPP"), "fieldname": "dpp", "fieldtype": "Currency", "width": 140},
        {"label": _("PPN"), "fieldname": "ppn", "fieldtype": "Currency", "width": 140},
        {"label": _("CSV Row"), "fieldname": "csv_row", "fieldtype": "Data", "width": 320},
    ]

    data = []
    if from_date and to_date:
        invoices = frappe.get_all(
            "Sales Invoice",
            filters={
                "docstatus": 1,
                "posting_date": ("between", [from_date, to_date]),
                "faktur_pajak_no": ("is", "set"),
            },
            fields=["name", "customer", "posting_date", "faktur_pajak_no"],
            order_by="posting_date asc, name asc",
        )
        for row in invoices:
            doc = frappe.get_doc("Sales Invoice", row.name)
            dpp = sum(item.amount for item in (doc.get("items") or []))
            ppn = sum(
                (tax.tax_amount or 0)
                for tax in (doc.get("taxes") or [])
                if "ppn" in str(tax.account_head or "").lower()
            )
            npwp = frappe.db.get_value("Customer", row.customer, "id_npwp") or ""
            data.append(
                {
                    "faktur_pajak_no": row.faktur_pajak_no,
                    "invoice": row.name,
                    "posting_date": row.posting_date,
                    "customer": row.customer,
                    "customer_npwp": npwp,
                    "dpp": dpp,
                    "ppn": ppn,
                    "csv_row": "FM;OF;..." + str(row.faktur_pajak_no),
                }
            )

    csv_text = ""
    if from_date and to_date:
        csv_text = generate_efaktur_csv(from_date, to_date, filters.get("company"))

    return columns, data, None, {"efaktur_csv": csv_text}
