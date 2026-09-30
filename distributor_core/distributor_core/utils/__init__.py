# -*- coding: utf-8 -*-
"""Bahasa Indonesia amount-in-words ("terbilang") conversion utilities."""


def _split_thousands(number):
    """Split an integer into groups of three digits, most significant first."""
    number = int(number)
    if number == 0:
        return [0]
    groups = []
    while number > 0:
        groups.append(number % 1000)
        number //= 1000
    groups.reverse()
    return groups


_ONES = [
    "",
    "satu",
    "dua",
    "tiga",
    "empat",
    "lima",
    "enam",
    "tujuh",
    "delapan",
    "sembilan",
    "sepuluh",
    "sebelas",
]


def _below_thousand(n):
    """Convert a number below 1000 to Indonesian words."""
    if n < 12:
        return _ONES[n]
    if n < 20:
        return _ONES[n - 10] + " belas"
    if n < 100:
        return _ONES[n // 10] + " puluh" + (" " + _ONES[n % 10] if n % 10 else "")
    # 100..999
    if n == 100:
        return "seratus"
    prefix = "seratus" if n // 100 == 1 else _ONES[n // 100] + " ratus"
    rest = _below_thousand(n % 100)
    return prefix + (" " + rest if rest else "")


def _integer_to_words(number):
    """Convert a non-negative integer to Indonesian words."""
    if number == 0:
        return "nol"

    groups = _split_thousands(number)
    scales = ["", "ribu", "juta", "milyar", "triliun", "kuadriliun"]

    parts = []
    for index, group in enumerate(groups):
        scale_index = len(groups) - 1 - index
        scale = scales[scale_index] if scale_index < len(scales) else ""
        if group == 0:
            continue
        # "seribu" instead of "satu ribu"
        if scale_index == 1 and group == 1:
            parts.append("seribu")
        else:
            parts.append((_below_thousand(group) + " " + scale).strip())
    return " ".join(parts)


def _fraction_to_words(fraction):
    """Convert a fractional part (e.g. 0.45) to per-cent words (e.g. "empat puluh lima")."""
    if not fraction:
        return ""
    cents = int(round(fraction * 100))
    if cents == 0:
        return ""
    return _integer_to_words(cents)


def terbilang(amount, currency="Rupiah"):
    """
    Convert a numeric amount to Indonesian amount-in-words ("terbilang").

    Examples:
        terbilang(125000)      -> "seratus dua puluh lima ribu Rupiah"
        terbilang(1500.75)     -> "seribu lima ratus Rupiah tujuh puluh lima sen"
        terbilang(0)           -> "nol Rupiah"
    """
    amount = float(amount)
    negative = amount < 0
    amount = abs(amount)

    integer_part = int(amount)
    fraction = amount - integer_part

    words = _integer_to_words(integer_part)

    # Rupiah has no commonly used subunit on invoices, but "sen" appears on
    # some settlement documents; include it when present.
    cent_words = _fraction_to_words(fraction)

    currency_name = currency if currency else "Rupiah"
    result = words + " " + currency_name
    if cent_words:
        result += " " + cent_words + " sen"
    if negative:
        result = "minus " + result
    return result.strip()
