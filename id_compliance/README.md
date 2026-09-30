# id_compliance

Indonesian tax compliance for **Distributor ERP Lite** on ERPNext v15
(Frappe framework).

## Features

- **e-Faktur export**
  - Whitelisted method `id_compliance.api.export_efaktur_csv(from_date, to_date)`
    plus a Script Report (`eFaktur Export`) that produce a DJP-format CSV of
    submitted Sales Invoices with a `faktur_pajak_no` set for a date range.
  - Jinja print template for printable **Faktur Pajak** documents.
- **PPN summary Script Report** (`PPN Summary`): output tax vs input tax per
  period per tax template.
- **Bukti Potong PPh 23** doctype: supplier invoice link, tax base, 2% rate,
  withholding amount.
- **Setup patch** creating standard tax templates:
  - PPN 11% — Output / Input tax (default)
  - PPN 12% — Output / Input tax (luxury goods)
  - PPh 23 withholding template
- **NPWP validation helper** (`id_compliance.npwp.validate_npwp`) supporting
  15-digit legacy and 16-digit NIKE formats.

## Installation

```bash
bench get-app https://github.com/danangswn/ERP --branch main
bench --site yoursite install-app id_compliance
```

## Testing

```bash
bench --site yoursite run-tests --app id_compliance
```

## License

MIT — see [license.txt](license.txt).
