import frappe


def execute():
    """Ensure the Credit Override role exists (patch entry point)."""
    if not frappe.db.exists("Role", "Credit Override"):
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": "Credit Override",
                "desk_access": 1,
            }
        ).insert(ignore_permissions=True)
