# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": _("Period"), "fieldname": "period", "fieldtype": "Data", "width": 100},
        {"label": _("Tax Template"), "fieldname": "tax_template", "fieldtype": "Data", "width": 200},
        {"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
        {"label": _("Output Tax"), "fieldname": "output_tax", "fieldtype": "Currency", "width": 150},
        {"label": _("Input Tax"), "fieldname": "input_tax", "fieldtype": "Currency", "width": 150},
        {"label": _("Net Payable"), "fieldname": "net_payable", "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    period = filters.get("period")  # e.g. "2025-01"
    conditions = ""
    values = {}

    if period:
        conditions += " AND DATE_FORMAT(gl.posting_date, '%Y-%m') = %(period)s"
        values["period"] = period

    if filters.get("company"):
        conditions += " AND gl.company = %(company)s"
        values["company"] = filters.get("company")

    rows = frappe.db.sql(
        f"""
        SELECT
            DATE_FORMAT(gl.posting_date, '%Y-%m') AS period,
            tax.account_head AS account,
            SUM(tax.tax_amount) AS tax_amount
        FROM `tabSales Taxes and Charges` tax
        JOIN `tabSales Invoice` si ON si.name = tax.parent
        JOIN `tabGL Entry` gl ON gl.voucher_no = si.name AND gl.is_cancelled = 0
        WHERE si.docstatus = 1
          {conditions}
        GROUP BY period, tax.account_head
        """,
        values=values,
        as_dict=1,
    ) or []

    data = {}
    for row in rows:
        key = (row.period, row.account)
        data.setdefault(key, 0.0)
        data[key] += row.tax_amount or 0

    purchase_rows = frappe.db.sql(
        f"""
        SELECT
            DATE_FORMAT(gl.posting_date, '%Y-%m') AS period,
            tax.account_head AS account,
            SUM(tax.tax_amount) AS tax_amount
        FROM `tabPurchase Taxes and Charges` tax
        JOIN `tabPurchase Invoice` pi ON pi.name = tax.parent
        JOIN `tabGL Entry` gl ON gl.voucher_no = pi.name AND gl.is_cancelled = 0
        WHERE pi.docstatus = 1
          {conditions}
        GROUP BY period, tax.account_head
        """,
        values=values,
        as_dict=1,
    ) or []

    for row in purchase_rows:
        key = (row.period, row.account)
        data.setdefault(key, 0.0)
        data[key] -= row.tax_amount or 0

    out = []
    for (period_key, account), amount in sorted(data.items()):
        output_tax = amount if amount > 0 else 0
        input_tax = -amount if amount < 0 else 0
        out.append(
            {
                "period": period_key,
                "tax_template": account,
                "company": filters.get("company"),
                "output_tax": output_tax,
                "input_tax": input_tax,
                "net_payable": output_tax - input_tax,
            }
        )
    return out
