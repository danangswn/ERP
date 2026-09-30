frappe.ui.form.on("Marketplace Order Log", {
	refresh(frm) {
		if (frm.doc.linked_sales_order) {
			frm.add_custom_button(__("Open Sales Order"), () => {
				frappe.set_route("Form", "Sales Order", frm.doc.linked_sales_order);
			});
		}
	},
});
