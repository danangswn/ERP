# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PriceTier(Document):
	def validate(self):
		self.validate_duplicate_item_groups()
		self.validate_discount_range()

	def validate_duplicate_item_groups(self):
		seen = set()
		for row in self.item_groups or []:
			if row.item_group in seen:
				frappe.throw(
					_("Item Group {0} appears more than once in tier {1}.").format(
						frappe.bold(row.item_group), frappe.bold(self.tier_name or self.name)
					)
				)
			seen.add(row.item_group)

	def validate_discount_range(self):
		if self.discount_percent is not None and not (0 <= self.discount_percent <= 100):
			frappe.throw(_("Discount percent must be between 0 and 100."))
