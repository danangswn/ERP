# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class SalesVisit(Document):
	def validate(self):
		self.validate_checkout_before_complete()

	def validate_checkout_before_complete(self):
		if self.status == "Completed" and not self.check_in:
			frappe.throw(_("Cannot complete a visit without checking in first."))
