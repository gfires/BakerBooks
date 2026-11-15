from datetime import date

import pytest

from tests._compat import parse_expected_expenses, parse_date_flexible


def parse(text):
    return parse_expected_expenses(text)


def test_vendor_then_price():
    [e] = parse("9/2/26 - Foo Bar - $5.25")
    assert (e.date, e.vendor, e.price) == (date(2026, 9, 2), "Foo Bar", 5.25)


def test_price_then_vendor():
    [e] = parse("9/2/26 - $5.25 - Foo Bar")
    assert (e.date, e.vendor, e.price) == (date(2026, 9, 2), "Foo Bar", 5.25)


def test_four_digit_year():
    [e] = parse("9/2/2026 - Foo - $1")
    assert e.date == date(2026, 9, 2)


def test_no_year_uses_current_year():
    [e] = parse("9/2 - Foo - $1")
    assert e.date == date(date.today().year, 9, 2)


def test_thousands_separators():
    [e] = parse("9/2/26 - Baz - $1,234,567.50")
    assert e.price == 1234567.5


@pytest.mark.parametrize("line", [
    "2/30/26 - Bar - $3",       # impossible date
    "1/1/26 - Q - $12abc",      # junk price
    "1/1/26 - OnlyTwoParts",    # wrong part count
    "not a date - Foo - $1",
    "",
])
def test_invalid_lines_are_skipped(line):
    assert parse(line) == []


def test_multiple_lines_and_blank_lines():
    out = parse("\n9/2/26 - A - $1\n\n9/3/26 - $2 - B\n")
    assert [(e.vendor, e.price) for e in out] == [("A", 1.0), ("B", 2.0)]


@pytest.mark.parametrize("text,expected", [
    ("3/4", date(date.today().year, 3, 4)),
    ("3/4/26", date(2026, 3, 4)),
    ("3/4/2026", date(2026, 3, 4)),
    (" 3/4/26 ", date(2026, 3, 4)),
])
def test_parse_date_flexible(text, expected):
    assert parse_date_flexible(text) == expected


def test_parse_date_flexible_rejects_impossible_date():
    with pytest.raises(ValueError):
        parse_date_flexible("2/30/26")
