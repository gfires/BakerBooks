from typing import List

from fastapi import APIRouter

from backend.core.expense_parser import parse_expected_expenses
from backend.schemas import ExpectedExpenseSchema, ParseExpensesRequest

router = APIRouter(prefix="/api")


@router.post("/parse-expenses", response_model=List[ExpectedExpenseSchema])
async def parse_expenses_endpoint(request: ParseExpensesRequest):
    """
    Parse free-text expected expenses with the same parser /api/reconcile uses.

    Returns only expenses that are valid inputs to /api/generate-affidavit
    (price > 0, non-empty vendor), with ISO dates.
    """
    return [
        ExpectedExpenseSchema.from_dataclass(e)
        for e in parse_expected_expenses(request.expected_expenses)
        if e.price > 0 and e.vendor
    ]
