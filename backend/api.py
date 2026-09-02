from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))

from parser import parse_purchases
from reconcile import reconcile_expenses
from backend.pdf_generator import generate_affidavit

from backend.models import (
    ReconcileRequest,
    ReconcileResponse,
    ExpectedExpenseSchema,
    ReportItemSchema,
    MatchedPair,
    AffidavitRequest
)

app = FastAPI(
    title="Expense Reconciliation API",
    description="API for reconciling expected expenses against actual expenses from Google Sheets",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.up\.railway\.app|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/reconcile", response_model=ReconcileResponse)
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


@app.post("/api/generate-affidavit")
async def generate_affidavit_endpoint(request: AffidavitRequest):
    """
    Generate affidavit PDF from expense data.

    - **vendor**: Vendor name from expected expense
    - **price**: Price from expected expense
    - **date**: Date in YYYY-MM-DD format
    - **cardholder_name**: Full cardholder name with role

    Returns PDF binary stream.
    """
    try:
        pdf_bytes = generate_affidavit(
            vendor=request.vendor,
            price=request.price,
            date=request.date,
            cardholder_name=request.cardholder_name
        )

        filename = f"affidavit_{request.vendor.replace(' ', '_')}_{request.date}.pdf"

        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Template file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Affidavit generation failed: {str(e)}")


frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
print(f"[startup] Looking for frontend at: {frontend_dist.resolve()}")
print(f"[startup] frontend/dist exists: {frontend_dist.is_dir()}")
if frontend_dist.is_dir():
    print(f"[startup] frontend/dist contents: {list(frontend_dist.iterdir())}")
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
else:
    parent = frontend_dist.parent
    print(f"[startup] frontend/ exists: {parent.is_dir()}")
    if parent.is_dir():
        print(f"[startup] frontend/ contents: {list(parent.iterdir())}")
