import frappe


def validate_credit_limit(doc, method=None):
    """
    Sales Invoice before_submit hook: block submit when the customer's
    outstanding AR plus this invoice exceeds their IDR credit limit,
    unless the user holds the "Credit Override" role.
    """
    customer_name = doc.customer
    if not customer_name:
        return

    customer = frappe.get_doc("Customer", customer_name)
    credit_limit = customer.get("credit_limit_idr") or 0

    # No credit limit configured -> nothing to enforce.
    if not credit_limit:
        return

    if "Credit Override" in frappe.get_roles():
        return

    outstanding_ar = _get_customer_outstanding_ar(customer_name)
    grand_total = doc.grand_total or 0

    if outstanding_ar + grand_total > credit_limit:
        frappe.throw(
            frappe._(
                "Credit limit exceeded for {0}: outstanding AR {1} + invoice {2} "
                "exceeds credit limit {3}. Ask a user with the Credit Override "
                "role to submit this invoice."
            ).format(
                frappe.bold(customer_name),
                frappe.utils.fmt_money(outstanding_ar, currency="IDR"),
                frappe.utils.fmt_money(grand_total, currency="IDR"),
                frappe.utils.fmt_money(credit_limit, currency="IDR"),
            ),
            frappe.PermissionError,
        )


def _get_customer_outstanding_ar(customer):
    """
    Sum outstanding amounts of this customer's submitted, unpaid/partially
    paid Sales Invoices (excludes cancelled and fully returned invoices).
    """
    # Sum of debit minus credit against the customer's AR account is what
    # "outstanding" means here; use GL Entries for accuracy.
    ar_account = _get_ar_account()
    conditions = ""
    if ar_account:
        conditions = " AND account = %(account)s"

    return (
        frappe.db.sql(
            f"""
            SELECT SUM(debit - credit)
            FROM `tabGL Entry`
            WHERE party_type = 'Customer'
              AND party = %(customer)s
              AND is_cancelled = 0
              {conditions}
            """,
            {"customer": customer, "account": ar_account},
        )[0][0]
        or 0.0
    )


def _get_ar_account():
    """Return the company default Accounts Receivable account, if resolvable."""
    from erpnext.accounts.utils import get_company_default

    try:
        return get_company_default("default_receivable_account")
    except Exception:
        # No company setup or account missing; fall back to any AR account.
        return frappe.db.get_value(
            "Account",
            {"account_type": "Receivable", "is_group": 0},
            "name",
        )
