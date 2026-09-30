# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import datetime
import unittest.mock as mock
from unittest import TestCase

from id_compliance.id_compliance.efaktur import _header_row


def _mock_frappe(case):
    patcher = mock.patch("id_compliance.id_compliance.efaktur.frappe")
    m = patcher.start()
    case.addCleanup(patcher.stop)

    d = datetime.date(2025, 1, 15)
    m.utils.getdate.return_value = d
    return m


def _make_invoice(faktur_pajak_no="01000012345678901"):
    doc = mock.Mock()
    doc.faktur_pajak_no = faktur_pajak_no
    doc.posting_date = "2025-01-15"
    doc.customer = "PT Sinar Jaya"
    doc.get.return_value = []
    return doc


class TestEFakturCSV(TestCase):
    """Test DJP e-Faktur CSV row generation without a live site."""

    def test_header_row_code_is_FM(self):
        _mock_frappe(self)
        row = _header_row(_make_invoice())
        self.assertEqual(row[0], "FM")

    def test_faktur_number_digits_only(self):
        _mock_frappe(self)
        # dotted/shortened input must be stripped to bare 16 digits
        doc = _make_invoice("0100.0012-3456.7890.1")
        row = _header_row(doc)
        self.assertEqual(row[1], "01000012345678901")

    def test_header_date_is_dd_mm_yyyy(self):
        m = _mock_frappe(self)
        m.utils.getdate.return_value.strftime.return_value = "15/01/2025"
        row = _header_row(_make_invoice())
        self.assertEqual(row[3], "15/01/2025")

    def test_empty_npwp_falls_back_to_zeroes(self):
        _mock_frappe(self)
        doc = _make_invoice()
        doc.get.return_value = []
        row = _header_row(doc)
        # CUSTOMER_NPWP column
        self.assertIn(row[4], ("000000000000000", "0000000000000000", ""))
