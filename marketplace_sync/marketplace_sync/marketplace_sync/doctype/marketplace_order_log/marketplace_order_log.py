# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document

from marketplace_sync.marketplace_sync.order_import import create_sales_order_from_payload


class MarketplaceOrderLog(Document):
	def validate(self):
		if self.payload:
			try:
				json.loads(self.payload)
			except json.JSONDecodeError as exc:
				frappe.throw(_("Payload is not valid JSON: {0}").format(str(exc)))

	def on_update(self):
		# Auto-import when enabled and the log is still New.
		settings = frappe.get_cached_doc("Marketplace Settings")
		if not settings.enabled:
			return
		if self.status != "New":
			return
		import_order(self.name)


def import_order(log_name):
	"""Import a Marketplace Order Log row into a Sales Order (idempotent)."""
	log = frappe.get_doc("Marketplace Order Log", log_name)
	settings = frappe.get_cached_doc("Marketplace Settings")
	if not settings.enabled:
		return None

	if log.status == "Imported" and log.linked_sales_order:
		return log.linked_sales_order

	try:
		so_name = create_sales_order_from_payload(log)
		frappe.db.set_value(
			"Marketplace Order Log",
			log_name,
			{"status": "Imported", "linked_sales_order": so_name, "error_message": None},
		)
		return so_name
	except Exception as exc:
		frappe.db.set_value(
			"Marketplace Order Log",
			log_name,
			{"status": "Failed", "error_message": str(exc)},
		)
		raise
