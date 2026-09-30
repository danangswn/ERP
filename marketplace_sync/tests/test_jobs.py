# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

"""Scheduled job gating tests (mocked frappe layer)."""

import unittest
from unittest import mock

from marketplace_sync.marketplace_sync import jobs


def _patch_frappe(case, enabled):
    patcher = mock.patch.object(jobs, "frappe")
    m = patcher.start()
    case.addCleanup(patcher.stop)
    m.db.get_single_value.return_value = enabled
    return m


class TestScheduledJobs(unittest.TestCase):
    def test_sync_orders_noop_when_disabled(self):
        m = _patch_frappe(self, enabled=False)
        with mock.patch.object(jobs, "get_connector") as gc:
            jobs.sync_orders()
            gc.assert_not_called()

    def test_push_stock_noop_when_disabled(self):
        m = _patch_frappe(self, enabled=False)
        with mock.patch.object(jobs, "get_connector") as gc:
            jobs.push_stock_updates()
            gc.assert_not_called()

    def test_reconcile_noop_when_disabled(self):
        m = _patch_frappe(self, enabled=False)
        with mock.patch.object(jobs, "get_connector") as gc:
            jobs.reconcile_settlements()
            gc.assert_not_called()

    def test_sync_orders_runs_connectors_when_enabled(self):
        _patch_frappe(self, enabled=True)
        with mock.patch.object(jobs, "get_connector") as gc:
            gc.return_value = mock.Mock()
            jobs.sync_orders()
            self.assertEqual(gc.call_count, 2)  # Shopee + Tokopedia
            gc.return_value.fetch_orders.assert_called()

    def test_sync_orders_swallows_not_implemented(self):
        _patch_frappe(self, enabled=True)
        with mock.patch.object(jobs, "get_connector") as gc:
            connector = mock.Mock()
            connector.fetch_orders.side_effect = NotImplementedError
            gc.return_value = connector
            jobs.sync_orders()  # should not raise
