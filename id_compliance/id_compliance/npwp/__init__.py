# -*- coding: utf-8 -*-
"""
NPWP (Nomor Pokok Wajib Pajak) validation helpers.

Supported formats:
- **15-digit** legacy NPWP:  `00.000.000.A-000.000` or bare 15 digits.
- **16-digit** NIKE (Nomor Induk Kepabeanan dan Cukai):  16 bare digits,
  issued since the 2023 coretax transition. Note that NIKE is a customs &
  excise registration number; it is accepted here where DJP now accepts
  16-digit taxpayer numbers for individuals.
"""


def normalize_npwp(value):
    """Strip punctuation/spaces from an NPWP string, returning digits only."""
    if not value:
        return ""
    return "".join(ch for ch in str(value) if ch.isdigit())


def format_npwp(value):
    """
    Format a 15-digit NPWP as `00.000.000.A-000.000`.
    16-digit NIKE numbers are returned as bare digits (no canonical layout).
    """
    digits = normalize_npwp(value)
    if len(digits) == 15:
        return (
            f"{digits[0:2]}.{digits[2:5]}.{digits[5:8]}."
            f"{digits[8]}-{digits[9:12]}.{digits[12:15]}"
        )
    if len(digits) == 16:
        return digits
    return str(value or "")


def validate_npwp(value):
    """
    Validate an NPWP / NIKE number.

    Returns (is_valid, normalized_digits). Raises nothing; callers decide
    whether to `frappe.throw` on invalid input.
    """
    digits = normalize_npwp(value)

    if len(digits) == 15:
        # 15-digit legacy NPWP: position 8 is a letter in the dotted form but
        # numeric 0/1 in bare digits? Historically the 9th character is a
        # letter 'A'..'I' or '0'-'9' in digit form; accept any digit here.
        return True, digits

    if len(digits) == 16:
        # NIKE / 16-digit taxpayer number: any 16 digits accepted.
        # DJP notes that NIKE is issued by Bea Cukai for importers; when
        # present it replaces the 15-digit NPWP in coretax filings.
        return True, digits

    return False, digits
