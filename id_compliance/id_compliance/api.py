import frappe

from id_compliance.id_compliance.efaktur import generate_efaktur_csv


@frappe.whitelist()
def export_efaktur_csv(from_date, to_date, company=None):
    """
    Whitelisted API: return DJP e-Faktur CSV text for the given date range.

    Example:
        frappe.call({
            method: "id_compliance.api.export_efaktur_csv",
            args: { from_date: "2025-01-01", to_date: "2025-01-31" }
        })
    """
    if not from_date or not to_date:
        frappe.throw(frappe._("from_date and to_date are required"))

    if frappe.utils.getdate(to_date) < frappe.utils.getdate(from_date):
        frappe.throw(frappe._("to_date must be on or after from_date"))

    # only users with Accounts Manager or System Manager can export
    allowed_roles = {"Accounts Manager", "System Manager"}
    if not allowed_roles.intersection(frappe.get_roles()):
        frappe.throw(frappe._("Not permitted"), frappe.PermissionError)

    return generate_efaktur_csv(from_date, to_date, company)
