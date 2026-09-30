# Distributor ERP Lite

A vertical ERP for **Indonesian distribution / wholesale SMBs**, built as a
suite of three ERPNext v15 (Frappe framework) apps.

```
┌──────────────────────────────────────────────────────────────┐
│                    ERPNext v15 (Frappe)                      │
├────────────────────┬─────────────────────┬───────────────────┤
│  distributor_core  │    id_compliance    │ marketplace_sync  │
│  ───────────────── │  ────────────────── │  ──────────────── │
│  • credit limits   │  • e-Faktur export  │  • Shopee/Tokop.  │
│  • terbilang       │  • PPN summary      │    connectors     │
│  • sales visits    │  • PPh 23 withholding│  • order import  │
│  • collection      │  • NPWP validation  │  • order logs     │
│    routes          │  • tax templates    │                   │
│  • price tiers     │                     │                   │
└────────────────────┴─────────────────────┴───────────────────┘
```

## The three apps

### 1. [`distributor_core`](distributor_core/README.md)

Core field-sales and credit operations:

- Custom fields on **Customer** (NPWP, IDR credit limit, payment terms,
  price tier, default sales rep, shipping area), **Item** (EAN barcode,
  unit conversions child table) and **Sales Invoice** (`terbilang`
  amount-in-words auto-computed on submit, `faktur_pajak_no`).
- Doctypes: **Sales Visit** (GPS check-in with photos), **Collection Route**
  (weekly visit sequencing), **Price Tier** (per-item-group discounts).
- Credit-limit enforcement on Sales Invoice submit — blocked when
  outstanding AR + the new invoice exceeds the customer's IDR limit, unless
  the user holds the **Credit Override** role.
- Whitelisted API `distributor_core.api.get_aging_reminder_text(customer)` —
  Bahasa Indonesia payment-reminder text for overdue invoices.

### 2. [`id_compliance`](id_compliance/README.md)

Indonesian tax compliance:

- **e-Faktur export** — whitelisted method + Script Report producing a
  DJP-format CSV for a date range of Sales Invoices with a
  `faktur_pajak_no`, plus a printable Jinja Faktur Pajak template.
- **PPN Summary** Script Report — output vs input tax per period per tax
  template.
- **Bukti Potong PPh 23** doctype — supplier invoice link, tax base, fixed
  2% rate, withheld amount.
- Setup patch creating **PPN 11%** (default output/input), **PPN 12%**
  (luxury) and **PPh 23** withholding tax templates.
- **NPWP validation** helper — 15-digit legacy and 16-digit NIKE formats.

### 3. [`marketplace_sync`](marketplace_sync/README.md)

Marketplace connector framework (skeleton — no live credentials needed):

- **Marketplace Settings** singleton — enable flag, Shopee
  partner/shop/partner-key (Password), Tokopedia client credentials
  (Password), sync interval, warehouse mapping.
- **Marketplace Order Log** — raw JSON payloads with import status
  (New / Imported / Failed / Ignored) and a linked Sales Order.
- `ShopeeConnector` / `TokopediaConnector` skeletons with
  `fetch_orders()`, `push_stock()`, `reconcile_settlement()` raising
  `NotImplementedError`; Shopee v2 HMAC-SHA256 signing documented in
  docstrings.
- **Idempotent import** — creates a Sales Order from the payload, skipping
  when the `marketplace_order_id` custom field already exists.
- Scheduled job stubs gated behind `settings.enabled`.

## Installation

Each app installs independently via bench:

```bash
bench get-app https://github.com/danangswn/ERP --branch main
bench --site yoursite install-app distributor_core
bench --site yoursite install-app id_compliance
bench --site yoursite install-app marketplace_sync
```

> `distributor_core` and `id_compliance` require **ERPNext**.
> `marketplace_sync` additionally expects ERPNext's Selling module for
> Sales Order imports.

## Development

See [docs/dev-setup.md](docs/dev-setup.md) for a full WSL2 / devcontainer
setup guide for developing Frappe apps on Windows.

## Testing

```bash
bench --site yoursite run-tests --app distributor_core
bench --site yoursite run-tests --app id_compliance
bench --site yoursite run-tests --app marketplace_sync
```

## License

All three apps are MIT licensed — see each app's `license.txt`.
