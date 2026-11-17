from datetime import date

import pytest
import requests

from tests._compat import ReportItem, RECONCILE_URL, patch_parse_purchases

EXPECTED_TEXT = """9/2 - $5 - Foo
2/30/26 - Bar - $3
9/2/2026 - Baz - $1,234,567.50
1/1/26 - Z - $0
1/1/26 - Q - $12abc
9/3/26 - $9 -
"""

REQ = {
    "cardholder_name": "Jane Doe",
    "start_date": "2026-09-01",
    "expected_expenses": "9/2/26 - Foo - $10",
    "sheet_link": "https://example.com/sheet",
}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_parse_expenses_returns_only_affidavit_valid_iso_rows(client):
    r = client.post("/api/parse-expenses", json={"expected_expenses": EXPECTED_TEXT})
    assert r.status_code == 200
    assert r.json() == [
        {"date": f"{date.today().year}-09-02", "vendor": "Foo", "price": 5.0},
        {"date": "2026-09-02", "vendor": "Baz", "price": 1234567.5},
    ]


def test_every_parsed_expense_generates_an_affidavit(client):
    """Regression: anything parse-expenses returns must never fail at generation."""
    parsed = client.post("/api/parse-expenses", json={"expected_expenses": EXPECTED_TEXT}).json()
    assert parsed
    for e in parsed:
        r = client.post("/api/generate-affidavit", json={**e, "cardholder_name": "Jane Doe, Treasurer"})
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content.startswith(b"%PDF")


@pytest.mark.parametrize("patch", [
    {"date": "20undefined-09-02"}, {"price": 0}, {"vendor": ""}, {"cardholder_name": ""},
])
def test_generate_affidavit_rejects_bad_input(client, patch):
    body = {"vendor": "Foo", "price": 5, "date": "2026-09-02", "cardholder_name": "Jane Doe", **patch}
    assert client.post("/api/generate-affidavit", json=body).status_code == 422


def test_reconcile_happy_path(client, monkeypatch):
    item = ReportItem(description="d", activity="a", date=date(2026, 9, 5), price=10.0,
                      vendor="Foo", receipts=[], flyer="")
    patch_parse_purchases(monkeypatch, lambda *a, **k: [item])
    r = client.post(RECONCILE_URL, json=REQ)
    assert r.status_code == 200
    body = r.json()
    assert len(body["matched"]) == 1
    assert body["unmatched_expected"] == [] and body["unmatched_actual"] == []


def test_reconcile_malformed_start_date_is_rejected_by_schema(client):
    r = client.post(RECONCILE_URL, json={**REQ, "start_date": "09/01/2026"})
    assert r.status_code == 422


def test_reconcile_value_error_is_400(client, monkeypatch):
    def boom(*a, **k):
        raise ValueError("bad")
    patch_parse_purchases(monkeypatch, boom)
    assert client.post(RECONCILE_URL, json=REQ).status_code == 400


def test_reconcile_network_error_is_502(client, monkeypatch):
    def boom(*a, **k):
        raise requests.exceptions.ConnectionError("down")
    patch_parse_purchases(monkeypatch, boom)
    assert client.post(RECONCILE_URL, json=REQ).status_code == 502


def test_reconcile_unexpected_error_is_500(client, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("x")
    patch_parse_purchases(monkeypatch, boom)
    assert client.post(RECONCILE_URL, json=REQ).status_code == 500
