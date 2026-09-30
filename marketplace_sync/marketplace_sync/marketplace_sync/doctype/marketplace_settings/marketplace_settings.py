# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class MarketplaceSettings(Document):
	def validate(self):
		self.validate_warehouse_mapping()

	def validate_warehouse_mapping(self):
		"""Each mapping line must be key=value."""
		for line in (self.warehouse_mapping or "").splitlines():
			line = line.strip()
			if not line:
				continue
			if "=" not in line:
				frappe.throw(
					_("Invalid warehouse mapping line {0}. Expected format: key=Warehouse Name").format(
						frappe.bold(line)
					)
				)
