// list view settings for Sales Visit
frappe.listview_settings["Sales Visit"] = {
	filters: [["status", "!=", "Cancelled"]],
};
