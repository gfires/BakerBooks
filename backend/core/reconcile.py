from typing import List, Tuple
from difflib import SequenceMatcher
from backend.core.expense_parser import parse_expected_expenses
from backend.core.models import ExpectedExpense, ReportItem


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
