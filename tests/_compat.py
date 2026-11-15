"""Single place that knows where things live. Update only this file when modules move."""
import backend.api as _api
from backend.api import app
from backend.core.dates import parse_date_flexible
from backend.core.expense_parser import parse_expected_expenses
from backend.core.reconcile import reconcile_expenses, vendor_similarity
from backend.core.models import ExpectedExpense, ReportItem
import backend.pdf_generator as pdf_module

RECONCILE_URL = "/reconcile"


def patch_parse_purchases(monkeypatch, fn):
    monkeypatch.setattr(_api, "parse_purchases", fn)
