frappe.ui.form.on("Bukti Potong PPh 23", {
	refresh(frm) {
		// tax base defaults to the supplier invoice grand total
		if (frm.is_new() && frm.doc.supplier_invoice && !frm.doc.tax_base) {
			frappe.db.get_value(
				"Purchase Invoice",
				frm.doc.supplier_invoice,
				"base_grand_total",
				(r) => frm.set_value("tax_base", r.base_grand_total)
			);
		}
	},
});
