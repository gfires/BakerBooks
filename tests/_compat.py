"""Single place that knows where things live. Update only this file when modules move."""
import backend.routes.reconcile as _reconcile_route
from backend.main import app
from backend.core.dates import parse_date_flexible
from backend.core.expense_parser import parse_expected_expenses
from backend.core.reconcile import reconcile_expenses, vendor_similarity
from backend.core.models import ExpectedExpense, ReportItem
import backend.pdf.generator as pdf_module

RECONCILE_URL = "/api/reconcile"


def patch_parse_purchases(monkeypatch, fn):
    monkeypatch.setattr(_reconcile_route, "parse_purchases", fn)
