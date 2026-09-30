frappe.ui.form.on("Collection Route", {
	// customers are managed inline; visit_sequence can be auto-numbered on save
	validate(frm) {
		(frm.doc.customers || []).forEach((row, idx) => {
			if (!row.visit_sequence) {
				frappe.model.set_value(row.doctype, row.name, "visit_sequence", idx + 1);
			}
		});
	},
});
