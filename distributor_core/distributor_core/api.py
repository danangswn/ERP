import frappe

from distributor_core.distributor_core.utils import terbilang as to_words


@frappe.whitelist()
def get_aging_reminder_text(customer):
    """
    Whitelisted API: return a Bahasa Indonesia payment-reminder text for the
    given customer's overdue invoices.

    Example:
        frappe.call({
            method: "distributor_core.api.get_aging_reminder_text",
            args: { customer: "CUST-0001" }
        })
    """
    if not customer:
        frappe.throw(frappe._("Customer is required"))

    if not frappe.db.exists("Customer", customer):
        frappe.throw(frappe._("Customer {0} not found").format(frappe.bold(customer)))

    overdue = _get_overdue_invoices(customer)

    if not overdue:
        return (
            f"Kepada Yth. {customer}, "
            "seluruh tagihan Anda saat ini sudah lunas. Terima kasih atas kerja sama Anda."
        )

    total_due = sum(inv.get("outstanding_amount") or 0 for inv in overdue)

    lines = [
        f"Kepada Yth. {customer},",
        "",
        f"Berdasarkan catatan kami, terdapat {len(overdue)} invoice jatuh tempo "
        f"dengan total outstanding sebesar Rp {total_due:,.0f}.".replace(",", "."),
        "",
        "Rincian tagihan yang jatuh tempo:",
    ]

    for inv in overdue:
        lines.append(
            "- Invoice {0} tanggal {1}, nilai outstanding Rp {2:,.0f}, "
            "sudah terlambat {3} hari.".format(
                inv.get("name"),
                inv.get("due_date"),
                (inv.get("outstanding_amount") or 0),
                (inv.get("days_overdue") or 0),
            ).replace(",", ".")
        )

    lines.append("")
    lines.append(
        "Mohon segera lakukan pembayaran atau hubungi tim penagihan kami "
        "apabila terdapat ketidaksesuaian data."
    )
    lines.append("Terima kasih atas kerja sama Anda.")

    return "\n".join(lines)


def _get_overdue_invoices(customer):
    """Fetch submitted, unpaid Sales Invoices past their due date."""
    rows = frappe.get_all(
        "Sales Invoice",
        filters={
            "customer": customer,
            "docstatus": 1,
            "outstanding_amount": (">", 0),
            "status": ("!=", "Return"),
        },
        fields=["name", "outstanding_amount", "due_date"],
        order_by="due_date asc",
    )

    today = frappe.utils.getdate(frappe.utils.today())
    overdue = []
    for row in rows:
        if not row.due_date:
            continue
        days = (today - frappe.utils.getdate(row.due_date)).days
        if days > 0:
            overdue.append({**row, "days_overdue": days})
    return overdue
