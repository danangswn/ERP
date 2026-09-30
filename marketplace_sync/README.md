# marketplace_sync

Marketplace connector framework for **Distributor ERP Lite** on ERPNext v15
(Frappe framework). Skeleton implementation — no live credentials required.

## Features

- **Marketplace Settings** singleton: enable/disable sync, Shopee
  (`partner_id`, `shop_id`, `partner_key` as Password), Tokopedia
  (`client_id`, `client_secret` as Password), sync interval, warehouse
  mapping.
- **Marketplace Order Log** doctype: raw payload (JSON), marketplace,
  order id, import status (New / Imported / Failed / Ignored), linked Sales
  Order and error message.
- **Connector classes** `ShopeeConnector` / `TokopediaConnector` with
  `fetch_orders()`, `push_stock()`, `reconcile_settlement()` stubs that raise
  `NotImplementedError`. Shopee v2 request signing (HMAC-SHA256 over
  timestamp + path + body) is documented in the docstrings.
- **Idempotent order import**: creates a Sales Order from a stored payload;
  skips creation when a Sales Order with the same `marketplace_order_id`
  custom field already exists.
- Scheduled job stubs in `hooks.py`, gated behind `settings.enabled`.

## Installation

```bash
bench get-app https://github.com/danangswn/ERP --branch main
bench --site yoursite install-app marketplace_sync
```

## Testing

```bash
bench --site yoursite run-tests --app marketplace_sync
```

## License

MIT — see [license.txt](license.txt).
