import frappe


def update_visit_statuses():
    """Daily scheduled job: cancel stale Planned visits older than 7 days."""
    stale = frappe.get_all(
        "Sales Visit",
        filters={"status": "Planned"},
        fields=["name"],
    )
    today = frappe.utils.getdate(frappe.utils.today())
    for visit in stale:
        doc = frappe.get_doc("Sales Visit", visit.name)
        created = frappe.utils.getdate(doc.creation)
        if (today - created).days > 7:
            doc.status = "Cancelled"
            doc.save(ignore_permissions=True)
