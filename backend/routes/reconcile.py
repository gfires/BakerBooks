from datetime import datetime

import requests
from fastapi import APIRouter, HTTPException

from backend.core.reconcile import reconcile_expenses
from backend.core.sheet_parser import parse_purchases
from backend.schemas import (
    ExpectedExpenseSchema,
    MatchedPair,
    ReconcileRequest,
    ReconcileResponse,
    ReportItemSchema,
)

router = APIRouter(prefix="/api")


@router.post("/reconcile", response_model=ReconcileResponse)
async def reconcile(request: ReconcileRequest):
    """
    Reconcile expected expenses against actual expenses from Google Sheets.

    - **cardholder_name**: Name to filter transactions by
    - **start_date**: Start date in YYYY-MM-DD format
    - **expected_expenses**: Text block with expected expenses (MM/DD/YY - Vendor - $Price)

    Returns matched pairs, unmatched expected expenses, and unmatched actual expenses.
    """
    try:
        start_date_obj = datetime.strptime(request.start_date, "%Y-%m-%d")
        start_date_parser = start_date_obj.strftime("%m/%d/%Y")

        actual_items = parse_purchases(
            request.sheet_link,
            request.cardholder_name,
            start_date_parser
        )

        results = reconcile_expenses(
            request.expected_expenses,
            actual_items,
            price_tolerance=1.00,
            similarity_threshold=0.75
        )

        return ReconcileResponse(
            matched=[
                MatchedPair(
                    expected=ExpectedExpenseSchema.from_dataclass(exp),
                    actual=ReportItemSchema.from_dataclass(act)
                )
                for exp, act in results["matched"]
            ],
            unmatched_expected=[
                ExpectedExpenseSchema.from_dataclass(exp)
                for exp in results["unmatched_expected"]
            ],
            unmatched_actual=[
                ReportItemSchema.from_dataclass(act)
                for act in results["unmatched_actual"]
            ]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to access Google Sheets: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reconciliation failed: {str(e)}")
