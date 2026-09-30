# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

"""Idempotent marketplace order import tests (mocked frappe layer)."""

import unittest
from unittest import mock

from marketplace_sync.marketplace_sync import order_import


def _make_log(marketplace="Shopee", order_id="SHOPEE-123", payload=None):
    log = mock.Mock()
    log.marketplace = marketplace
    log.order_id = order_id
    log.payload = payload or _sample_payload(order_id)
    return log


def _sample_payload(order_id="SHOPEE-123"):
    return (
        '{"order_id": "%s", "buyer_username": "budi01", "created_at": "2025-01-15", '
        '"items": [{"item_code": "SKU-1", "qty": 2, "price": 50000}]}'
        % order_id
    )


class _FrappePatcher:
    """Patch the frappe module used inside order_import."""

    def __init__(self, case, existing_order=None):
        patcher = mock.patch.object(order_import, "frappe")
        self.frappe = patcher.start()
        case.addCleanup(patcher.stop)

        self.frappe.db.get_value.side_effect = self._db_get_value
        self.frappe.db.get_single_value.return_value = None
        self.frappe.get_all.return_value = ["DEFAULT-CO"]
        self.existing_order = existing_order
        self.created_orders = []

        so_doc = mock.Mock()
        so_doc.name = "SO-NEW-001"
        so_doc.__dict__["items"] = []
        self.frappe.get_doc.return_value = so_doc

    def _db_get_value(self, doctype, filters, field="name"):
        if doctype == "Sales Order":
            return self.existing_order
        if doctype == "Customer":
            return None
        return None


class TestIdempotentMarketplaceImport(unittest.TestCase):
    def test_creates_sales_order_for_new_payload(self):
        p = _FrappePatcher(self, existing_order=None)
        name = order_import.create_sales_order_from_payload(_make_log())

        self.assertEqual(name, "SO-NEW-001")
        so_args = p.frappe.get_doc.call_args[0][0]
        self.assertEqual(so_args["doctype"], "Sales Order")
        self.assertEqual(so_args["marketplace_order_id"], "SHOPEE-123")
        self.assertEqual(so_args["marketplace"], "Shopee")
        self.assertEqual(len(so_args["items"]), 1)
        p.frappe.get_doc.return_value.insert.assert_called_once()

    def test_skips_when_marketplace_order_id_already_exists(self):
        p = _FrappePatcher(self, existing_order="SO-EXISTING-001")
        name = order_import.create_sales_order_from_payload(_make_log())

        self.assertEqual(name, "SO-EXISTING-001")
        # no new Sales Order inserted
        p.frappe.get_doc.assert_not_called()
        p.frappe.get_doc.return_value.insert.assert_not_called()

    def test_invalid_payload_raises(self):
        _FrappePatcher(self)
        log = _make_log(payload="{not json")
        with self.assertRaises(ValueError):
            order_import.create_sales_order_from_payload(log)

    def test_payload_without_order_id_raises(self):
        _FrappePatcher(self)
        log = _make_log(payload='{"buyer_username": "budi01", "items": []}')
        with self.assertRaises(ValueError):
            order_import.create_sales_order_from_payload(log)

    def test_payload_without_mappable_items_raises(self):
        _FrappePatcher(self)
        log = _make_log(payload='{"order_id": "SHOPEE-9", "items": []}')
        with self.assertRaises(ValueError):
            order_import.create_sales_order_from_payload(log)
