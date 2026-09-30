# -*- coding: utf-8 -*-
"""
Marketplace connector framework.

Concrete connectors subclass :class:`BaseConnector` and implement the three
sync primitives used by the scheduled jobs and the manual-sync UI:

- ``fetch_orders()``  — pull new orders since the last sync cursor
- ``push_stock()``    — push ERPNext stock levels to the marketplace
- ``reconcile_settlement()`` — pull settlement/payout reports

This is a skeleton: all network I/O is intentionally unimplemented and the
concrete classes raise ``NotImplementedError`` until credentials and API
versions are provisioned.
"""

import abc
import hashlib
import hmac
import time
from typing import Any, Dict, Optional


class BaseConnector(abc.ABC):
    """Common contract for marketplace connectors."""

    marketplace: str = "Base"

    def __init__(self, settings):
        """
        :param settings: a ``Marketplace Settings`` document (frappe Document).
        """
        self.settings = settings

    # ------------------------------------------------------------------
    # Sync primitives
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def fetch_orders(self) -> list:
        """Return a list of raw order payloads (dicts) to import."""

    @abc.abstractmethod
    def push_stock(self) -> Dict[str, Any]:
        """Push ERPNext stock levels; return a summary dict."""

    @abc.abstractmethod
    def reconcile_settlement(self) -> Dict[str, Any]:
        """Pull settlement reports; return a summary dict."""

    # ------------------------------------------------------------------
    # Shared signing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def hmac_sha256_hex(secret: str, message: str) -> str:
        """HMAC-SHA256 helper shared by Shopee (and similar) connectors."""
        return hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def current_timestamp() -> int:
        """Unix timestamp in seconds (marketplace APIs generally use seconds)."""
        return int(time.time())


class ShopeeConnector(BaseConnector):
    """
    Shopee Open Platform v2 connector (skeleton).

    Request signing (Shopee v2):

    Every authenticated call to the Shopee v2 OpenAPI must include the
    ``signature`` query parameter, computed as::

        base_string = partner_id + path        + timestamp + body
                      ^^^^^^^^^^ ^^^^^^^^^^^^^ ^^^^^^^^^ ^^^^^
                      e.g. 1234  /api/v2/order/ 1700000000 {"order_sn":"..."}

        signature  = HMAC-SHA256(partner_key, base_string).hexdigest()

    where ``path`` is the *path portion only* of the endpoint URL
    (e.g. ``/api/v2/order/get_order_list``), ``timestamp`` is the current
    Unix epoch in seconds, and ``body`` is the raw JSON request body (an
    empty string for GET requests). The resulting lowercase hex digest is
    sent as the ``signature`` query parameter together with ``partner_id``,
    ``timestamp``, and (for shop-level endpoints) ``shop_id`` and
    ``access_token``.

    See https://open.shopee.com/documents for the authoritative reference.
    """

    marketplace = "Shopee"

    def __init__(self, settings):
        super().__init__(settings)
        self.partner_id = settings.get("shopee_partner_id")
        self.shop_id = settings.get("shopee_shop_id")
        self.partner_key = settings.get_password("shopee_partner_key")
        self.host = settings.get("shopee_host") or "https://partner.shopeemobile.com"

    def sign(self, path: str, body: str = "", timestamp: Optional[int] = None) -> str:
        """
        Compute the Shopee v2 signature for ``path``.

        ``signature = HMAC-SHA256(partner_key, partner_id + path + timestamp + body)``
        """
        ts = timestamp if timestamp is not None else self.current_timestamp()
        base_string = f"{self.partner_id}{path}{ts}{body}"
        return self.hmac_sha256_hex(self.partner_key or "", base_string)

    def fetch_orders(self) -> list:
        raise NotImplementedError("ShopeeConnector.fetch_orders requires live credentials")

    def push_stock(self) -> Dict[str, Any]:
        raise NotImplementedError("ShopeeConnector.push_stock requires live credentials")

    def reconcile_settlement(self) -> Dict[str, Any]:
        raise NotImplementedError("ShopeeConnector.reconcile_settlement requires live credentials")


class TokopediaConnector(BaseConnector):
    """
    Tokopedia Seller API connector (skeleton).

    Tokopedia uses OAuth2 bearer tokens (``client_id``/``client_secret``
    exchanged for an access token) rather than request signing.
    """

    marketplace = "Tokopedia"

    def __init__(self, settings):
        super().__init__(settings)
        self.client_id = settings.get("tokopedia_client_id")
        self.client_secret = settings.get_password("tokopedia_client_secret")
        self.host = settings.get("tokopedia_host") or "https://open.tokopedia.com"

    def fetch_orders(self) -> list:
        raise NotImplementedError("TokopediaConnector.fetch_orders requires live credentials")

    def push_stock(self) -> Dict[str, Any]:
        raise NotImplementedError("TokopediaConnector.push_stock requires live credentials")

    def reconcile_settlement(self) -> Dict[str, Any]:
        raise NotImplementedError("TokopediaConnector.reconcile_settlement requires live credentials")


def get_connector(marketplace: str, settings=None) -> BaseConnector:
    """Factory returning the connector instance for a marketplace name."""
    if settings is None:
        settings = frappe_get_settings()
    if marketplace == "Shopee":
        return ShopeeConnector(settings)
    if marketplace == "Tokopedia":
        return TokopediaConnector(settings)
    raise ValueError(f"Unknown marketplace: {marketplace}")


def frappe_get_settings():
    import frappe

    return frappe.get_cached_doc("Marketplace Settings")
