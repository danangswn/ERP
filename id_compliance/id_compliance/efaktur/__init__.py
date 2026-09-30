# -*- coding: utf-8 -*-
"""
e-Faktur DJP-format CSV export.

Generates a CSV in the structure expected by DJP's e-Faktur desktop client
(``efaktur-export.csv``) for a date range of submitted Sales Invoices that
have a ``faktur_pajak_no`` set.

Column layout (semicolon separated, per DJP e-Faktur 3.x):
    FM,NSFQ,MSFQ,FM_DATE,CUSTOMER_NPWP,CUSTOMER_NAME,LT,
    CUSTOMER_ADDRESS,JENIS_FAKTUR,UANG_MUKA,JML_BARIS,DISKON,DPP,
    PPN,PPNBM,MATERAI,REFERENSI,F_DIREKSI
then one row per line item:
    OF,JML_BARIS,NOMOR_BARIS,NAMA_BARANG,NAMA_UNIT,HARGA,JML_BARANG,
    TOTAL_DISKON,DPP,PPN,TARIF_PPNBM,PPNBM
"""

import csv
import io

import frappe
from frappe import _

DELIMITER = ";"

HEADER_CODE = "FM"
DETAIL_CODE = "OF"

# Record types per DJP spec
JENIS_FAKTUR_NORMAL = "01"
JENIS_FAKTUR_PENGGANTI = "02"


def generate_efaktur_csv(from_date, to_date, company=None):
    """
    Build the DJP e-Faktur CSV text for submitted Sales Invoices dated
    ``from_date``..``to_date`` that carry a ``faktur_pajak_no``.

    Returns a string suitable for writing straight to ``.csv``.
    """
    invoices = get_invoices_with_faktur_pajak(from_date, to_date, company)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=DELIMITER, lineterminator="\r\n")

    for invoice in invoices:
        writer.writerow(_header_row(invoice))
        for idx, item in enumerate(invoice.items, start=1):
            writer.writerow(_detail_row(invoice, item, idx))

    return buffer.getvalue()


def get_invoices_with_faktur_pajak(from_date, to_date, company=None):
    """Fetch submitted Sales Invoices with faktur_pajak_no set in a date range."""
    filters = {
        "docstatus": 1,
        "faktur_pajak_no": ("is", "set"),
        "posting_date": ("between", [from_date, to_date]),
    }
    if company:
        filters["company"] = company

    invoices = frappe.get_all(
        "Sales Invoice",
        filters=filters,
        fields=["name", "customer", "posting_date", "faktur_pajak_no", "company"],
        order_by="posting_date asc, name asc",
    )

    out = []
    for row in invoices:
        doc = frappe.get_doc("Sales Invoice", row.name)
        doc.efaktur_npwp = _get_customer_npwp(doc.customer)
        out.append(doc)
    return out


def _header_row(doc):
    lines = doc.get("items") or []
    total_dpp = sum(item.amount for item in lines)
    total_ppn = sum(
        (tax.tax_amount or 0)
        for tax in (doc.get("taxes") or [])
        if _is_ppn_account(tax.account_head)
    )

    return [
        HEADER_CODE,                       # FM
        _faktur_sequence(doc),             # NSFQ: nomor urut faktur (16 digit)
        "",                                # MSFQ: masa serah faktur
        _format_date(doc.posting_date),    # FM_DATE
        doc.get("efaktur_npwp") or "000000000000000",  # CUSTOMER_NPWP
        doc.customer or "",                # CUSTOMER_NAME
        "",                                # LT: lawan transaksi (1=import, 0=local)
        doc.get("address_display") or "",  # CUSTOMER_ADDRESS
        JENIS_FAKTUR_NORMAL,               # JENIS_FAKTUR
        0,                                 # UANG_MUKA
        len(lines),                        # JML_BARIS
        0,                                 # DISKON
        round(total_dpp, 2),               # DPP
        round(total_ppn, 2),               # PPN
        0,                                 # PPNBM
        0,                                 # MATERAI
        doc.get("remarks") or "",          # REFERENSI
        "",                                # F_DIREKSI
    ]


def _detail_row(doc, item, line_number):
    item_ppn = sum(
        (tax.tax_amount or 0) for tax in (doc.get("taxes") or []) if _is_ppn_account(tax.account_head)
    )
    item_dpp = item.amount or 0
    return [
        DETAIL_CODE,                       # OF
        len(doc.get("items") or []),       # JML_BARIS
        line_number,                       # NOMOR_BARIS
        item.item_name or item.item_code or "",  # NAMA_BARANG
        item.uom or "",                    # NAMA_UNIT
        round(item.rate or 0, 2),          # HARGA
        item.qty or 0,                     # JML_BARANG
        round(item.discount_amount or 0, 2),  # TOTAL_DISKON
        round(item_dpp, 2),                # DPP
        round(item_ppn / max(len(doc.items), 1), 2),  # PPN (proportional)
        0,                                 # TARIF_PPNBM
        0,                                 # PPNBM
    ]


def _is_ppn_account(account):
    if not account:
        return False
    name = str(account).lower()
    return "ppn" in name or "vat" in name or "ppn keluaran" in name


def _faktur_sequence(doc):
    """NSFQ is the 16-digit faktur number; strip punctuation if present."""
    no = doc.get("faktur_pajak_no") or ""
    digits = "".join(ch for ch in str(no) if ch.isdigit())
    return digits


def _format_date(value):
    if not value:
        return ""
    return frappe.utils.getdate(value).strftime("%d/%m/%Y")


def _get_customer_npwp(customer):
    if not customer:
        return ""
    npwp = frappe.db.get_value("Customer", customer, "id_npwp")
    if npwp:
        return "".join(ch for ch in str(npwp) if ch.isdigit())
    return frappe.db.get_value("Customer", customer, "tax_id") or ""
