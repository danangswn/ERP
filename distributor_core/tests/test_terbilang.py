# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import unittest

from distributor_core.distributor_core.utils import terbilang


class TestTerbilang(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(terbilang.terbilang(0), "nol Rupiah")

    def test_simple_hundreds(self):
        self.assertEqual(terbilang.terbilang(500), "lima ratus Rupiah")

    def test_seribu_special_case(self):
        # 1000 is "seribu", never "satu ribu"
        self.assertEqual(terbilang.terbilang(1000), "seribu Rupiah")

    def test_thousands(self):
        self.assertEqual(terbilang.terbilang(125000), "seratus dua puluh lima ribu Rupiah")

    def test_two_thousand_uses_satu_ribu(self):
        self.assertEqual(terbilang.terbilang(2000), "dua ribu Rupiah")

    def test_millions(self):
        self.assertEqual(
            terbilang.terbilang(1500000), "satu juta lima ratus ribu Rupiah"
        )

    def test_billions(self):
        self.assertEqual(
            terbilang.terbilang(2500000000),
            "dua milyar lima ratus juta Rupiah",
        )

    def test_teen_numbers(self):
        self.assertEqual(terbilang.terbilang(11), "sebelas Rupiah")
        self.assertEqual(terbilang.terbilang(15), "lima belas Rupiah")

    def test_tens(self):
        self.assertEqual(terbilang.terbilang(20), "dua puluh Rupiah")
        self.assertEqual(terbilang.terbilang(45), "empat puluh lima Rupiah")

    def test_fraction_becomes_sen(self):
        self.assertEqual(
            terbilang.terbilang(1500.75),
            "seribu lima ratus Rupiah tujuh puluh lima sen",
        )

    def test_negative_amounts(self):
        self.assertEqual(terbilang.terbilang(-125000), "minus seratus dua puluh lima ribu Rupiah")

    def test_rounding_up_fraction(self):
        # 0.995 rounds to 100 sen -> 1 sen unit words ("seratus")
        self.assertIn("sen", terbilang.terbilang(10.995))
