from datetime import date

from tests._compat import ReportItem, reconcile_expenses, vendor_similarity


def item(price, vendor, d=date(2026, 9, 5)):
    return ReportItem(description="", activity="", date=d, price=price,
                      vendor=vendor, receipts=[], flyer="")


def test_exact_price_match():
    r = reconcile_expenses("9/2/26 - Foo - $10", [item(10.0, "Whatever")])
    assert len(r["matched"]) == 1
    assert not r["unmatched_expected"] and not r["unmatched_actual"]


def test_actual_before_expected_date_does_not_match():
    r = reconcile_expenses("9/2/26 - Foo - $10", [item(10.0, "Foo", date(2026, 9, 1))])
    assert not r["matched"]
    assert len(r["unmatched_expected"]) == 1 and len(r["unmatched_actual"]) == 1


def test_fuzzy_match_within_tolerance_and_similar_vendor():
    r = reconcile_expenses("9/2/26 - Amazon - $10.00", [item(10.50, "Amazon.com")])
    assert len(r["matched"]) == 1


def test_fuzzy_rejected_when_price_outside_tolerance():
    r = reconcile_expenses("9/2/26 - Amazon - $10.00", [item(12.00, "Amazon")])
    assert not r["matched"]


def test_fuzzy_rejected_when_vendor_dissimilar():
    r = reconcile_expenses("9/2/26 - Amazon - $10.00", [item(10.50, "Zzzzzz")])
    assert not r["matched"]


def test_one_to_one_matching():
    r = reconcile_expenses("9/2/26 - A - $10\n9/2/26 - B - $10", [item(10.0, "A")])
    assert len(r["matched"]) == 1 and len(r["unmatched_expected"]) == 1


def test_vendor_similarity():
    assert vendor_similarity("Foo", "foo ") == 1.0
    assert vendor_similarity("", "foo") == 0.0
