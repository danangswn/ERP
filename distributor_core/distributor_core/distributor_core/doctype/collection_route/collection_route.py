# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CollectionRoute(Document):
	def validate(self):
		self.validate_unique_customers()

	def validate_unique_customers(self):
		seen = set()
		for row in self.customers or []:
			if row.customer in seen:
				frappe.throw(
					_("Customer {0} appears more than once in route {1}.").format(
						frappe.bold(row.customer), frappe.bold(self.route_name or self.name)
					)
				)
			seen.add(row.customer)
