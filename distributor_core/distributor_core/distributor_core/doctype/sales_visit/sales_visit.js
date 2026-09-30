frappe.ui.form.on("Sales Visit", {
	refresh(frm) {
		if (frm.doc.status === "Planned") {
			frm.add_custom_button(__("Check In"), () => {
				frm.set_value("check_in", frappe.datetime.now_datetime());
				frm.set_value("status", "Checked-in");
				frm.save();
			});
		}
		if (frm.doc.status === "Checked-in") {
			frm.add_custom_button(__("Check Out"), () => {
				frm.set_value("check_out", frappe.datetime.now_datetime());
				frm.set_value("status", "Completed");
				frm.save();
			});
		}
	},
});
