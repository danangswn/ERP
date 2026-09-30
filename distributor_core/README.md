# distributor_core

Core distributor operations layer for **Distributor ERP Lite** — a vertical ERP
for Indonesian distribution/wholesale SMBs built on ERPNext v15 (Frappe
framework).

## Features

- **Custom fields on standard doctypes**
  - `Customer`: `id_npwp`, `credit_limit_idr`, `payment_terms_days`,
    `price_tier` (Retail / Grosir / Sub-distributor), `default_sales_rep`,
    `shipping_area`
  - `Item`: `barcode_ean`, `unit_conversions` child table
    (`from_unit`, `to_unit`, `conversion_factor`)
  - `Sales Invoice`: `terbilang` (amount in words, Bahasa Indonesia,
    auto-computed on submit), `faktur_pajak_no` (16-digit e-Faktur number)
- **New doctypes**
  - `Sales Visit` — field-sales check-in/check-out tracking with geolocation
    and photos
  - `Collection Route` — weekly customer visit sequencing for debt collectors
  - `Price Tier` — tier-based discounts per item group
- **Credit limit enforcement** on Sales Invoice submit: blocks when
  outstanding AR + the new invoice exceeds the customer's IDR credit limit,
  unless the user holds the *Credit Override* role.
- Property setters for IDR number formatting; Bahasa Indonesia translation
  stub (`id.csv`).
- Whitelisted helper: `distributor_core.api.get_aging_reminder_text(customer)`
  returns a Bahasa Indonesia payment-reminder text for a customer's overdue
  invoices.

## Installation

```bash
bench get-app https://github.com/danangswn/ERP --branch main
bench --site yoursite install-app distributor_core
```

## Testing

```bash
bench --site yoursite run-tests --app distributor_core
```

## License

MIT — see [license.txt](license.txt).
