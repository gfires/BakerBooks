from typing import List

from backend.core.dates import parse_date_flexible
from backend.core.models import ExpectedExpense


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
            expense_date = parse_date_flexible(date_str)
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
