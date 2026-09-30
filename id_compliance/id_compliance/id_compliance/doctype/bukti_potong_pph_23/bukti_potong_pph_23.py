# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BuktiPotongPPh23(Document):
	def validate(self):
		# PPh 23 rate is fixed at 2% per Indonesian income tax rules for
		# jasa/royalty payments subject to this withholding.
		self.rate = 2
		if self.tax_base is None:
			frappe.throw(_("Tax Base is required"))
		self.amount = (self.tax_base or 0) * (self.rate / 100)
