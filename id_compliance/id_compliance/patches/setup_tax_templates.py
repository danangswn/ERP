import frappe


def execute():
    """Create standard Indonesian tax templates if they do not exist."""
    _create_template("PPN 11% Output", 11, "Output")
    _create_template("PPN 11% Input", 11, "Input")
    _create_template("PPN 12% Output (Luxury)", 12, "Output")
    _create_template("PPN 12% Input (Luxury)", 12, "Input")
    _create_template("PPh 23 Withholding", 2, "Output")


def _create_template(title, rate, tax_type):
    if frappe.db.exists("Sales Taxes and Charges Template", title):
        return

    company = frappe.get_all("Company", limit=1, pluck="name")
    company_name = company[0] if company else None

    doc = frappe.get_doc(
        {
            "doctype": (
                "Sales Taxes and Charges Template"
                if tax_type == "Output"
                else "Purchase Taxes and Charges Template"
            ),
            "title": title,
            "company": company_name,
            "is_default": 1 if (rate == 11 and tax_type == "Output") else 0,
            "taxes": [
                {
                    "charge_type": "On Net Total",
                    "account_head": _get_tax_account(rate, company_name),
                    "rate": rate,
                    "description": f"{tax_type} VAT {rate}%",
                }
            ],
        }
    )
    doc.insert(ignore_permissions=True, ignore_mandatory=True)


def _get_tax_account(rate, company):
    """Best-effort lookup of a VAT account for the given rate."""
    candidates = frappe.get_all(
        "Account",
        filters={
            "company": company,
            "is_group": 0,
            "disabled": 0,
        },
        or_filters=[
            ["account_name", "like", f"%PPN {rate}%"],
            ["account_name", "like", f"%VAT {rate}%"],
            ["account_name", "like", "%Persediaan Barang%" if rate == 0 else "%Tax%"],
        ],
        pluck="name",
        limit=1,
    )
    return candidates[0] if candidates else None
