// Copyright (c) 2025, Distributor ERP Lite and contributors
// For license information, please see license.txt

frappe.query_reports["eFaktur Export"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1,
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
	],
	formatter(value, row, column, data, default_formatter) {
		return default_formatter(value, row, column, data);
	},
};
