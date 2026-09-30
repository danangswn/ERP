# -*- coding: utf-8 -*-
"""
Scheduled job stubs.

Every job is a no-op unless ``Marketplace Settings.enabled`` is checked.
Connectors raise NotImplementedError until real credentials are provisioned,
so each job guards and logs rather than spamming the error log.
"""

import frappe

from marketplace_sync.marketplace_sync.connectors import get_connector


def _sync_enabled():
    return frappe.db.get_single_value("Marketplace Settings", "enabled")


def sync_orders():
    """cron */15 * * * *: pull new orders from each enabled marketplace."""
    if not _sync_enabled():
        return
    for marketplace in ("Shopee", "Tokopedia"):
        try:
            connector = get_connector(marketplace)
        except Exception as exc:
            frappe.log_error(f"marketplace_sync connector init failed for {marketplace}: {exc}")
            continue
        try:
            connector.fetch_orders()
        except NotImplementedError:
            # Skeleton: connector not yet wired to live API.
            continue
        except Exception as exc:
            frappe.log_error(f"marketplace_sync fetch_orders failed for {marketplace}: {exc}")


def push_stock_updates():
    """cron 0 */4 * * *: push ERPNext stock levels to marketplaces."""
    if not _sync_enabled():
        return
    for marketplace in ("Shopee", "Tokopedia"):
        try:
            connector = get_connector(marketplace)
            connector.push_stock()
        except NotImplementedError:
            continue
        except Exception as exc:
            frappe.log_error(f"marketplace_sync push_stock failed for {marketplace}: {exc}")


def reconcile_settlements():
    """cron 0 2 * * *: pull settlement reports and reconcile payouts."""
    if not _sync_enabled():
        return
    for marketplace in ("Shopee", "Tokopedia"):
        try:
            connector = get_connector(marketplace)
            connector.reconcile_settlement()
        except NotImplementedError:
            continue
        except Exception as exc:
            frappe.log_error(f"marketplace_sync reconcile_settlement failed for {marketplace}: {exc}")
