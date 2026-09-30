# Copyright (c) 2025, Distributor ERP Lite and contributors
# For license information, please see license.txt

import unittest
from unittest import mock

from distributor_core.distributor_core.credit_limit import validate_credit_limit


def _make_invoice(customer="CUST-001", grand_total=1_000_000):
    invoice = mock.Mock()
    invoice.customer = customer
    invoice.grand_total = grand_total
    return invoice


class TestCreditLimitValidation(unittest.TestCase):
    """Credit-limit logic tests. These run without a live Frappe site by
    patching the frappe helpers used inside validate_credit_limit."""

    def _patch_frappe(self, credit_limit=5_000_000, roles=(), outstanding=0.0):
        self._frappe_patcher = mock.patch(
            "distributor_core.distributor_core.credit_limit.frappe",
        )
        frappe_mock = self._frappe_patcher.start()
        self.addCleanup(self._frappe_patcher.stop)

        frappe_mock.get_roles.return_value = list(roles)
        frappe_mock.get_doc.return_value.get.return_value = credit_limit
        frappe_mock._get_customer_outstanding_ar.return_value = outstanding
        frappe_mock.PermissionError = Exception

        thrown = {}

        def _throw(*args, **kwargs):
            thrown["exc"] = args[0] if args else kwargs.get("msg")
            raise frappe_mock.PermissionError(args[0] if args else "blocked")

        frappe_mock.throw.side_effect = _throw
        return frappe_mock, thrown

    def test_submit_blocked_when_credit_limit_exceeded(self):
        """outstanding AR 4.5M + invoice 1M > limit 5M -> blocked."""
        frappe_mock, thrown = self._patch_frappe(
            credit_limit=5_000_000, outstanding=4_500_000
        )
        with self.assertRaises(frappe_mock.PermissionError):
            validate_credit_limit(_make_invoice(grand_total=1_000_000))
        self.assertIn("Credit limit exceeded", str(thrown["exc"]))

    def test_submit_allowed_within_credit_limit(self):
        """outstanding AR 3M + invoice 1M <= limit 5M -> allowed."""
        frappe_mock, thrown = self._patch_frappe(
            credit_limit=5_000_000, outstanding=3_000_000
        )
        validate_credit_limit(_make_invoice(grand_total=1_000_000))
        frappe_mock.throw.assert_not_called()

    def test_submit_blocked_at_exactly_the_limit(self):
        """outstanding 4.5M + invoice 0.5M == 5M limit -> allowed (not greater)."""
        frappe_mock, thrown = self._patch_frappe(
            credit_limit=5_000_000, outstanding=4_500_000
        )
        validate_credit_limit(_make_invoice(grand_total=500_000))
        frappe_mock.throw.assert_not_called()

    def test_credit_override_role_bypasses_check(self):
        """A user with the Credit Override role may submit past the limit."""
        frappe_mock, thrown = self._patch_frappe(
            credit_limit=5_000_000, outstanding=9_999_999, roles=("Credit Override",)
        )
        validate_credit_limit(_make_invoice(grand_total=10_000_000))
        frappe_mock.throw.assert_not_called()

    def test_no_credit_limit_configured_is_noop(self):
        """Customer without a credit limit configured -> invoice allowed."""
        frappe_mock, thrown = self._patch_frappe(credit_limit=0, outstanding=0)
        validate_credit_limit(_make_invoice(grand_total=999_999_999))
        frappe_mock.throw.assert_not_called()
