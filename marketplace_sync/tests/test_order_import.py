# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import unittest

from marketplace_sync.marketplace_sync.order_import import _parse_payload


class TestOrderImportHelpers(unittest.TestCase):
	def test_parse_payload_valid(self):
		data = _parse_payload('{"order_id": "SHOPEE-123", "items": []}')
		self.assertEqual(data["order_id"], "SHOPEE-123")

	def test_parse_payload_invalid_json(self):
		with self.assertRaises(ValueError):
			_parse_payload("{not json")

	def test_parse_payload_not_object(self):
		with self.assertRaises(ValueError):
			_parse_payload('["array"]')

	def test_parse_payload_empty(self):
		with self.assertRaises(ValueError):
			_parse_payload("")
