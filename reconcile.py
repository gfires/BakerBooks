from typing import List, Tuple
from datetime import date, datetime
from difflib import SequenceMatcher
from models import ExpectedExpense, ReportItem


def _parse_date_flexible(date_str: str) -> date:
    parts = date_str.strip().split("/")
    month = int(parts[0])
    day = int(parts[1])
    if len(parts) == 3 and parts[2]:
        year = int(parts[2])
        if year < 100:
            year += 2000
    else:
        year = date.today().year
    return date(year, month, day)

def parse_expected_expenses(text: str) -> List[ExpectedExpense]:
    """Supports 'MM/DD/YY - Vendor - $Price' and 'MM/DD/YY - $Price - Vendor'."""
    expenses = []

    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split("-")]
        if len(parts) != 3:
            continue

        date_str, part1, part2 = parts

        try:
            expense_date = _parse_date_flexible(date_str)
        except (ValueError, IndexError):
            continue

        if part1.startswith("$"):
            price_str = part1
            vendor = part2
        else:
            vendor = part1
            price_str = part2

        try:
            price = float(price_str.replace("$", "").replace(",", "").strip())
        except ValueError:
            continue

        expenses.append(ExpectedExpense(
            date=expense_date,
            vendor=vendor,
            price=price
        ))

    return expenses

def vendor_similarity(vendor1: str, vendor2: str) -> float:
    if not vendor1 or not vendor2:
        return 0.0

    v1 = vendor1.lower().strip()
    v2 = vendor2.lower().strip()

    return SequenceMatcher(None, v1, v2).ratio()

def reconcile_expenses(
    expected_text: str,
    actual_items: List[ReportItem],
    price_tolerance: float = 1.00,
    similarity_threshold: float = 0.75
) -> dict:
    """Two-phase one-to-one matching: exact price first, then fuzzy (price tolerance + vendor similarity)."""
    expected_expenses = parse_expected_expenses(expected_text)

    matched_pairs: List[Tuple[ExpectedExpense, ReportItem]] = []
    matched_expected_indices = set()
    matched_actual_indices = set()

    for exp_idx, expected in enumerate(expected_expenses):
        if exp_idx in matched_expected_indices:
            continue

        for act_idx, actual in enumerate(actual_items):
            if act_idx in matched_actual_indices:
                continue

            if (expected.price == actual.price and
                actual.date >= expected.date):

                matched_pairs.append((expected, actual))
                matched_expected_indices.add(exp_idx)
                matched_actual_indices.add(act_idx)
                break

    for exp_idx, expected in enumerate(expected_expenses):
        if exp_idx in matched_expected_indices:
            continue

        for act_idx, actual in enumerate(actual_items):
            if act_idx in matched_actual_indices:
                continue

            price_diff = abs(expected.price - actual.price)
            if price_diff > price_tolerance:
                continue

            if actual.date < expected.date:
                continue

            similarity = vendor_similarity(expected.vendor, actual.vendor)
            if similarity < similarity_threshold:
                continue

            matched_pairs.append((expected, actual))
            matched_expected_indices.add(exp_idx)
            matched_actual_indices.add(act_idx)
            break

    unmatched_expected = [
        exp for idx, exp in enumerate(expected_expenses)
        if idx not in matched_expected_indices
    ]

    unmatched_actual = [
        act for idx, act in enumerate(actual_items)
        if idx not in matched_actual_indices
    ]

    return {
        "matched": matched_pairs,
        "unmatched_expected": unmatched_expected,
        "unmatched_actual": unmatched_actual
    }
