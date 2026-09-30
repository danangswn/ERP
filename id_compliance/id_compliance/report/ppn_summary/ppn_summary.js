// Copyright (c) 2025, Distributor ERP Lite and contributors
// For license information, please see license.txt

frappe.query_reports["PPN Summary"] = {
	filters: [
		{
			fieldname: "period",
			label: __("Period (YYYY-MM)"),
			fieldtype: "Data",
			default: frappe.datetime.strftime(frappe.datetime.month_start(), "%Y-%m"),
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
};
