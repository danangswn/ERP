from distributor_core.distributor_core.utils.terbilang import terbilang

import frappe


def get_context(context):
    context.doc = frappe.get_doc(frappe.form_dict.doctype, frappe.form_dict.name)
    context.terbilang = terbilang(context.doc.grand_total) if hasattr(context.doc, "grand_total") else ""
