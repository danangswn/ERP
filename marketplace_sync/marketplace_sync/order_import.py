# -*- coding: utf-8 -*-
"""
Idempotent marketplace order import.

``create_sales_order_from_payload(log)`` converts a ``Marketplace Order Log``
row into an ERPNext Sales Order. Import is idempotent: if a Sales Order with
the same ``marketplace_order_id`` custom field already exists, the existing
order is returned and nothing new is created.
"""

import json
from typing import Any, Dict, Optional

import frappe
from frappe import _


def create_sales_order_from_payload(log) -> str:
    """
    Create (or return the existing) Sales Order for a Marketplace Order Log.

    :param log: a ``Marketplace Order Log`` document (has ``payload`` JSON,
        ``marketplace``, ``order_id``).
    :returns: name of the (possibly pre-existing) Sales Order.
    :raises ValueError: when the payload is malformed.
    """
    payload = _parse_payload(log.payload)

    marketplace_order_id = str(
        payload.get("order_id") or payload.get("order_sn") or log.order_id or ""
    ).strip()
    if not marketplace_order_id:
        raise ValueError(_("Payload has no order_id / order_sn"))

    existing = _find_existing_sales_order(marketplace_order_id)
    if existing:
        return existing

    customer = _resolve_customer(payload, log)
    items = _resolve_items(payload)
    company = _default_company()

    so = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": customer,
            "company": company,
            "marketplace_order_id": marketplace_order_id,
            "marketplace": log.marketplace,
            "transaction_date": payload.get("created_at") or frappe.utils.today(),
            "items": items,
        }
    )
    so.insert(ignore_permissions=True)
    return so.name


def _find_existing_sales_order(marketplace_order_id: str) -> Optional[str]:
    """Idempotency guard: look up a previously imported order."""
    return frappe.db.get_value(
        "Sales Order",
        {"marketplace_order_id": marketplace_order_id},
        "name",
    )


def _parse_payload(payload: str) -> Dict[str, Any]:
    if not payload:
        raise ValueError(_("Empty payload"))
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(_("Payload is not valid JSON: {0}").format(str(exc)))
    if not isinstance(data, dict):
        raise ValueError(_("Payload must be a JSON object"))
    return data


def _resolve_customer(payload: Dict[str, Any], log) -> str:
    """Map the marketplace buyer to an ERPNext Customer, creating if needed."""
    buyer_name = (
        payload.get("buyer_username")
        or payload.get("buyer_name")
        or f"{log.marketplace} Guest"
    )
    customer = frappe.db.get_value("Customer", {"customer_name": buyer_name}, "name")
    if customer:
        return customer

    customer_doc = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": buyer_name,
            "customer_type": "Individual",
            "customer_group": frappe.db.get_single_value("Selling Settings", "customer_group")
            or "All Customer Groups",
            "territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
        }
    )
    customer_doc.insert(ignore_permissions=True)
    return customer_doc.name


def _resolve_items(payload: Dict[str, Any]) -> list:
    """Map payload line items to Sales Order items (best-effort)."""
    raw_items = payload.get("items") or payload.get("item_list") or []
    items = []
    for raw in raw_items:
        item_code = raw.get("item_code") or raw.get("sku") or raw.get("item_id")
        if not item_code:
            continue
        items.append(
            {
                "item_code": item_code,
                "qty": raw.get("qty") or raw.get("quantity") or 1,
                "rate": raw.get("price") or raw.get("item_price") or 0,
            }
        )
    if not items:
        raise ValueError(_("No mappable items in payload"))
    return items


def _default_company() -> str:
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        companies = frappe.get_all("Company", limit=1, pluck="name")
        company = companies[0] if companies else None
    if not company:
        raise ValueError(_("No company configured"))
    return company
