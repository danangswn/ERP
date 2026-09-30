# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import unittest

from id_compliance.id_compliance.npwp import format_npwp, normalize_npwp, validate_npwp


class TestNPWPValidation(unittest.TestCase):
    def test_valid_15_digit(self):
        is_valid, digits = validate_npwp("01.234.567.8-901.234")
        self.assertTrue(is_valid)
        self.assertEqual(digits, "012345678901234")

    def test_valid_16_digit_nike(self):
        is_valid, digits = validate_npwp("1234567890123456")
        self.assertTrue(is_valid)
        self.assertEqual(digits, "1234567890123456")

    def test_invalid_short(self):
        is_valid, digits = validate_npwp("01.234.567.8-901")
        self.assertFalse(is_valid)

    def test_invalid_long(self):
        is_valid, digits = validate_npwp("01.234.567.8-901.234.5")
        self.assertFalse(is_valid)

    def test_invalid_letters(self):
        is_valid, digits = validate_npwp("ABCD")
        self.assertFalse(is_valid)

    def test_empty_string(self):
        is_valid, digits = validate_npwp("")
        self.assertFalse(is_valid)

    def test_none(self):
        is_valid, digits = validate_npwp(None)
        self.assertFalse(is_valid)

    def test_normalize(self):
        self.assertEqual(normalize_npwp("01.234.567.8-901.234"), "012345678901234")

    def test_format_15_digit(self):
        self.assertEqual(
            format_npwp("012345678901234"), "01.234.567.8-901.234"
        )

    def test_format_16_digit_passthrough(self):
        self.assertEqual(format_npwp("1234567890123456"), "1234567890123456")
