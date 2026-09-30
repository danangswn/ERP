# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import hashlib
import hmac
import unittest
from unittest import mock

from marketplace_sync.marketplace_sync.connectors import (
    ShopeeConnector,
    TokopediaConnector,
)


def _make_settings():
    settings = mock.Mock()
    settings.get.side_effect = lambda key: {
        "shopee_partner_id": "1234",
        "shopee_shop_id": "5678",
        "shopee_host": "https://partner.test",
        "tokopedia_client_id": "tok-client",
        "tokopedia_host": "https://tokotest",
    }.get(key)
    settings.get_password.side_effect = lambda key: {
        "shopee_partner_key": "shopee-secret",
        "tokopedia_client_secret": "tok-secret",
    }.get(key)
    return settings


class TestShopeeConnector(unittest.TestCase):
    def test_sign_matches_reference_algorithm(self):
        """signature = HMAC-SHA256(partner_key, partner_id + path + timestamp + body)"""
        connector = ShopeeConnector(_make_settings())
        path = "/api/v2/order/get_order_list"
        ts = 1700000000
        body = '{"order_sn":"ABC"}'

        expected = hmac.new(
            b"shopee-secret",
            f"1234{path}{ts}{body}".encode(),
            hashlib.sha256,
        ).hexdigest()

        self.assertEqual(connector.sign(path, body, timestamp=ts), expected)

    def test_sign_is_lowercase_hex(self):
        connector = ShopeeConnector(_make_settings())
        sig = connector.sign("/api/v2/test", "")
        self.assertEqual(sig, sig.lower())
        self.assertEqual(len(sig), 64)

    def test_fetch_orders_not_implemented(self):
        connector = ShopeeConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.fetch_orders()

    def test_push_stock_not_implemented(self):
        connector = ShopeeConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.push_stock()

    def test_reconcile_settlement_not_implemented(self):
        connector = ShopeeConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.reconcile_settlement()


class TestTokopediaConnector(unittest.TestCase):
    def test_fetch_orders_not_implemented(self):
        connector = TokopediaConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.fetch_orders()

    def test_push_stock_not_implemented(self):
        connector = TokopediaConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.push_stock()

    def test_reconcile_settlement_not_implemented(self):
        connector = TokopediaConnector(_make_settings())
        with self.assertRaises(NotImplementedError):
            connector.reconcile_settlement()
