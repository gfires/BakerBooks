"""Single place that knows where things live. Update only this file when modules move."""
import backend.api as _api
from backend.api import app
from parser import parse_date_flexible
from reconcile import parse_expected_expenses, reconcile_expenses, vendor_similarity
from models import ExpectedExpense, ReportItem
import backend.pdf_generator as pdf_module

RECONCILE_URL = "/reconcile"


def patch_parse_purchases(monkeypatch, fn):
    monkeypatch.setattr(_api, "parse_purchases", fn)
